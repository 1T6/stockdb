import pymysql




conn = pymysql.connect(host='localhost', user='root', password='1234', db='stockdb_day', charset='utf8')
curs = conn.cursor()


print(conn)
print(curs)