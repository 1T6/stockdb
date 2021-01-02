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

    def request_minute(self, code,  length, request_num, db_recent_date):

        if code[0]!= 'A':
            code = 'A' + code

        received_data = []
        received_num = 0

        #연결 확인
        self._check_connection_status()

        self.objStockChart.SetInputValue(0, code)  # 종목코드
        self.objStockChart.SetInputValue(1, ord('2'))  # 개수로 받기
        self.objStockChart.SetInputValue(4, request_num)  # 조회 개수
        self.objStockChart.SetInputValue(5, [0,     #날짜
                                             1,     #시간
                                             2,     #시가
                                             3,     #고가
                                             4,     #저가
                                             5,     #종가
                                             8,     #거래량
                                             9,     #거래대금
                                             10,    #누적매도
                                             11])  # 누적매수
        self.objStockChart.SetInputValue(6, ord('m'))  # '차트 주기 - 분/틱
        self.objStockChart.SetInputValue(7, length)  # 분틱차트 주기
        self.objStockChart.SetInputValue(9, ord('1'))  # 수정주가 사용

        while request_num >received_num:
            self.objStockChart.BlockRequest()
            #통신상태 확인
            self._check_rq_status()
            time.sleep(0.26)

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
                trading_value = int(self.objStockChart.GetDataValue(7, i)/1000)
                acu_sell = self.objStockChart.GetDataValue(8, i)
                acu_buy = self.objStockChart.GetDataValue(9, i)


                if int(minute)<1000 :
                    date = str(date)+'0'+str(minute)+'00'

                else :
                    date = str(date)+str(minute)+'00'

                temp = [date, open, high, low, close, volume, trading_value, acu_sell, acu_buy]



                received_data.append(temp)

            received_min_date = min(received_data)[0]

            # BREAK OPTIONS
            if self.objStockChart.Continue ==0:
                break

            elif (db_recent_date is not None)  and (received_min_date < str(db_recent_date)) :
                break

        return received_data

    def request_day(self, code, request_num, db_recent_date):

        if code[0] != 'A':
            code = 'A' + code

        received_data = []
        received_num = 0

        # 연결 확인
        self._check_connection_status()

        self.objStockChart.SetInputValue(0, code)  # 종목코드
        self.objStockChart.SetInputValue(1, ord('2'))  # 개수로 받기
        self.objStockChart.SetInputValue(4, request_num)  # 조회 개수
        self.objStockChart.SetInputValue(5,
                                         [0,        #일자
                                          2,        #시가
                                          3,        #고가
                                          4,        #저가
                                          5,        #종가
                                          8,        #거래량
                                          9,        #거래대금
                                          10,       #매도
                                          11,       #매수
                                          13,       #시총
                                          17,       #외국인 비율
                                          19,       #수정주가 비율
                                          20,       #기관 순매수
                                          21,       #기관 누적
                                          37])      #대비부호
        # 요청항목 - 날짜, 시간,시가,고가,저가,종가,거래량
        self.objStockChart.SetInputValue(6, ord('D'))  # '차트 주기 - 분/틱
        self.objStockChart.SetInputValue(9, ord('1'))  # 수정주가 사용

        while request_num > received_num:
            self.objStockChart.BlockRequest()
            # 통신상태 확인
            self._check_rq_status()
            time.sleep(0.25)

            received_length = self.objStockChart.GetHeaderValue(3)  # 받아온 데이터 개수
            received_length = min(received_length, request_num - received_num)
            received_num = received_num + received_length

            for i in range(received_length):

                temp = []

                for j in range(15):
                    #수정주가는 배열 맨 마지막에 붙인다.
                    if j == 11:
                        revision_rate = self.objStockChart.GetDataValue(j, i)

                    #거래대금 시가총액 억단위로 바꾼다.
                    elif j==6 or j==9:
                        temp.append(int(self.objStockChart.GetDataValue(j,i)/100000000))
                    else:
                        temp.append(self.objStockChart.GetDataValue(j, i))

                temp.append(revision_rate)
                received_data.append(temp)

            received_min_date = min(received_data)[0]


            # BREAK OPTIONS
            if self.objStockChart.Continue == 0:
                break

            elif (str(received_min_date) < str(db_recent_date)):
                break

        return received_data


def remove_accumulation(data):
    '''
    누적 매도 누적 매수를 그냥 그 시간대의 수량으로 변환한다.

    '''
    i=0
    # i 가 len(data) -2 까지
    while(i<len(data)-1):

        #일자로 크기 비교
        if data[i][0][8:12] >data[i+1][0][8:12] :
            data[i][7] = data[i][7] - data[i+1][7]
            data[i][8] = data[i][8] - data[i+1][8]
            i+=1
        elif data[i][0][8:12] < data[i+1][0][8:12] :
            i+=1
        elif data[i][0][8:12] == data[i + 1][0][8:12]:
            i+=1

    if data[len(data)-1][0][8:12] == '0901':
        return data

    else:
        return data[:-1]

if __name__ == '__main__':
    chart = Cy_chart()

    data = chart.request_minute(code = 'A005930', length = 5, request_num = 500, db_recent_date = 0)
    print(data)

    print(len(data))
