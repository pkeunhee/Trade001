import datetime

from pandas_datareader import data as pdr
import yfinance as yf
import matplotlib.pyplot as plt
import db.dbconn as dbconn

yf.pdr_override()
mk = dbconn.MarketDB()
data = pdr.get_data_yahoo('BTC-USD', start=datetime.datetime(2023,5,10), end=datetime.datetime(2023,8,14))
for idx, row in data.iterrows():
    date = idx.strftime('%Y-%m-%d')
    price = round(row['Adj Close'], 2)
    print(f"{date} / {price}")
    mk.insertStockDatePoint('BITCOIN_USD', date, price, 0)

plt.plot(data.index, data['Close'])
plt.grid(True)
plt.show()
