import sys
from PyQt5.QtWidgets import *
import win32com.client
import pandas as pd
import os
import time
import datetime

g_objCodeMgr = win32com.client.Dispatch('CpUtil.CpCodeMgr')
g_objCpStatus = win32com.client.Dispatch('CpUtil.CpCybos')


class Cy_code_manger:
    def __init__(self):
        self.objCpCodeMgr = win32com.client.Dispatch("CpUtil.CpCodeMgr")

    def get_kospi_200_codes(self):
        codes = list(self.objCpCodeMgr.GetGroupCodeList(180))
        return codes

    def get_kosdaq_150_codes(self):
        #앞의 0 빼먹어진다.
        df = pd.read_excel('kosdaq150.xls', dtype = str)
        df = df.loc[:, '종목코드']
        codes = list(df)
        codes = list(map(lambda x : 'A'+x, codes))

        return codes

    def get_kospi_50_codes(self):
        codes = self.objCpCodeMgr.GetGroupCodeList(182)
        return codes

    def get_industry_list(self):
        list = self.objCpCodeMgr.GetIndustryList()

        return list




class Cy_chart:
    def __init__(self):
        self.objStockChart = win32com.client.Dispatch("CpSysDib.StockChart")

    def _check_rq_status(self):
        """
        self.objStockChart.BlockRequest() 로 요청한 후 이 메소드로 통신상태 검사해야함
        :return: None
        """
        rqStatus = self.objStockChart.GetDibStatus()
        rqRet = self.objStockChart.GetDibMsg1()
        if rqStatus == 0:
            pass
            # print("통신상태 정상[{}]{}".format(rqStatus, rqRet), end=' ')
        else:
            print("통신상태 오류[{}]{} 종료합니다..".format(rqStatus, rqRet))
            exit()

    def _check_connection_status(self):
        '''
        연결 여부를 체크.
        :return: None
        '''
        bConnect = g_objCpStatus.IsConnect
        if (bConnect == 0):
            print("PLUS가 정상적으로 연결되지 않음. ")
            return False

    def request_minute(self, code, chart_type, length, request_num):

        if code[0]!= 'A':
            code = 'A' + code

        received_data = []
        received_num = 0


        #연결 확인
        self._check_connection_status()

        self.objStockChart.SetInputValue(0, code)  # 종목코드
        self.objStockChart.SetInputValue(1, ord('2'))  # 개수로 받기
        self.objStockChart.SetInputValue(4, request_num)  # 조회 개수
        self.objStockChart.SetInputValue(5, [0, 1, 2, 3, 4, 5, 8])  # 요청항목 - 날짜, 시간,시가,고가,저가,종가,거래량
        self.objStockChart.SetInputValue(6, chart_type)  # '차트 주기 - 분/틱
        self.objStockChart.SetInputValue(7, length)  # 분틱차트 주기
        self.objStockChart.SetInputValue(9, ord('1'))  # 수정주가 사용

        while request_num >received_num:
            self.objStockChart.BlockRequest()
            #통신상태 확인
            self._check_rq_status()
            time.sleep(0.25)

            received_length = self.objStockChart.GetHeaderValue(3)  # 받아온 데이터 개수
            received_length = min(received_length, request_num-received_num)
            received_num = received_num + received_length

            for i in range(received_length):

                date = self.objStockChart.GetDataValue(0, i)
                minute = self.objStockChart.GetDataValue(1, i)
                open = self.objStockChart.GetDataValue(2, i)
                high = self.objStockChart.GetDataValue(3, i)
                low =self.objStockChart.GetDataValue(4, i)
                close = self.objStockChart.GetDataValue(5, i)
                volume = self.objStockChart.GetDataValue(6, i)


                if int(minute)<1000 :
                    date = str(date)+'0'+str(minute)+'00'

                else :
                    date = str(date)+str(minute)+'00'
                temp = [date,open,high,low, close, volume]



                received_data.append(temp)

            received_min_date = min(received_data)[0]

            db_recent_date = '0'
            # BREAK OPTIONS
            if self.objStockChart.Continue ==0:
                break

            elif (db_recent_date is not None)  and (received_min_date < db_recent_date) :
                break

        return received_data

    def request_day(self, code, length, request_num, curs):

        if code[0]!= 'A':
            code = 'A' + code

        received_data = []
        received_num = 0

        #현재 DB의 가장 최근 일자
        sql = 'select max(`일자`) from `'+code+'`'
        curs.execute(sql)
        db_recent_date = curs.fetchall()[0][0]
        db_recent_date = db_recent_date.strftime('%Y%m%d%H%M%S')

        #연결 확인
        self._check_connection_status()

        self.objStockChart.SetInputValue(0, code)  # 종목코드
        self.objStockChart.SetInputValue(1, ord('2'))  # 개수로 받기
        self.objStockChart.SetInputValue(4, request_num)  # 조회 개수
        self.objStockChart.SetInputValue(5, [0, 2, 3, 4, 5, 8, 9])  # 요청항목 - 날짜, 시가,고가,저가,종가,거래량
        self.objStockChart.SetInputValue(6, ord('D')) # '차트 주기 - 분/틱
        self.objStockChart.SetInputValue(7, length)  # 분틱차트 주기
        self.objStockChart.SetInputValue(9, ord('1'))  # 수정주가 사용

        while request_num >received_num:
            self.objStockChart.BlockRequest()
            #통신상태 확인
            self._check_rq_status()
            time.sleep(0.25)

            received_length = self.objStockChart.GetHeaderValue(3)  # 받아온 데이터 개수
            received_length = min(received_length, request_num-received_num)
            received_num = received_num + received_length

            for i in range(received_length):

                date = self.objStockChart.GetDataValue(0, i)
                minute = self.objStockChart.GetDataValue(1, i)
                open = self.objStockChart.GetDataValue(2, i)
                high = self.objStockChart.GetDataValue(3, i)
                low =self.objStockChart.GetDataValue(4, i)
                close = self.objStockChart.GetDataValue(5, i)
                volume = self.objStockChart.GetDataValue(6, i)


                if int(minute)<1000 :
                    date = str(date)+'0'+str(minute)+'00'

                else :
                    date = str(date)+str(minute)+'00'
                temp = [date,open,high,low, close, volume]



                received_data.append(temp)

            received_min_date = min(received_data)[0]

            # BREAK OPTIONS
            if self.objStockChart.Continue ==0:
                break

            elif (db_recent_date is not None)  and (received_min_date < db_recent_date) :
                break

        return received_data



if __name__ == '__main__':
    chart = Cy_chart()

    data = chart.request_minute('005930', ord('m'), length = 1, request_num =500)


    print(data)


