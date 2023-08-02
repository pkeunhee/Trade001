import pandas as pd
from pandas_datareader import data as pdr
import yfinance as yf
from scipy import stats
import matplotlib.pyplot as plt

# yfinance 패키지를 통해 야후 파이낸스에서 제공하는 다우존스 지수와 코스피 지수 데이터 다운로드
yf.pdr_override()

dow = pdr.get_data_yahoo('^DJI', '2000-01-04')
kospi = pdr.get_data_yahoo('^KS11', '2000-01-04')

# 두 지수의 종가 칼럼으로 데이터프레임을 생성한 후 NaN 제거
df = pd.DataFrame({'X': dow['Close'], 'Y': kospi['Close']})
df = df.fillna(method='bfill')
df = df.fillna(method='ffill')

# scipy 패키지를 통해 다우존스 지수 X에서 코스피 지수 Y로의 선형회귀 모델 객체 생성
regr = stats.linregress(df.X, df.Y)
regr_line = f'Y = {regr.slope:.2f} * X + {regr.intercept:.2f}'

# 회귀 분석 모델 시각화
plt.figure(figsize=(7, 7))
plt.plot(df.X, df.Y, '.') # 산점도 출력
plt.plot(df.X, regr.slope * df.X + regr.intercept, 'r') # 회귀선 출력
plt.legend(['DOW x KOSPI', regr_line])
plt.title(f'DOW x KOSPI (R = {regr.rvalue:.2f})')
plt.xlabel('Dow Jones Industrial Average')
plt.ylabel('KOSPI')
plt.show()