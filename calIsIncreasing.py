# -*- coding: utf-8 -*-
from dbhelper import dbhelper

def isIncreasing():
    result = []
    coon = dbhelper()
    coon.open('stock')
    sql = 'select date, value from merge order by merge.date asc'
    data = coon.select(sql)
    for i in range(len(data)-1):
        # 此处作为计算分类的根源，将股票指数简单进行了二分类，可以考虑进行10分类之类的
        if data[i][1] < data[i+1][1]:
            temp = list(data[i])
            temp.append(1)
        else:
            temp = list(data[i])
            temp.append(0)
        result.append(temp)
        sqlcur = 'update merge set increasing = ' + str(temp[2]) + ' where date = ' + str(temp[0])
        coon.insert(sqlcur)

    coon.close()

    return result

if __name__ == '__main__':
    isIncreasing()