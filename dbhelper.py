# -*- coding: utf-8 -*-
import pymysql

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
        try:
            # 执行sql语句
            cur.execute(sql)
            # 执行sql语句
            self.coon.commit()
        except:
            # 发生错误时回滚
            self.coon.rollback()
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

    def create(self,id):
        # 使用 cursor() 方法创建一个游标对象 cursor
        cursor = self.coon.cursor()
        cursor.execute("DROP TABLE IF EXISTS sh" + id)
        sql = 'CREATE TABLE sh'+ str(id) +' (  `id` int(20) NOT NULL AUTO_INCREMENT ,  `date` INT,  `value` double,  PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8'
        cursor.execute(sql)

        sql = 'ALTER TABLE sh'+ str(id) +'  ADD `contents` MEDIUMTEXT  ,  ADD `vector` MEDIUMTEXT  ,  ADD `increasing` INT  ;'
        cursor.execute(sql)
        cursor.close()
