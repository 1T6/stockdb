import pymysql



conn = pymysql.connect(host='localhost', user='root', password='1234', db='stockdb_min_1', charset='utf8')
curs = conn.cursor()

sql = 'select max(`일자`) from `A005930`'

curs.execute(sql)

a = curs.fetchall()

print(a[0][0])


