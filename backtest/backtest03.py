import backtrader as bt
import backtrader.indicators as btind
from datetime import date, datetime, time, timedelta

import pandas as pd

from db import dbconn


class Report:
    code = None
    name = None
    profit = 0

    def __init__(self, code, name, profit):
        self.code = code
        self.name = name
        self.profit = profit

class MyStrategy(bt.Strategy):
    params = dict(
        fast_ma_period=10,
        slow_ma_period=30,
        sma1_period=112,
        sma2_period=224,
        sma3_period=448,
        sma4_period=5,
        stop_loss=0.03,
        take_profit=0.05
    )

    def __init__(self):
        # self.fast_ma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.fast_ma_period)
        self.slow_ma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.slow_ma_period)
        self.sma1 = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.sma1_period)
        self.sma2 = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.sma2_period)
        # self.sma3 = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.sma3_period)
        self.sma4 = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.sma4_period)

        self.crossover = bt.indicators.CrossOver(self.sma4, self.sma1)

        self.order = None
        self.stop_price = None
        self.take_price = None

        print('init')

    def log(self, txt, dt=None):
        if dt is None:
            dt = self.datas[0].datetime.datetime()

        print('%s, %s' % (dt, txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        if order.status in [order.Completed]:
            order_details = f"매매가격: {order.executed.price}, Cost: {order.executed.value}, 수수료: {order.executed.comm}, 매매수량: {order.executed.size}, 자산: {cerebro.broker.getvalue():,.0f}"

            if order.isbuy():
                self.log(f"매수: {order_details}")
            else:  # Sell
                profit = (order.executed.price * abs(order.executed.size)) - order.executed.value
                self.log(f"매도: {order_details}, 수익: {profit}")

        elif order.status in [order.Canceled]:
            self.log('ORDER CANCELD')
        elif order.status in [order.Margin]:
            self.log('ORDER MARGIN')
        elif order.status in [order.Rejected]:
            self.log('ORDER REJECTED')

        self.order = None

    def notify_trade(self, trade):
        print('notify_trade')

        if not trade.isclosed:
            return
        self.log('OPERATION PROFIT, GROSS %.2f, net %.2f' % (trade.pnl, trade.pnlcomm))

    def next(self):
        # 매도
        if self.position:
            if self.data.close[0] >= self.take_price or \
                    self.data.close[0] <= self.stop_price:
                self.sell()
            return
        # 매수
        else:
            # if self.fast_ma[0] < self.slow_ma[0] and self.fast_ma[-1] > self.slow_ma[-1]:
            # 역배열 상황인지 확인
            rev_array = self.sma2[0] > self.sma1[0] and self.sma1[0] > self.slow_ma[0]
            if self.crossover > 0 and rev_array:
                self.order = self.buy()
                self.stop_price = self.data.close[0] * (1.0 - self.params.stop_loss)
                self.take_price = self.data.close[0] * (1.0 + self.params.take_profit)


def summary(rtnSumm):
    winCnt = 0
    loseCnt = 0
    winPer = 0
    losePer = 0

    for key, value in rtnSumm.items():
        print(f'수익률 : {value.name} / {value.code}: {value.profit:,.0f}% KRW')
        if value.profit > 0:
            winCnt = winCnt + 1
            winPer = winPer + 1
        else:
            loseCnt = loseCnt + 1
            losePer = losePer + 1

    print(f'이긴 게임수: {winCnt}, 수익률합: {winPer}, 진 게임수: {loseCnt}, 손실 수익률합: {losePer}')



if __name__ == '__main__':
    start_date = '2020-01-02'
    end_date = '2023-08-31'
    test = False
    corpList = None

    mk = dbconn.MarketDB()
    if test:
        corpList = [
            ['005930', '삼성전자']
        ]

        # corpList = [
        #     ['005930', '삼성전자'],
        #     ['000660', 'SK하이닉스'],
        #     ['035420', 'NAVER'],
        #     ['035720', '카카오'],
        #     ['207940', '삼성바이오로직스']
        # ]

        corpList = pd.DataFrame(corpList, columns=['code', 'name'])
    else:
        corpList = mk.get_all_stock_corp()

    rtnSumm = {}

    for idx, row in corpList.iterrows():
        code = row['code']
        name = row['name']

        df = mk.get_daily_stock_price(code, start_date, end_date, 'S')
        df = df.drop(['code', 'date', 'name'], axis=1)
        df.columns = ['close', 'open', 'high', 'low', 'volume']

        data = bt.feeds.PandasData(dataname=df)

        cerebro = bt.Cerebro()
        cerebro.broker.setcash(10000000)
        cerebro.broker.setcommission(commission=0.0014)  # ④
        cerebro.addsizer(bt.sizers.PercentSizer, percents=95)
        # cerebro.addsizer(bt.sizers.FixedSize, stake=10)
        cerebro.adddata(data)
        cerebro.addstrategy(MyStrategy)

        startAmt = cerebro.broker.getvalue()
        print(f'Initial Portfolio Value : {cerebro.broker.getvalue():,.0f} KRW')

        cerebro.run()

        endAmt = cerebro.broker.getvalue()
        print(f'Final Portfolio Value   : {cerebro.broker.getvalue():,.0f} KRW')

        profit = (endAmt - startAmt) / startAmt * 100
        print(f'수익률 : {name} / {code}: {profit}% KRW')
        print('--------------------------------------------------------------------------------------------------------------')

        rtnSumm[code] = Report(code, name, profit)


        # cerebro.plot(style='candlestick')

    summary(rtnSumm)


