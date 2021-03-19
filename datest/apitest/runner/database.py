"""
@project: PyCharm
@author: MZM
@file: database.py
@ide: PyCharm
@time: 2021/3/7 17:49
@desc： 
"""
import pymysql


class getSqldata():
    def __init__(self,host='127.0.0.1',
                        port=3306,
                        user='root',
                        password='',
                        database='shopxo',
                        charset="utf8"):
        self.conn = pymysql.connect(host=host,
                        port=port,
                        user=user,
                        password=password,
                        database=database,
                        charset=charset)

    def query(self,s):
        cursor = self.conn.cursor()
        cursor.execute(s)
        res = cursor.fetchall()
        cursor.close()
        return res

    def exec(self,s):
        cursor = self.conn.cursor()
        try:
            cursor.execute(s)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
        cursor.close()