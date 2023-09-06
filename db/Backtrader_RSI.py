import backtrader as bt
import dbconn
import backtrader as bt

import dbconn

class MyStrategy(bt.Strategy):  # ①
    def __init__(self):
        self.rsi = bt.indicators.RSI(self.data.close)  # ②
    def next(self):  # ③
        if not self.position:
            if self.rsi < 30:
                self.order = self.buy()
        else:
            if self.rsi > 70:
                self.order = self.sell()

code = '005930'
start_date = '2022-01-03'
end_date = '2023-08-18'

mk = dbconn.MarketDB()
corpDf = mk.get_daily_stock_price(code, start_date, end_date, 'S')
corpDf2 = corpDf.drop(['code', 'date', 'name'], axis=1)
corpDf2.columns = ['close', 'open', 'high', 'low', 'volume']

cerebro = bt.Cerebro()  # ④
cerebro.addstrategy(MyStrategy)
data = bt.feeds.PandasData(dataname=corpDf2)
cerebro.adddata(data)
cerebro.broker.setcash(10000000)  # ⑥
cerebro.addsizer(bt.sizers.SizerFix, stake=30)  # ⑦

print(f'Initial Portfolio Value : {cerebro.broker.getvalue():,.0f} KRW')
cerebro.run()  # ⑧
print(f'Final Portfolio Value   : {cerebro.broker.getvalue():,.0f} KRW')
cerebro.plot()  # ⑨