import datetime

import dateutil.utils
from pykiwoom.kiwoom import *

# 로그인
kiwoom = Kiwoom()
kiwoom.CommConnect()

# 전종목 종목코드
codes = ['005930']

# 문자열로 오늘 날짜 얻기
now = datetime.datetime.now()
#today = now.strftime("%Y%m%d")
#yesterday = (dateutil.utils.today() - datetime.timedelta(1)).strftime("%Y%m%d")

today = (dateutil.utils.today() - datetime.timedelta(1)).strftime("%Y%m%d")
yesterday = (dateutil.utils.today() - datetime.timedelta(2)).strftime("%Y%m%d")


# 전 종목의 일봉 데이터
for i, code in enumerate(codes):
    print(f"{i}/{len(codes)} {code}")
    priceDf = kiwoom.block_request("opt10081",
                                   종목코드=code,
                                   기준일자=today,
                                   수정주가구분=1,
                                   output="주식일봉차트조회",
                                   next=0)

    currentInfo = kiwoom.block_request("opt10001",
                              종목코드=code,
                              output="주식기본정보",
                              next=0)

    priceDf.index = priceDf['일자']
    yesterdayOhlc = priceDf.loc[yesterday]
    todayOhlc = priceDf.loc[today]

    todayStart = int(todayOhlc['시가'])
    yesterdayHigh = int(yesterdayOhlc['고가'])
    yesterdayLow = int(yesterdayOhlc['저가'])
    currentPrice = abs(int(currentInfo['현재가'][0]))

    targetPrice = todayStart + (yesterdayHigh - yesterdayLow) * 0.5

    if(targetPrice >= currentPrice and targetPrice - currentPrice < 500):
        print(f"매수 타이밍 targetPrice: {targetPrice} / currentPrice: {currentPrice}")

    # time.sleep(3.6)