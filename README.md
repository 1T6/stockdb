# stockdb

-------prerequisite--------

DB로 MYSQL을 사용한다.
생성해야 하는 DB목록.
stockdb_day,
,stockdb_min_1
,stockdb_min_3
,stockdb_min_5
,stockdb_min_10
,stockdb_min_15

대신증권 api이용 등록해야 함.
대신증권 cyboos plus 실행된 상태에서 db_updater 실행시킨다.
파이썬버전3.7.4 32bit

-------------------------------------------------


db_updater 누르면 DB에 저장된 최근일 이후로 전부 받아온다. 수정주가 이벤트가 발생하면 자동으로 이전 DB데이터들에 반영한다.

코스닥 150, 코스피 200 종목들만 받아오게 되어있다.(약간만 코드 수정하면 전종목 가능)




