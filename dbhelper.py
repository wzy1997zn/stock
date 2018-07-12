# -*- coding: utf-8 -*-
import  pymysql

class dbhelper:
    coon = 'test'

    def __init__(self):
        pass

    def open(self,dbname):
        self.coon = pymysql.connect(
            host='127.0.0.1', user='root', passwd='',
            port=3306, db=dbname, charset='utf8'
            # port必须写int类型
            # charset必须写utf8，不能写utf-8
        )

    def insert(self,sql):
        cur = self.coon.cursor()  # 建立游标
        cur.execute(sql)    # 执行插入
        self.coon.commit()
        # res = cur.fetchall()  # 获取结果
        # print(res)
        cur.close()  # 关闭游标

    def select(self,sql):
        cur = self.coon.cursor()  # 建立游标
        cur.execute(sql)  # 查询数据
        res = cur.fetchall()  # 获取结果
        # print(res)
        cur.close()  # 关闭游标
        return res

    def close(self):
        self.coon.close() # 关闭连接
