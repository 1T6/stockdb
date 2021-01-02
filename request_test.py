import pymysql
from creon import *
from module import *

chart = Cy_chart()


conn = pymysql.connect(host='localhost', user='root', password='1234', db='stockdb_day', charset='utf8')
curs = conn.cursor()
db_recent_date = get_recent_date_time(curs, 'A001060', db_type = 'day')
day_data = chart.request_day(code = 'A001060', request_num = 20, db_recent_date=db_recent_date)

print(day_data)




