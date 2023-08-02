from pandas_datareader import data as pdr
import yfinance as yf
import matplotlib.pyplot as plt

# yfinance 패키지를 통해 야후 파이낸스에서 제공하는 삼성전자와 마이크로소프트 주식 시세를 데이터프레임으로 입력
yf.pdr_override()

# 삼성전자 데이터프레임에서 일간 변동률 누적합 추출
sec = pdr.get_data_yahoo('005930.KS', start='2020-01-01')
sec_dpc = (sec['Close'] / sec['Close'].shift(1) - 1) * 100
sec_dpc.iloc[0] = 0

# matplotlib 패키지를 통해 주식 수익률 출력
plt.hist(sec_dpc, bins=18)
plt.grid(True)
plt.show()