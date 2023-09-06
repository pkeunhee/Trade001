import backtrader as bt
import backtrader.indicators as btind
from datetime import date, datetime, time, timedelta
from db import dbconn


class MyStrategy(bt.Strategy):
    params = dict(
        period = 20
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.buyprice = None
        self.buycomm = None

        self.sma = bt.indicators.SMA(self.datas[0].close, period=self.params.period)
        print('init')

    def log(self, txt, dt=None):
        if dt is None:
            dt = self.datas[0].datetime.datetime()

        print('%s, %s' % (dt, txt))

    def notify_order(self, order):
        self.log('notify_order')

        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            self.log(
                'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' % (
                order.executed.price, order.executed.value, order.executed.comm))
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
            self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('OPERATION PROFIT, GROSS %.2f, net %.2f' % (trade.pnl, trade.pnlcomm))

    def next(self):
        # self.log('Close, %.2f' % self.dataclose[0])

        if self.order:
            return

        if not self.position:
            if self.dataclose[0] > self.sma[0]:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])

            self.order = self.buy()
        else:
            if self.dataclose[0] < self.sma[0]:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
            self.order = self.sell()


if __name__ == '__main__':
    start_date = '2023-01-01'
    end_date = '2023-08-25'

    mk = dbconn.MarketDB()
    df = mk.get_daily_stock_price('005930', start_date, end_date, 'S')
    df = df.drop(['code', 'date', 'name'], axis=1)
    df.columns = ['close', 'open', 'high', 'low', 'volume']

    data = bt.feeds.PandasData(dataname=df)

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(1000000)
    # cerebro.broker.setcommission(commission=0.0014)  # ④
    cerebro.addsizer(bt.sizers.PercentSizer, percents=95)
    cerebro.adddata(data)
    cerebro.addstrategy(MyStrategy)

    # strats = cerebro.optstrategy(OpeningRangeBreakout, num_opening_bars=[15, 30, 60])

    startAmt = cerebro.broker.getvalue()

    print(f'Initial Portfolio Value : {startAmt:,.0f} KRW')
    cerebro.run()

    endAmt = cerebro.broker.getvalue()
    print(f'Final Portfolio Value   : {endAmt:,.0f} KRW')

    profit = (endAmt - startAmt) / startAmt * 100
    print(f'수익률 : {profit}% KRW')

    cerebro.plot(style='candlestick')
