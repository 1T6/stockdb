import pymysql
from creon import *
from module import *



code_mgr = Cy_code_manger()

kospi_200 = code_mgr.get_kospi_200_codes()
kosdaq_150 = code_mgr.get_kosdaq_150_codes()
codes = kospi_200+kosdaq_150


print(codes.index('A001060'))
print(codes[18])

