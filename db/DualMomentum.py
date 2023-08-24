import pandas as pd

import dbconn


class DualMomentum:
    def __init__(self, start_date, end_date):
        """생성자: KRX 종목코드(codes)를 구하기 위한 MarkgetDB 객체 생성"""

        self.mk = dbconn.MarketDB()
        stockCorpDf = self.mk.get_all_stock_corp()

        self.allMap = {}

        for code in stockCorpDf.index:
            corpDf = self.mk.get_daily_stock_price(code, start_date, end_date)
            self.allMap[code] = corpDf

        print("init completed")

    def get_rltv_momentum(self, start_date, end_date, stock_count):
        """특정 기간 동안 수익률이 제일 높았던 stock_count 개의 종목들 (상대 모멘텀)
            - start_date  : 상대 모멘텀을 구할 시작일자 ('2020-01-01')
            - end_date    : 상대 모멘텀을 구할 종료일자 ('2020-12-31')
            - stock_count : 상대 모멘텀을 구할 종목수
        """

        # KRX 종목별 수익률을 구해서 2차원 리스트 형태로 추가
        rows = []
        columns = ['code', 'name', 'old_price', 'new_price', 'returns']

        for key, value in self.allMap.items():
            if start_date not in value.index:
                print(f"해당 날짜 없음 {key} / startDate : {start_date}")
                continue

            if end_date not in value.index:
                print(f"해당 날짜 없음 {key} / endDate : {end_date}")
                continue

            r1 = value.loc[start_date]
            r2 = value.loc[end_date]

            code = r1['code']
            name = r1['name']
            old_price = r1['endPrice']
            new_price = r2['endPrice']
            returns = (new_price / old_price - 1) * 100
            rows.append([code, name, old_price, new_price, returns])

        # 상대 모멘텀 데이터프레임을 생성한 후 수익률순으로 출력
        df = pd.DataFrame(rows, columns=columns)
        df = df[['code', 'name', 'old_price', 'new_price', 'returns']]
        df = df.sort_values(by='returns', ascending=False)
        df = df.head(stock_count)  # 정렬된 rows 에서 상위 100 개만 남긴다
        df.index = pd.Index(range(stock_count))  # 정렬한 순서대로 0 ~ 100 식으로 인덱스 재생성
        print(df)
        print(f"\nRelative momentum ({start_date} ~ {end_date}) : " \
              f"{df['returns'].mean():.2f}% \n")
        return df

    def get_abs_momentum(self, rltv_momentum, start_date, end_date):
        """특정 기간 동안 상대 모멘텀에 투자했을 때의 평균 수익률 (절대 모멘텀)
            - rltv_momentum : get_rltv_momentum() 함수의 리턴값 (상대 모멘텀)
            - start_date    : 절대 모멘텀을 구할 매수일 ('2020-01-01')
            - end_date      : 절대 모멘텀을 구할 매도일 ('2020-12-31')
        """
        rows = []
        columns = ['code', 'name', 'old_price', 'new_price', 'returns']

        for code in rltv_momentum['code']:
            val1 = self.allMap[code]
            r1 = val1.loc[start_date]
            r2 = val1.loc[end_date]

            if start_date not in val1.index:
                print(f"해당 날짜 없음 {code} / startDate : {start_date}")
                continue

            if end_date not in val1.index:
                print(f"해당 날짜 없음 {code} / endDate : {end_date}")
                continue

            code = r1['code']
            name = r1['name']
            old_price = r1['endPrice']
            new_price = r2['endPrice']
            returns = (new_price / old_price - 1) * 100
            rows.append([code, name, old_price, new_price, returns])

        # 상대 모멘텀 데이터프레임을 생성한 후 수익률순으로 출력
        df = pd.DataFrame(rows, columns=columns)
        df = df[['code', 'name', 'old_price', 'new_price', 'returns']]
        df = df.sort_values(by='returns', ascending=False)
        print(df)
        print(f"\nAbasolute momentum ({start_date} ~ {end_date}) : " \
              f"{df['returns'].mean():.2f}%")
        return df

start_date = '2023-05-22'
end_date = '2023-08-23'

start_date2 = '2022-02-24'
end_date2 = '2023-08-23'

dm = DualMomentum(start_date, end_date2)
df = dm.get_rltv_momentum(start_date, end_date, 30)
# dm.get_abs_momentum(df, start_date2, end_date2)
