
import baostock as bs
import pandas as pd
import numpy as np
from openpyxl import Workbook
from zhencang.tags_cluster import plot


class bshelper:
    def __init__(self):
        #### 登陆系统 ####
        lg = bs.login()
        # 显示登陆返回信息
        print('login respond error_code:' + lg.error_code)
        print('login respond  error_msg:' + lg.error_msg)

    def get_data(self,id,start='2018-01-01',end='2018-07-17'):
        #### 获取沪深A股历史K线数据 ####
        # 详细指标参数，参见“历史行情指标参数”章节
        rs = bs.query_history_k_data("sh."+str(id),
                                     "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,isST",
                                     start_date=start, end_date=end,
                                     frequency="d", adjustflag="3")
        print('query_history_k_data respond error_code:' + rs.error_code)
        print('query_history_k_data respond  error_msg:' + rs.error_msg)

        #### 打印结果集 ####
        data_list = []
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            data_list.append(rs.get_row_data())
        result = pd.DataFrame(data_list, columns=rs.fields)

        #### 结果集输出到csv文件 ####
        # result.to_csv("D:\\history_A_stock_k_data.csv", index=False)
       # print(result['turn'])
        return result

    def close(self):
        #### 登出系统 ####
        bs.logout()

def bs_data(id,start='2014-07-01',end='2018-07-17'):
    b = bshelper()
    result = b.get_data(id,start,end)
    b.close()
    return result

def get_high_turn(id,start='2014-07-01',end='2018-07-17'):
    df = bs_data(id)
    df = df[df.turn != '']
    data_list = []
    data = []

    index_list = []

    for indexs in df.index:
        cur = df.loc[indexs]

        if float(cur['turn']) > 5:
            cur_list = (df.loc[df.index[indexs - 15:indexs + 15]])['close'].tolist()

            ####没有操作####
            if len(cur_list)==0:
                print("No operation")

            ####归一化####

            dis=float(max(cur_list))-float(min(cur_list))
            m=float(min(cur_list))
            # cur_list=(cur_list-min)/dis

            for i in range(0,len(cur_list)):
                temp=(float(cur_list[i])-m)/dis
                cur_list[i]=temp

            data_list.append(cur_list)
            index_list.append(indexs)

            data = np.array(data_list)

    return data

###写入结果###
def writexsl(arr):
    a=arr

    wb = Workbook()
    sheet = wb.active
    for i in range(0,len(a)):
        sheet["A%d" % (i + 1)].value = a[i]
    wb.save('result.xlsx')
    return

def sum_data(a,b):
    arr1=a
    arr2=b
    k=np.row_stack((arr1,arr2))
    return k


def get_data():
    data_list1 = get_high_turn(600059)
    data_list2 = get_high_turn(600062)
    data_list3= get_high_turn(600058)

    data_list = np.row_stack((data_list1, data_list2))
    #data_list = np.row_stack((data_list, data_list3))

    return data_list

def show_by_class(data,labels,n):
    class_data = []
    for i in range(n):
        class_data.append([])
    for i in range(len(labels)):
        class_data[int(labels[i])].append(data[i].tolist())

    for cur_class_data in class_data:
        drawFigure(cur_class_data,[1,2,3,4])



import pylab as pl
def drawFigure(list, nameslist):
    linestyle = ['cx--', 'mo:', 'kp-.', 'bs--', 'p*:']  # 红，绿，黄，蓝，粉,每个折线给不同的颜色

    linenum = len(list)  # list中的元素仍为列表，对应着某一折线图的纵坐标


    x = [i for i in range(0, len(list[0]))]  # 横坐标
    plotlist=[]
    for i in range(1,linenum):
        plot1,=pl.plot(x,list[i]) #一定要有逗号，画出对应的折线图
        plotlist.append(plot1)
        pl.legend(plotlist, nameslist, loc='upper right', shadow=True) #多个折线的图例
        pl.title('Electricity market problem') # 标题
        pl.xlabel('timestamp') # 横坐标标题
        pl.ylabel('Number of rules') # 纵坐标标题
        # pl.xlim(0, 135)
        # pl.ylim(0, 180)
    pl.show()

if __name__=="__main__":
    # data_list1 = get_high_turn(600058)
    n_cluster = 4
    data0 = get_data()
    labels = plot(data0,n_cluster)
    show_by_class(data0,labels,n_cluster)
    print(data0)