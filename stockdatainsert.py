# -*- coding: utf-8 -*-
import xlrd
from dbhelper import dbhelper
from snowballspider.spider import get_indexes
import pandas as pd

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

    def csvtomysql(self,id):
        base_path = 'C:/Users/wzy/Desktop/export/'
        try:
            data = pd.read_table(base_path + 'SH#' + str(id) + '.txt',header=None,encoding='gb2312',delimiter=',',names=["date",'open','high','low','close','vol','count'])  # 打开csv
        except:
            return
        # table = data.sheet_by_name(str(id) + ".SH")  # 读sheet
        date = data['date'].tolist()
        close = data['close'].tolist()
        increasing = []
        for i in range(len(close)-1):
            if close[i+1] > close[i]:
                increasing.append(1)
            else:
                increasing.append(0)
        increasing.append(1)


        coon = dbhelper()
        coon.open('stock')
        for i in range(len(close)):  #
            # rows = table.row_values(i)  # 行的数据放在数组里
            cur_date = str(date[i])
            cur_close = str(close[i])
            cur_increasing = str(increasing[i])
            sql = 'update sh'+str(id)+' set value = "' + cur_close + '", increasing = "'+cur_increasing+'" where date= "' + cur_date + '";'
            coon.insert(sql)
            # result.append(rows)
        # print(result)
        coon.close()

if __name__ == "__main__":
    inserter = stockdatainsert()
    # inserter.exceltomysql()
    index_list = get_indexes('C:/Users/wzy/Desktop/暑期实训/data/上证A股/上证A股')
    for each in index_list:
        inserter.csvtomysql(each)



