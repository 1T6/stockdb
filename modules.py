from creon import *
import pandas as pd
import pymysql
import datetime
import logging





def make_min_db(codes):

    db_base = 'stockdb_min_'
    list = [1, 3, 5, 10, 15]

    for i in list:
        db_name = db_base+str(i)

        conn = pymysql.connect(host='localhost', user='root', password='1234', db=db_name, charset='utf8')
        curs = conn.cursor()

        for i, code in enumerate(codes):
            sql = 'create table `' + code + '` ( `일자` datetime primary key, `시가` int not null, ' \
                                            '`고가` int not null, `저가` int not null, ' \
                                            '`종가` int not null, `거래량` int not null,' \
                                            '`거래대금` int not null, `매도` int not null,' \
                                            '`매수` int not null);'
            curs.execute(sql)

        conn.commit()
        conn.close()
        print('{} DB 테이블 생성 완료'.format(db_name))

def collect_min_db(codes):

    chart = Cy_chart()

    db_base = 'stockdb_min_'
    list = [1,3,5,10,15]

    for i in list:
        db_name = db_base+str(i)

        conn = pymysql.connect(host='localhost', user='root', password='1234', db=db_name, charset='utf8')
        curs = conn.cursor()

        for code in codes:
            #db의 최근일 날짜를 가져온다.
            db_recent_date = get_recent_date_time(curs=curs, code=code, db_type='minute')

            data = chart.request_minute(code, length=i, request_num = 200000, db_recent_date= db_recent_date)


            #누적 체결을 그냥 체결로 바꾼다.
            data = remove_accumulation(data)

            for row in data:
                sql = 'insert ignore into `'+code+'` values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                curs.execute(sql, row)
            print('{}분봉 {}종목 저장 완료. {}/{}'.format(i, code, codes.index(code), len(codes)-1))



            conn.commit()
        conn.close()

'''
def collect_day_db(codes):

    conn = pymysql.connect(host='localhost', user='root', password='1234', db='stockdb_day', charset='utf8')
    curs = conn.cursor()

    for code in codes:
        db_recent_date = get_recent_date(curs, code)

'''

def update_min_db(code):
    pass


if __name__ =='__main__':

    code_mgr = Cy_code_manger()

    kospi_200 = code_mgr.get_kospi_200_codes()
    kosdaq_150 = code_mgr.get_kosdaq_150_codes()
    codes = kospi_200+ kosdaq_150

    #make_min_db(codes)
    collect_min_db(codes)


