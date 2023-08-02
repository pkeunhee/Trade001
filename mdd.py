from pandas_datareader import data as pdr
import yfinance as yf
import matplotlib.pyplot as plt

# yfinance 패키지를 통해 야후 파이낸스에서 제공하는 KOSPI 지수 데이터 다운로드
yf.pdr_override()

kospi = pdr.get_data_yahoo('^KS11', '2004-01-04')

window = 252 # 산정 기간, 1년 동안의 개장일을 어림잡아 252일로 설정
peak = kospi['Adj Close'].rolling(window, min_periods=1).max() # 산정 기간 중 최고치
drawdown = kospi['Adj Close']/peak - 1.0 # 최고치 대비 하락률
max_dd = drawdown.rolling(window, min_periods=1).min() # 산정 기간 중 최저치

# matplotlib 패키지를 통해 MDD 출력
plt.figure(figsize=(9, 7))
plt.subplot(211)
kospi['Close'].plot(label='KOSPI', title='KOSPI MDD', grid=True, legend=True)
plt.subplot(212)
drawdown.plot(c='blue', label='KOSPI DD', grid=True, legend=True)
max_dd.plot(c='red', label='KOSPI MDD', grid=True, legend=True)
plt.show()