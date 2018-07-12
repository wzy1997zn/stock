# -*- coding: utf-8 -*-
import xlrd
from dbhelper import dbhelper

class stockdatainsert:
    def exceltomysql(self):
        data = xlrd.open_workbook("shangzheng.xlsx")  # 打开excel
        table = data.sheet_by_name("Sheet1")  # 读sheet
        nrows = table.nrows  # 获得行数
        result = []
        attrs = table.row_values(0)

        coon = dbhelper()
        coon.open('stock')
        for i in range(1, nrows):  #
            rows = table.row_values(i)  # 行的数据放在数组里
            date = str(int(rows[0]))
            close = str(rows[4])
            sql = 'insert into value(date,close) VALUE ("' + date + '","' + close + '");'
            coon.insert(sql)
            result.append(rows)
        print(result)
        coon.close()

if __name__ == "__main__":
    inserter = stockdatainsert()
    inserter.exceltomysql()



