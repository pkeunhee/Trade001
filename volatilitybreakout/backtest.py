import backtrader as bt
from datetime import date, datetime, time, timedelta
from db import dbconn


class VolatilityBreakout(bt.Strategy):
    def __init__(self):
        self.bought_today = False
        self.order = None

        self.sma1 = bt.indicators.SMA(self.datas[0].close, period=5)
        self.sma2 = bt.indicators.SMA(self.datas[0].close, period=10)

        print("init end")

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
            order_details = f"매매가격: {order.executed.price}, Cost: {order.executed.value}, 수수료: {order.executed.comm}, 매매수량: {order.executed.size}, 자산: {cerebro.broker.getvalue():,.0f}, SMA: {self.sma1[0]}"

            if order.isbuy():
                self.log(f"매수: {order_details}")
            else:  # Sell
                profit = (order.executed.price * abs(order.executed.size)) - order.executed.value
                self.log(f"매도: {order_details}, 수익: {profit}")

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def next(self):
        current_bar_datetime = self.data.num2date(self.data.datetime[0])  # 현재 데이터의 시간
        previous_bar_datetime = self.data.num2date(self.data.datetime[-1])  # 현재에서 바로 직전 데이터의 시간

        # 맨처음 데이터인 경우
        if current_bar_datetime.time() < previous_bar_datetime.time():
            self.bought_today = False
            return

        today_open = self.data.open[0]
        last_day_high = self.data.high[-1]
        last_day_low = self.data.low[-1]
        target_price = today_open + (last_day_high - last_day_low) * 0.5

        # 오프닝 시간 범위에서 가장 비싼 가격을 현재가가 돌파하는 시점이 되면 매수 한다.
        if self.data.close[0] >= target_price and not self.bought_today\
                and self.data.close[0] > self.sma1[0]\
                and self.data.close[0] > self.sma2[0]:
            self.order = self.buy()
            self.bought_today = True

        # 다음날 시가에 청산
        if self.position and current_bar_datetime.time() >= time(15, 35, 0):
            # self.log("RUNNING OUT OF TIME - LIQUIDATING POSITION")
            self.log("다음날 시가에 청산하자")
            self.close()  # 만약 시간을 종료 시간 (15:30:00) 으로 설정 했다면 당일에 매도 되지 않고 다음날 시초에 매도 된다.

    #def stop(self):
     #   self.log('(Num Opening Bars %2d) Ending Value %.2f' %
      #           (self.params.num_opening_bars, self.broker.getvalue()))


if __name__ == '__main__':
    start_date = '2023-05-21'
    end_date = '2023-08-25'
    code = '005930'

    mk = dbconn.MarketDB()
    df = mk.get_minute_stock_price(code, start_date, end_date)

    data = bt.feeds.PandasData(dataname=df)

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(1000000)
    # cerebro.broker.setcommission(commission=0.0014)  # ④
    # cerebro.addsizer(backtrader.sizers.PercentSizer, percents=95)
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)
    cerebro.adddata(data)
    cerebro.addstrategy(VolatilityBreakout)

    print(f'Initial Portfolio Value : {cerebro.broker.getvalue():,.0f} KRW')
    cerebro.run()
    print(f'Final Portfolio Value   : {cerebro.broker.getvalue():,.0f} KRW')
    cerebro.plot(style='candlestick')
