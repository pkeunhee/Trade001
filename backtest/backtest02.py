import backtrader as bt
import backtrader.indicators as btind
from datetime import date, datetime, time, timedelta
from db import dbconn


class MyStrategy(bt.Strategy):
    params = dict(
        period1 = 14,
        period2 = 20,
        devfactor = 2
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.b = None

        self.bb = bt.indicators.BollingerBands(self.data.close, period=self.params.period2, devfactor=self.params.devfactor)
        self.pb = (self.data.close - self.bb.bot) / (self.bb.top - self.bb.bot)

        tprice = (self.data.close + self.data.low + self.data.high) / 3.0
        mfraw = tprice * self.data.volume

        flowpos = bt.indicators.SumN(mfraw * (tprice > tprice(-1)), period=self.params.period1)
        flowneg = bt.indicators.SumN(mfraw * (tprice < tprice(-1)), period=self.params.period1)

        mfiratio = bt.indicators.DivByZero(flowpos, flowneg, zero=100.0)
        self.mfi = 100.0 - 100.0 / (1.0 + mfiratio)

        # self.sma = bt.indicators.SMA(self.datas[0].close, period=self.params.period)
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
            order_details = f"매매가격: {order.executed.price}, Cost: {order.executed.value}, 수수료: {order.executed.comm}, 매매수량: {order.executed.size}, 자산: {cerebro.broker.getvalue():,.0f}, %b: {self.pb[0]}, MFI: {self.mfi[0]}, buy price: {self.buyprice}"

            if order.isbuy():
                self.log(f"매수: {order_details}")
                self.buyprice = order.executed.price
            else:  # Sell
                profit = (order.executed.price * abs(order.executed.size)) - order.executed.value
                self.log(f"매도: {order_details}, 수익: {profit}")

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('OPERATION PROFIT, GROSS %.2f, net %.2f' % (trade.pnl, trade.pnlcomm))

    def next(self):
        if not self.position:
            if self.pb[0] > 0.8 and self.mfi >= 80:
                self.order = self.buy()
        else:
            pp = (self.data.close[0] - self.buyprice) / self.data.close[0] * 100
            if (self.pb[0] <= 0.2 and self.mfi < 20):
                self.order = self.sell()

if __name__ == '__main__':
    start_date = '2022-01-02'
    end_date = '2023-08-04'
    # codeList = ['005930', '000660', '035420', '035720', '207940']
    codeList = ['005930']

    mk = dbconn.MarketDB()

    for code in codeList:
        df = mk.get_daily_stock_price(code, start_date, end_date, 'S')
        df = df.drop(['code', 'date', 'name'], axis=1)
        df.columns = ['close', 'open', 'high', 'low', 'volume']

        data = bt.feeds.PandasData(dataname=df)

        cerebro = bt.Cerebro()
        cerebro.broker.setcash(1000000)
        # cerebro.broker.setcommission(commission=0.0014)  # ④
        cerebro.addsizer(bt.sizers.PercentSizer, percents=95)
        cerebro.adddata(data)
        cerebro.addstrategy(MyStrategy)

        startAmt = cerebro.broker.getvalue()
        print(f'Initial Portfolio Value : {cerebro.broker.getvalue():,.0f} KRW')

        cerebro.run()

        endAmt = cerebro.broker.getvalue()
        print(f'Final Portfolio Value   : {cerebro.broker.getvalue():,.0f} KRW')

        profit = (endAmt - startAmt) / startAmt * 100
        print(f'수익률 : {profit}% KRW')

        cerebro.plot(style='candlestick')
