from creon import *
import pandas as pd
import pymysql
import datetime
from module import *

def db_update(codes, initial):

    #처음이면 테이블 부터 생성한다.
    if initial == True:
        make_day_db(codes)
        make_min_db(codes)

    min_list = [1, 3, 5, 10, 15]
    db_base = 'stockdb_min_'
    chart = Cy_chart()

    for code in codes:
        ##########################일봉 데이터#############################

        conn = pymysql.connect(host='localhost', user='root', password='1234', db='stockdb_day', charset='utf8')
        curs = conn.cursor()

        db_recent_date = get_recent_date_time(curs, code, db_type = 'day')

        # data를 받고
        day_data = chart.request_day(code, request_num = 2000000, db_recent_date=db_recent_date)

        # 수정주가 반영한다.
        revise_database(day_data, conn, curs, db_recent_date, code,  db_name = 'stockdb_day')

        #수정주가 제외
        insert_data = []
        for row in day_data:
            insert_data.append(row[0:-1])

        # 삽입
        insert_db(data = insert_data , conn = conn, curs = curs, code = code, db_name = 'stockdb_day')

        conn.close()

        ############################# 분봉 데이터 #####################################
        for i in min_list:

            db_name = db_base + str(i)

            conn = pymysql.connect(host='localhost', user='root', password='1234', db=db_name, charset='utf8')
            curs = conn.cursor()

            # data를 받고
            db_recent_date = get_recent_date_time(curs = curs, code =  code, db_type = 'minute')

            # 수정주가 반영한다.
            revise_database(day_data, conn, curs, db_recent_date, code, db_name = db_name)

            # data 받기
            min_data = chart.request_minute(code, length = i, request_num = 200000, db_recent_date = db_recent_date)

            # 삽입
            insert_db(data = min_data, conn = conn,curs =  curs, code = code, db_name =db_name)

            conn.close()

        print('{} 완료. {}/{}'.format(code, codes.index(code), len(codes)-1))

if __name__ =='__main__':

    code_mgr = Cy_code_manger()

    kospi_200 = code_mgr.get_kospi_200_codes()
    kosdaq_150 = code_mgr.get_kosdaq_150_codes()
    codes = kospi_200+ kosdaq_150

    db_update(codes, initial = False)


