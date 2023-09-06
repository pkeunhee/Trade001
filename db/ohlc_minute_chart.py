import pandas as pd

import matplotlib.pyplot as plt
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mdates

import dbconn

start_date = '2022-08-01'
end_date = '2023-09-03'

mk = dbconn.MarketDB()
df = mk.get_minute_stock_price('005930', start_date, end_date)

df['number'] = df.index.map(mdates.date2num)
ohlc = df[['number', 'open', 'high', 'low', 'close']]

p1 = plt.subplot(2, 1, 1)
candlestick_ohlc(p1, ohlc.values, width=.6, colorup='red', colordown='blue')

p1.xaxis_date()
p1.xaxis.set_major_formatter(mdates.DateFormatter('%y-%m-%d %H:%M:%S'))

plt.xticks(rotation=45)
plt.ylabel('Stock Price')
plt.xlabel('Date Hours:Minutes')
plt.show()