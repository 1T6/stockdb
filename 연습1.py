from creon1 import *
import pandas as pd
import pymysql



if __name__ =='__main__':

    code_mgr = Cy_code_manger()

    kospi_200 = code_mgr.get_kospi_200_codes()
    kosdaq_150 = code_mgr.get_kosdaq_150_codes()
    codes = kospi_200 + kosdaq_150


