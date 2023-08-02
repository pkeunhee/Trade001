from pykiwoom.kiwoom import *
import time
import pandas as pd

# 로그인
kiwoom = Kiwoom()
kiwoom.CommConnect(block=True)

# TR 요청 (연속조회)
dfs = []
df = kiwoom.block_request("opt10081",
                          종목코드="005930",
                          기준일자="20230418",
                          수정주가구분=1,
                          output="주식일봉차트조회",
                          next=0)
print("head 출력 이전")
print(df.head())
print("head 출력 이후")

dfs.append(df)

print("시작")
idx = 1
while kiwoom.tr_remained:
    print("while 진입")
    print(idx)
    df = kiwoom.block_request("opt10081",
                              종목코드="005930",
                              기준일자="20230418",
                              수정주가구분=1,
                              output="주식일봉차트조회",
                              next=2)
    dfs.append(df)
    time.sleep(1)

    print(idx)
    idx += 1

print("종료")
df = pd.concat(dfs)
df.to_excel("005930.xlsx")