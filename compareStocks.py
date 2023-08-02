from pandas_datareader import data as pdr
import yfinance as yf
import matplotlib.pyplot as plt

# yfinance 패키지를 통해 야후 파이낸스에서 제공하는 삼성전자와 마이크로소프트 주식 시세를 데이터프레임으로 입력
yf.pdr_override()

# 삼성전자 데이터프레임에서 일간 변동률 누적합 추출
sec = pdr.get_data_yahoo('005930.KS', start='2020-01-01')
sec_dpc = (sec['Close'] / sec['Close'].shift(1) - 1) * 100
sec_dpc.iloc[0] = 0
sec_dpc_cs = sec_dpc.cumsum()

# 마이크로소프트 데이터프레임에서 일간 변동률 누적합 추출
msft = pdr.get_data_yahoo('MSFT', start='2020-01-01')
msft_dpc = (msft['Close'] / msft['Close'].shift(1) - 1) * 100
msft_dpc.iloc[0] = 0
msft_dpc_cs = msft_dpc.cumsum()

# matplotlib 패키지를 통해 주식 수익률 출력
plt.plot(sec.index, sec_dpc_cs, 'b', label='Samsung Electronics')
plt.plot(msft.index, msft_dpc_cs, 'r--', label='Microsoft')
plt.ylabel('Change %')
plt.grid(True)
plt.legend(loc='best')
plt.show()