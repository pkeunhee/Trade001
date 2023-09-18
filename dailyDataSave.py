from datetime import date, datetime, timedelta

import yfinance as yf
from pandas_datareader import data as pdr

import db.dbconn as dbconn

yf.pdr_override()
mk = dbconn.MarketDB()

corpDict = {
    '^NDX': 'NDX',
    'BTC-USD': 'BITCOIN_USD',
    '^TNX': 'TNX'
}

startDate = datetime.combine(date.today() - timedelta(14), datetime.min.time())
endDate = datetime.combine(date.today() - timedelta(1), datetime.min.time())

for yjCode, dbCode in corpDict.items():
    data = pdr.get_data_yahoo(yjCode, start=startDate, end=endDate)
    for idx, row in data.iterrows():
        date = idx.strftime('%Y-%m-%d')
        open = round(row['Open'], 2)
        high = round(row['High'], 2)
        low = round(row['Low'], 2)
        close = round(row['Adj Close'], 2)
        volume = round(row['Volume'], 2)
        print(f"{date} / {yjCode} / {dbCode} / {open}, {high}, '{low}', {close}, {volume}")
        mk.insertStockDatePoint2(dbCode, date, open, high, low, close, volume)
