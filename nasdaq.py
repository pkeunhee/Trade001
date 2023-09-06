import datetime

from pandas_datareader import data as pdr
import yfinance as yf
import matplotlib.pyplot as plt
import db.dbconn as dbconn

yf.pdr_override()
mk = dbconn.MarketDB()
data = pdr.get_data_yahoo('^NDX', start=datetime.datetime(2023,5,10), end=datetime.datetime(2023,9,4))
for idx, row in data.iterrows():
    date = idx.strftime('%Y-%m-%d')
    open = round(row['Open'], 2)
    high = round(row['High'], 2)
    low = round(row['Low'], 2)
    close = round(row['Adj Close'], 2)
    volume = round(row['Volume'], 2)
    print(f"{date} / {open}, {high}, '{low}', {close}, {volume}")
    mk.insertStockDatePoint2('NDX', date, open, high, low, close, volume)

plt.plot(data.index, data['Close'])
plt.grid(True)
plt.show()
