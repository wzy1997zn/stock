import baostock as bs
import pandas as pd
import numpy as np

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
        print(result['turn'])
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
    df = bs_data(id,start,end)
    df = df[df.turn != '']
    data_list = []
    index_list = []
    for indexs in df.index:
        cur = df.loc[indexs]

        if float(cur['turn']) > 5:
            cur_list = (df.loc[df.index[indexs - 15:indexs + 15]])['close'].tolist()
            data_list.append(cur_list)
            index_list.append(indexs)

    data = np.array(data_list)
    lists = []
    for each in data_list:
        lists.append(np.array(each))
    data = np.array(lists)

    return data


if __name__=="__main__":
    data_list = get_high_turn(600187)
    print(data_list)




