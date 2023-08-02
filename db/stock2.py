import matplotlib.pyplot as plt

import dbconn

start_date = '2020-05-01'
end_date = '2023-04-01'

mk = dbconn.MarketDB()
new_gs = mk.get_daily_stock_price('005930', start_date, end_date)

# Moving average
ma5 = new_gs['price'].rolling(window=5).mean()
ma20 = new_gs['price'].rolling(window=20).mean()
ma60 = new_gs['price'].rolling(window=60).mean()
ma120 = new_gs['price'].rolling(window=120).mean()

# Insert columns
new_gs.insert(len(new_gs.columns), "MA5", ma5)
new_gs.insert(len(new_gs.columns), "MA20", ma20)
new_gs.insert(len(new_gs.columns), "MA60", ma60)
new_gs.insert(len(new_gs.columns), "MA120", ma120)

# Plot
plt.plot(new_gs.index, new_gs['price'], label='price')
plt.plot(new_gs.index, new_gs['MA5'], label='MA5')
plt.plot(new_gs.index, new_gs['MA20'], label='MA20')
plt.plot(new_gs.index, new_gs['MA60'], label='MA60')
plt.plot(new_gs.index, new_gs['MA120'], label='MA120')

plt.legend(loc="best")
plt.grid()
plt.show()