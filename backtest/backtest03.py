import backtrader as bt
import backtrader.indicators as btind
from datetime import date, datetime, time, timedelta
from db import dbconn


class MyStrategy(bt.Strategy):
    params = dict(
        fast_ma_period=10,
        slow_ma_period=30,
        stop_loss=0.03,
        take_profit=0.07
    )

    def __init__(self):
        self.fast_ma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.fast_ma_period)
        self.slow_ma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.slow_ma_period)

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
        if self.position:
            if self.data.close[0] >= self.take_price or \
                    self.data.close[0] <= self.stop_price:
                self.sell()
            return
        else:
            if self.fast_ma[0] < self.slow_ma[0] and self.fast_ma[-1] > self.slow_ma[-1]:
                self.order = self.buy()
                self.stop_price = self.data.close[0] * (1.0 - self.params.stop_loss)
                self.take_price = self.data.close[0] * (1.0 + self.params.take_profit)


if __name__ == '__main__':
    start_date = '2022-01-02'
    end_date = '2023-08-04'
    codeList = ['005930', '000660', '035420', '035720', '207940']
    # codeList = ['005930']

    mk = dbconn.MarketDB()

    for code in codeList:
        df = mk.get_daily_stock_price(code, start_date, end_date, 'S')
        df = df.drop(['code', 'date', 'name'], axis=1)
        df.columns = ['close', 'open', 'high', 'low', 'volume']

        data = bt.feeds.PandasData(dataname=df)

        cerebro = bt.Cerebro()
        cerebro.broker.setcash(1000000)
        # cerebro.broker.setcommission(commission=0.0014)  # ④
        # cerebro.addsizer(bt.sizers.PercentSizer, percents=95)
        cerebro.addsizer(bt.sizers.FixedSize, stake=10)
        cerebro.adddata(data)
        cerebro.addstrategy(MyStrategy)

        startAmt = cerebro.broker.getvalue()
        print(f'Initial Portfolio Value : {cerebro.broker.getvalue():,.0f} KRW')

        cerebro.run()

        endAmt = cerebro.broker.getvalue()
        print(f'Final Portfolio Value   : {cerebro.broker.getvalue():,.0f} KRW')

        profit = (endAmt - startAmt) / startAmt * 100
        print(f'수익률 : {profit}% KRW')

        # cerebro.plot(style='candlestick')
