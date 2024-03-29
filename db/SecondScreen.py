import pandas as pd
import matplotlib.pyplot as plt
import datetime
# from mpl_finance import candlestick_ohlc
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mdates
import dbconn

start_date = '2020-05-01'
end_date = '2023-04-01'

mk = dbconn.MarketDB()
df = mk.get_daily_stock_price('035420', start_date, end_date, 'S')

ema60 = df.endPrice.ewm(span=60).mean()
ema130 = df.endPrice.ewm(span=130).mean()
macd = ema60 - ema130
signal = macd.ewm(span=45).mean() 
macdhist = macd - signal

df = df.assign(ema130=ema130, ema60=ema60, macd=macd, signal=signal,
    macdhist=macdhist).dropna()
df['number'] = df.index.map(mdates.date2num)
ohlc = df[['number','startPrice','highPrice','lowPrice','endPrice']]

ndays_high = df.highPrice.rolling(window=14, min_periods=1).max()      # ①
ndays_low = df.lowPrice.rolling(window=14, min_periods=1).min()        # ②
fast_k = (df.endPrice - ndays_low) / (ndays_high - ndays_low) * 100  # ③
slow_d= fast_k.rolling(window=3).mean()                           # ④
df = df.assign(fast_k=fast_k, slow_d=slow_d).dropna()             # ⑤

plt.figure(figsize=(9, 7))
p1 = plt.subplot(2, 1, 1)
plt.title('Triple Screen Trading - Second Screen')
plt.grid(True)
candlestick_ohlc(p1, ohlc.values, width=.6, colorup='red', colordown='blue')
p1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.plot(df.number, df['ema130'], color='c', label='EMA130')
plt.legend(loc='best')
p1 = plt.subplot(2, 1, 2)
plt.grid(True)
p1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.plot(df.number, df['fast_k'], color='c', label='%K')
plt.plot(df.number, df['slow_d'], color='k', label='%D')
plt.yticks([0, 20, 80, 100]) # ⑥
plt.legend(loc='best')
plt.show()
