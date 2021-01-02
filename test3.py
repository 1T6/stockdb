import pymysql
import datetime
import pandas as pd

conn = pymysql.connect(host='localhost', user='root', password='1234', db='stockdb_min_1', charset='utf8')
curs = conn.cursor()

sql = 'select * from `A005930` order by `일자` desc limit 10;'

curs.execute(sql)

data = curs.fetchall()

print(data[0][0])

columns = ['일자', '시가', '고가','저가','종가','거래량','거래대금','매도','매수']
df = pd.DataFrame(data, columns = columns)

rate =50

print(df)
df[['시가','종가']] = df[['시가','종가']]*50
print(df)

print(df[['시가']])

print(df.values.tolist())