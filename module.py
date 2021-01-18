from creon import *
import pandas as pd
import pymysql
import datetime
import logging
from sqlalchemy import create_engine

def make_min_db(codes):
    '''
    분봉 테이블 생성한다
    '''
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

def make_day_db(codes):
    '''
    일봉 테이블 생성한다
    '''
    db_name = 'stockdb_day'

    conn = pymysql.connect(host='localhost', user='root', password='1234', db=db_name, charset='utf8')
    curs = conn.cursor()

    for i, code in enumerate(codes):
        sql = 'create table `' + code + '` ( `일자` date primary key, `시가` int not null, ' \
                                        '`고가` int not null, `저가` int not null, ' \
                                        '`종가` int not null, `거래량` int not null,' \
                                        '`거래대금` int not null, `매도` int not null,' \
                                        '`매수` int not null, `시총` int not null, `외인비율` float not null,' \
                                        ' `기관순매수` int not null, `기관누적` int not null,' \
                                        '`대비부호` int not null);'
        curs.execute(sql)

    conn.commit()
    conn.close()
    print('{} DB 테이블 생성 완료'.format(db_name))

def insert_db(data, conn, curs, code, db_name):



    if db_name[8:11] == 'day':
        for row in data:

            sql = 'insert ignore into `'+code+'` values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            curs.execute(sql, row)
        print('{} {} 저장 완료. '.format(db_name,  code))

        conn.commit()

    elif db_name[8:11] == 'min':
        for row in data:
            sql = 'insert ignore into `' + code + '` values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            curs.execute(sql, row)
        print('{} {} 저장 완료.'.format(db_name,  code))

        conn.commit()


def revise_database(day_data, conn, curs, db_recent_date, code, db_name):

    for event_index, row in enumerate(day_data):
        if row[-1] != 100:
            break

    revision_rate = float(day_data[event_index][-1])
    revision_date = str(day_data[event_index][0])

    #업데이트 없이 넘어감
    if revision_date<db_recent_date[0:8] or db_recent_date == '0':
        print('{} {} 주가 수정 불필요'.format(db_name, code))
        return

    #수정주가 반영해야한다.
    elif revision_date>= db_recent_date[0:8]:
        print('{} {} 수정주가 반영'.format(db_name, code))

        if db_name[8:11] =='day':

            # DATA FETCH
            sql = 'select * from `' + code+ '`;'
            curs.execute(sql)
            data = list(curs.fetchall())

            columns = ['일자','시가','고가','저가','종가','거래량','거래대금','매도','매수','시총',
                       '외인비율','기관순매수','기관누적','대비부호']
            df = pd.DataFrame(data, columns = columns)

            #수정주가 반영
            df[['시가','고가','저가','종가']] = revision_rate/100 * df[['시가','고가','저가','종가']]
            df[['거래량','매도','매수','기관순매수','기관누적']] = 100/revision_rate * df[['거래량','매도','매수','기관순매수','기관누적']]

            # timestamp자료형 변경
            df['일자'] = df['일자'].astype(str)

            #기존 데이터 삭제
            sql = 'delete from `'+code+ '`'
            curs.execute(sql)

            #삽입
            insert_db(data= df.values.tolist(), conn = conn, curs = curs, code = code, db_name= db_name)

        elif db_name[8:11] =='min':
            #DATA FETCH
            sql = 'select * from `'+code+'`;'
            curs.execute(sql)

            data = list(curs.fetchall())

            columns = ['일자', '시가', '고가', '저가', '종가', '거래량', '거래대금', '매도', '매수']
            df = pd.DataFrame(data, columns=columns)

            #수정주가 반영
            df[['시가','고가','저가','종가']] = revision_rate/100 * df[['시가','고가','저가','종가']]
            df[['거래량', '매도', '매수']] = 100/revision_rate * df[['거래량', '매도', '매수']]

            #timestamp자료형 변경
            df['일자'] = df['일자'].astype(str)

            #기존 데이터 삭제
            sql = 'delete from `'+code+'`'
            curs.execute(sql)

            #삽입
            insert_db(data= df.values.tolist(), conn = conn, curs = curs, code = code, db_name= db_name)


def get_recent_date_time(curs, code, db_type):

    # 현재 DB의 가장 최근 일자
    sql = 'select max(`일자`) from `' + code + '`'
    curs.execute(sql)
    db_recent_date = curs.fetchall()[0][0]

    if db_recent_date is None:
        return '0'

    if db_type =='minute':
        db_recent_date = db_recent_date.strftime('%Y%m%d%H%M%S')

    elif db_type =='day':
        db_recent_date = db_recent_date.strftime('%Y%m%d')

    return db_recent_date


if __name__ =='__main__':

    code_mgr = Cy_code_manger()

    kospi_200 = code_mgr.get_kospi_200_codes()
    kosdaq_150 = code_mgr.get_kosdaq_150_codes()
    codes = kospi_200+ kosdaq_150



