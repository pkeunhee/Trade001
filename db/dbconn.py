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

    def get_daily_stock_price(self, code, start_date=None, end_date=None):
        sql = f"SELECT * FROM stock_date_point WHERE code = '{code}'"\
            f" and date >= '{start_date}' and date <= '{end_date}'"
        df = pd.read_sql(sql, self.conn)
        df.index = df['date']
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

        with self.conn.cursor() as curs:
            curs.execute(sql)
            self.conn.commit()




        
