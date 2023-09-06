import pandas as pd
import pymysql


class MarketDB:
    def __init__(self):
        """생성자: MariaDB 연결 및 종목코드 딕셔너리 생성"""
        self.conn = pymysql.connect(host='www.ghp.pe.kr', user='pkeunhee', port=3306,
                                    password='', db='apt', charset='utf8')
        self.codes = {}
        # self.get_comp_info()

    def __del__(self):
        """소멸자: MariaDB 연결 해제"""
        self.conn.close()

    def get_all_stock_corp(self):
        sql = \
            f"SELECT code, `name` " \
            f"FROM stock_corp " \
            f"WHERE type = 'S' " \
            f"ORDER BY totAmt desc"
        df = pd.read_sql(sql, self.conn)
        df.index = df['code']
        return df

    def get_daily_stock_price(self, code, start_date=None, end_date=None, type=None):
        sql = \
            f"SELECT " \
            f"sp.code as code, " \
            f"sp.date as date, " \
            f"sc.name as `name`, " \
            f"sp.endPrice as endPrice, " \
            f"sp.startPrice as startPrice, " \
            f"sp.highPrice as highPrice, " \
            f"sp.lowPrice as lowPrice, " \
            f"sp.tradeCnt as tradeCnt " \
            f"FROM stock_date_point sp JOIN stock_corp sc " \
            f"WHERE sp.code = sc.code " \
            f"AND sp.code = '{code}'" \
            f"AND sc.type = '{type}' " \
            f"AND `date` BETWEEN '{start_date}' AND '{end_date}'"

        df = pd.read_sql(sql, self.conn)
        df.index = df['date']
        df.index = pd.to_datetime(df.index)
        return df

    def get_minute_stock_price(self, code, start_date=None, end_date=None):
        sql = \
            f"SELECT " \
            f"sp.code as code, " \
            f"sp.date as date, " \
            f"sp.close as close, " \
            f"sp.open as open, " \
            f"sp.high as high, " \
            f"sp.low as low, " \
            f"sp.volume as volume " \
            f"FROM stock_date_point2 sp " \
            f"WHERE sp.code = '{code}' " \
            f"AND `date` BETWEEN '{start_date}' AND '{end_date}'"

        df = pd.read_sql(sql, self.conn)
        df.index = df['date']
        df.index = pd.to_datetime(df.index)
        return df

    def get_daily_apt_price(self, loc1, loc2, loc3, name, type, startSize, endSize, start_date=None, end_date=None):
        sql = f"SELECT * FROM apt_transaction2 WHERE loc1 = '{loc1}'" \
              f" and loc2 = '{loc2}' and loc3 = '{loc3}' and name = '{name}' and type = '{type}' and size BETWEEN '{startSize}' AND '{endSize}' and date >= '{start_date}' and date <= '{end_date}' order by date"
        df = pd.read_sql(sql, self.conn)
        df.index = df['date']
        return df

    def insertStockDatePoint(self, code, date, price, tradeCnt):
        sql = f"INSERT IGNORE INTO stock_date_point" \
              f" (code, `date`, endPrice, tradeCnt, regDate)" \
              f" VALUES" \
              f" ('{code}', '{date}', '{price}', '{tradeCnt}', now())"

    def insertStockDatePoint2(self, code, date, open, high, low, close, tradeCnt):
        sql = f"INSERT IGNORE INTO stock_date_point" \
              f" (code, `date`, startPrice, highPrice, lowPrice, endPrice, tradeCnt, regDate)" \
              f" VALUES" \
              f" ('{code}', '{date}', '{open}', '{high}', '{low}', '{close}', '{tradeCnt}', now())"

        with self.conn.cursor() as curs:
            curs.execute(sql)
            self.conn.commit()
