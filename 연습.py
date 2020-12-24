from creon import *
import pandas as pd
import pymysql
import sys

code_mgr = Cy_code_manger()

kospi_200 = code_mgr.get_kospi_200_codes()
kosdaq_150 = code_mgr.get_kosdaq_150_codes()
codes = kospi_200+ kosdaq_150

print(codes[139])

conn = pymysql.connect(host='localhost', user='root', password='1234', db='stockdb_min_5', charset='utf8')
curs = conn.cursor()

db_recent_date = get_recent_date_time(curs, codes[139], 'minute')

print(db_recent_date)

chart = Cy_chart()

data = chart.request_minute(codes[139], length=5, request_num = 200000, db_recent_date= db_recent_date)

print(len(data))

print(data[47960])

print(sys.getsizeof(data))

data = remove_accumulation(data)

print(len(data))
