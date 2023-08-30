import backtrader, pandas
from datetime import date, datetime, time, timedelta
from db import dbconn


class OpeningRangeBreakout(backtrader.Strategy):
    params = dict(
        num_opening_bars = 15 # 오프닝 끝이 되는 분
    )

    def __init__(self):
        self.opening_range_low = 0
        self.opening_range_high = 0
        self.opening_high_low_range = 0
        self.bought_today = False
        self.order = None

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
            order_details = f"매매가격: {order.executed.price}, Cost: {order.executed.value}, 수수료: {order.executed.comm}, 매매수량: {order.executed.size:,.0f}, 자산: {cerebro.broker.getvalue():,.0f}"

            if order.isbuy():
                self.log(f"매수: {order_details}")
            else:  # Sell
                self.log(f"매도: {order_details}")

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def next(self):
        current_bar_datetime = self.data.num2date(self.data.datetime[0]) # 현재 데이터의 시간
        previous_bar_datetime = self.data.num2date(self.data.datetime[-1]) # 현재에서 바로 직전 데이터의 시간

        # 두 데이터의 날짜부분이 다른 경우 현재 가격 사용하며 시작. 개장 시점인 경우는 현재 날짜와 이전날짜가 다른 상황이다.
        if current_bar_datetime.date() != previous_bar_datetime.date():
            self.opening_range_low = self.data.low[0]
            self.opening_range_high = self.data.high[0]
            self.bought_today = False

        opening_range_start_time = time(9, 0, 0) # 주식시장 개장 시간
        dt = datetime.combine(date.today(), opening_range_start_time) + timedelta(minutes=self.p.num_opening_bars)
        opening_range_end_time = dt.time() # 오프닝 기준 시간 구하기

        # 현재의 시간이 주식 개장 이후이고 오프닝 기준 시간 범위내인 경우 매매에 참여하진 않고 최대 high, 최소 low, range 구함
        if current_bar_datetime.time() >= opening_range_start_time \
                and current_bar_datetime.time() < opening_range_end_time:
            self.opening_range_high = max(self.data.high[0], self.opening_range_high)
            self.opening_range_low = min(self.data.low[0], self.opening_range_low)
            self.opening_high_low_range = self.opening_range_high - self.opening_range_low # 고가와 저가 차액 계산
        else:
            if self.order:
                return

            # 현재가가 (오프닝 고점 + 오프닝갭) 보다 높은 시점이면 매도하여 익절
            if self.position and (self.data.close[0] > (self.opening_range_high + self.opening_high_low_range)):
                self.close()

            # 오프닝 시간 범위에서 가장 비싼 가격을 현재가가 돌파하는 시점이 되면 매수 한다.
            if self.data.close[0] > self.opening_range_high and not self.position and not self.bought_today:
                self.order = self.buy()
                self.bought_today = True

            # 현재가가 (오프닝 고점 - 오프닝갭) 이하가 되면 매도하여 MDD 최소화
            if self.position and (self.data.close[0] < (self.opening_range_high - self.opening_high_low_range)):
                self.order = self.close()

            # 매수한게 있는데 시장 닫는 시간이 된 경우. 종가에 그냥 청산한다.
            if self.position and current_bar_datetime.time() >= time(15, 19, 0):
                # self.log("RUNNING OUT OF TIME - LIQUIDATING POSITION")
                self.log("종가에 청산 한다.")
                self.close() # 만약 시간을 종료 시간 (15:30:00) 으로 설정 했다면 당일에 매도 되지 않고 다음날 시초에 매도 된다.

    def stop(self):
        self.log('(Num Opening Bars %2d) Ending Value %.2f' %
                 (self.params.num_opening_bars, self.broker.getvalue()))

        # if self.broker.getvalue() > 130000:
        #     self.log("*** BIG WINNER ***")
        #
        # if self.broker.getvalue() < 70000:
        #     self.log("*** MAJOR LOSER ***")


if __name__ == '__main__':

    start_date = '2022-08-21'
    end_date = '2023-08-25'

    mk = dbconn.MarketDB()
    df = mk.get_minute_stock_price('005930', start_date, end_date)

    data = backtrader.feeds.PandasData(dataname=df)

    cerebro = backtrader.Cerebro()
    cerebro.broker.setcash(1000000)
    # cerebro.broker.setcommission(commission=0.0014)  # ④
    cerebro.addsizer(backtrader.sizers.PercentSizer, percents=95)
    cerebro.adddata(data)
    cerebro.addstrategy(OpeningRangeBreakout)

    # strats = cerebro.optstrategy(OpeningRangeBreakout, num_opening_bars=[15, 30, 60])

    print(f'Initial Portfolio Value : {cerebro.broker.getvalue():,.0f} KRW')
    cerebro.run()
    print(f'Final Portfolio Value   : {cerebro.broker.getvalue():,.0f} KRW')
    cerebro.plot(style='candlestick')
