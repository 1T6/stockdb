import sys
from PyQt5.QtWidgets import *
import win32com.client
import pandas as pd
import os
import time

g_objCodeMgr = win32com.client.Dispatch('CpUtil.CpCodeMgr')
g_objCpStatus = win32com.client.Dispatch('CpUtil.CpCybos')


class Cy_stockadj:

    def __init__(self):
        self.obj_stock_adj = win32com.client.Dispatch('CpSysDib.StockAdj')

    def request_stock_adj(self, code):
        self.obj_stock_adj.SetInputValue(0, code)
        self.obj_stock_adj.BlockRequest()

        for i in range(3):
            print(self.obj_stock_adj.GetHeaderValue(i))

        for i in range(self.obj_stock_adj.GetHeaderValue(2)):
            print(self.obj_stock_adj.GetDataValue(0, i))
            print(self.obj_stock_adj.GetDataValue(1, i))
            print(self.obj_stock_adj.GetDataValue(2, i))
            print(self.obj_stock_adj.GetDataValue(3, i))
            print(self.obj_stock_adj.GetDataValue(4, i))
            print(self.obj_stock_adj.GetDataValue(5, i))
            print(self.obj_stock_adj.GetDataValue(6, i))
            print(self.obj_stock_adj.GetDataValue(7, i))
            print()


class CpStockChart:
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

    # 차트 요청 - 기간 기준으로
    def RequestFromTo(self, code, fromDate, toDate, caller):
        print(code, fromDate, toDate)
        # 연결 여부 체크
        bConnect = g_objCpStatus.IsConnect
        if (bConnect == 0):
            print("PLUS가 정상적으로 연결되지 않음. ")
            return False

        self.objStockChart.SetInputValue(0, code)  # 종목코드
        self.objStockChart.SetInputValue(1, ord('1'))  # 기간으로 받기
        self.objStockChart.SetInputValue(2, toDate)  # To 날짜
        self.objStockChart.SetInputValue(3, fromDate)  # From 날짜
        # self.objStockChart.SetInputValue(4, 500)  # 최근 500일치
        self.objStockChart.SetInputValue(5, [0, 2, 3, 4, 5, 8])  # 날짜,시가,고가,저가,종가,거래량
        self.objStockChart.SetInputValue(6, ord('D'))  # '차트 주기 - 일간 차트 요청
        self.objStockChart.SetInputValue(9, ord('1'))  # 수정주가 사용
        self.objStockChart.BlockRequest()

        rqStatus = self.objStockChart.GetDibStatus()
        rqRet = self.objStockChart.GetDibMsg1()
        print("통신상태", rqStatus, rqRet)
        if rqStatus != 0:
            exit()

        len = self.objStockChart.GetHeaderValue(3)

        caller.dates = []
        caller.opens = []
        caller.highs = []
        caller.lows = []
        caller.closes = []
        caller.vols = []
        for i in range(len):
            caller.dates.append(self.objStockChart.GetDataValue(0, i))
            caller.opens.append(self.objStockChart.GetDataValue(1, i))
            caller.highs.append(self.objStockChart.GetDataValue(2, i))
            caller.lows.append(self.objStockChart.GetDataValue(3, i))
            caller.closes.append(self.objStockChart.GetDataValue(4, i))
            caller.vols.append(self.objStockChart.GetDataValue(5, i))

        print(len)

    # 차트 요청 - 최근일 부터 개수 기준
    def RequestDWM(self, code, dwm, count, caller):
        # 연결 여부 체크
        bConnect = g_objCpStatus.IsConnect
        if (bConnect == 0):
            print("PLUS가 정상적으로 연결되지 않음. ")
            return False

        self.objStockChart.SetInputValue(0, code)  # 종목코드
        self.objStockChart.SetInputValue(1, ord('2'))  # 개수로 받기
        self.objStockChart.SetInputValue(4, count)  # 최근 500일치
        self.objStockChart.SetInputValue(5, [0, 2, 3, 4, 5, 8])  # 요청항목 - 날짜,시가,고가,저가,종가,거래량
        self.objStockChart.SetInputValue(6, dwm)  # '차트 주기 - 일/주/월
        self.objStockChart.SetInputValue(9, ord('1'))  # 수정주가 사용
        self.objStockChart.BlockRequest()

        rqStatus = self.objStockChart.GetDibStatus()
        rqRet = self.objStockChart.GetDibMsg1()
        print("통신상태", rqStatus, rqRet)
        if rqStatus != 0:
            exit()

        len = self.objStockChart.GetHeaderValue(3)

        caller.dates = []
        caller.opens = []
        caller.highs = []
        caller.lows = []
        caller.closes = []
        caller.vols = []
        caller.times = []
        for i in range(len):
            caller.dates.append(self.objStockChart.GetDataValue(0, i))
            caller.opens.append(self.objStockChart.GetDataValue(1, i))
            caller.highs.append(self.objStockChart.GetDataValue(2, i))
            caller.lows.append(self.objStockChart.GetDataValue(3, i))
            caller.closes.append(self.objStockChart.GetDataValue(4, i))
            caller.vols.append(self.objStockChart.GetDataValue(5, i))

        print(len)

        return

    def request_minute(self, code, length, request_num):

        if code[0]!= 'A':
            code = 'A' + code

        received_data = []
        received_num = 0


        #연결 확인
        self._check_connection_status()

        self.objStockChart.SetInputValue(0, code)  # 종목코드
        self.objStockChart.SetInputValue(1, ord('2'))  # 개수로 받기
        self.objStockChart.SetInputValue(4, request_num)  # 조회 개수
        self.objStockChart.SetInputValue(5, [0, 1, 2, 3, 4, 5, 8, 9, 10, 11])  # 요청항목 - 날짜, 시간,시가,고가,저가,종가,거래량,거래대금, 누적매도, 누적매수
        # 요청항목 - 날짜, 시간,시가,고가,저가,종가,거래량
        self.objStockChart.SetInputValue(6, ord('m'))  # '차트 주기 - 분/틱
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

                temp = []

                date = self.objStockChart.GetDataValue(0, i)
                minute = self.objStockChart.GetDataValue(1, i)
                open = self.objStockChart.GetDataValue(2, i)
                high = self.objStockChart.GetDataValue(3, i)
                low = self.objStockChart.GetDataValue(4, i)
                close = self.objStockChart.GetDataValue(5, i)
                volume = self.objStockChart.GetDataValue(6, i)
                trading_value = self.objStockChart.GetDataValue(7, i)
                acu_sell = self.objStockChart.GetDataValue(8, i)
                acu_buy = self.objStockChart.GetDataValue(9, i)

                if int(minute) < 1000:
                    date = str(date) + '0' + str(minute) + '00'

                else:
                    date = str(date) + str(minute) + '00'
                temp = [date, open, high, low, close, volume,trading_value, acu_sell, acu_buy]

                received_data.append(temp)
            # BREAK OPTIONS
            if self.objStockChart.Continue ==0:
                break



        return received_data


    def request_day(self, code,request_num):

        if code[0]!= 'A':
            code = 'A' + code

        received_data = []
        received_num = 0


        #연결 확인
        self._check_connection_status()

        self.objStockChart.SetInputValue(0, code)  # 종목코드
        self.objStockChart.SetInputValue(1, ord('2'))  # 개수로 받기
        self.objStockChart.SetInputValue(4, request_num)  # 조회 개수
        self.objStockChart.SetInputValue(5, [0, 1, 2, 3, 4, 5, 6, 8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,37])
        # 요청항목 - 날짜, 시간,시가,고가,저가,종가,거래량
        self.objStockChart.SetInputValue(6, ord('D'))  # '차트 주기 - 분/틱
        self.objStockChart.SetInputValue(9, ord('1'))  # 수정주가 사용

        while request_num >received_num:
            self.objStockChart.BlockRequest()
            #통신상태 확인
            self._check_rq_status()
            time.sleep(0.25)

            received_length = self.objStockChart.GetHeaderValue(3)  # 받아온 데이터 개수
            received_length = min(received_length, request_num-received_num)
            received_num = received_num + received_length


            for j in range(24):
                print('{} : {}'.format(j, self.objStockChart.GetHeaderValue(j)))

            for i in range(received_length):

                temp =[]

                for j in range(27):
                    temp.append(self.objStockChart.GetDataValue(j, i))
                received_data.append(temp)

            received_min_date = min(received_data)[0]

            # BREAK OPTIONS
            if self.objStockChart.Continue ==0:
                break

        return received_data


    def remove_acuumulation(data):
        '''
        누적 매도 누적 매수를 그냥 그 시간대의 수량으로 변환한다.

        '''
        i=0
        while(i<len(data)-1):

            if data[i][0][8:12] >data[i+1][0][8:12] :

                data[i][7] = data[i][7] -data[i+1][7]
                data[i][8] = data[i][8] - data[i + 1][8]
                i+=1

            elif data[i][0][8:12] < data[i+1][0][8:12] :

                i+=1

        if data[len(data)-1][0][8:12] == '0901':
            return data[:-1]

        else:
            return data



# 날짜 시간 시가 고가 저가 종가 전일대비 거래량 거래대금 누적체결매도수량 누적체결매수수량 상장주식수 시가총액 외국인주문한도수량
# 외국인주문가능수량 외국인현보유수량 외국인현보유비율 수정주가일자 수정주가비율 기관순매수 기관누적순매수 등락주선 등락비율
# 예탁금 주식회전율 거래성립률 대비부호

if __name__ == "__main__":

    chart = CpStockChart()

    print('1분봉')
    #data = chart.request_minute('A005930',  length = 1, request_num = 500)

    #print(data)
    print()
    #data = remove_accumulation(data)
    #print(data)
    time.sleep(0.25)

    print('일봉')



    data = chart.request_day('A005930',request_num = 1000)
    for row in data:
        print(row)
