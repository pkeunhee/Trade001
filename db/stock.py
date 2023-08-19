import pandas as pd
import matplotlib.pyplot as plt
import dbconn

start_date = '2010-05-01'
end_date = '2023-06-21'

mk = dbconn.MarketDB()
df_stock = mk.get_daily_stock_price('005930', start_date, end_date)
df_apt = mk.get_daily_apt_price(loc1 = '서울특별시', loc2 = '송파구', loc3 = '잠실동', name = '잠실엘스', type='매매', startSize=80, endSize=85, start_date=start_date, end_date=end_date)
df_apt = df_apt['price'].groupby(level=0).agg(['mean']) # 하루에 여러건 거래가 있는 경우 평균값 구함

stock_index = df_stock['endPrice'] / df_stock.iloc[0]['endPrice'] * 100
apt_index = df_apt['mean'] / df_apt.iloc[0][0] * 100

df = pd.DataFrame({'stock': stock_index, 'apt': apt_index})
df = df.fillna(method='bfill')
df = df.fillna(method='ffill')
print(df.corr())

plt.figure(figsize=(9, 5))
plt.plot(stock_index.index, stock_index, 'r--', label='stock')
plt.plot(apt_index.index, apt_index, 'b', label='apt')
plt.grid(True)
plt.legend(loc='best')
plt.show()
