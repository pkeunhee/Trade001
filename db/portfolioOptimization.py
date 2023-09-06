import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import dbconn

mk = dbconn.MarketDB()

start_date = '2020-05-01'
end_date = '2023-04-01'

stocks = ['005930', '035420', '005380']

df = pd.DataFrame()

for s in stocks:
    df1 = mk.get_daily_stock_price(s, start_date, end_date, 'S')
    df[s] = df1['endPrice']


daily_ret = df.pct_change() # 일간 수익률 (변동률)
annual_ret = daily_ret.mean() * 252 # 연간 수익률
daily_cov = daily_ret.cov()  # 일간 수익률의 공분산
annual_cov = daily_cov * 252 # 연간 공분산

port_ret = []
port_risk = []
port_weights = []

# 몬테카를로 시뮬레이션. 각 종목에 대한 비중을 렌덤하게 생성하여 risk 와 returns 를 구해보자
for _ in range(20000):
    weights = np.random.random(len(stocks))
    weights /= np.sum(weights)

    returns = np.dot(weights, annual_ret)
    risk = np.sqrt(np.dot(weights.T, np.dot(annual_cov, weights)))

    port_ret.append(returns)
    port_risk.append(risk)
    port_weights.append(weights)

portfolio = {'Returns': port_ret, 'Risk': port_risk}
for i, s in enumerate(stocks):
    portfolio[s] = [weight[i] for weight in port_weights]
df = pd.DataFrame(portfolio)
df = df[['Returns', 'Risk'] + [s for s in stocks]]

df.plot.scatter(x='Risk', y='Returns', figsize=(8, 6), grid=True)
plt.title('Efficient Frontier')
plt.xlabel('Risk')
plt.ylabel('Expected Returns')
plt.show()


