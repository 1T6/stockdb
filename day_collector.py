from creon import *
import pandas as pd
import pymysql
from module import *


def collect_day_db(codes):
    #테이블 생성
    make_day_db(codes)

    chart = Cy_chart()


    for code in codes:
        conn = pymysql.connect(host='localhost', user='root', password='1234', db='stockdb_day', charset='utf8')
        curs = conn.cursor()

        #데이터 받아오기
        day_data = chart.request_day(code, request_num = 2000000, db_recent_date='0')

        #수정주가 제외
        insert_data = []
        for row in day_data:
            insert_data.append(row[0:-1])

        #삽입
        insert_db(data = insert_data, conn=conn, curs= curs, code = code, db_name = 'stockdb_day')

        print('{} {}/{}'.format(code, code.index(code), len(code)-1))

if __name__ =='__main__':
    code_mgr = Cy_code_manger()

    kospi_200 = code_mgr.get_kospi_200_codes()
    kosdaq_150 = code_mgr.get_kosdaq_150_codes()
    codes = kospi_200 + kosdaq_150

    collect_day_db(codes)