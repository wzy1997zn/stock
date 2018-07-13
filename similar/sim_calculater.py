# coding:utf-8
from similar.gauss import get_gauss
from sklearn import preprocessing
import numpy as np
import math
import matplotlib.pyplot as plt


class sim_calculater(object):
    def __init__(self,file_path_1, file_path_2):
        """初始化"""
        self.get_data(file_path_1,file_path_2)


    def get_data(self,file_path_1, file_path_2):
        """获得数据"""
        x1,y1 = get_gauss(file_path_1)
        x2,y2 = get_gauss(file_path_2)

        if len(x1) > len(x2):
            self.x = x2
            self.y1 = y1[-len(self.x):]
            self.y2 = y2
        else:
            self.x = x1
            self.y1 = y1
            self.y2 = y2[-len(self.x):]
        self.total_length = len(self.x)

    def cut(self,length,step):
        """切割数据"""
        # input
        # length：窗口长度
        # step：窗口移动距离

        cut_data_1 = []
        cut_data_2 = []
        for i in range(0,self.total_length,step):
            if i + length < self.total_length:
                window_1 = self.y1[i:i+length]
                window_2 = self.y2[i:i+length]
            else:
                window_1 = self.y1[i:]
                window_2 = self.y2[i:]
            cut_data_1.append(window_1)
            cut_data_2.append(window_2)

        return cut_data_1,cut_data_2

    def fit(self,y_list,exp,scale):
        """
        输入一段y拟合一个曲线,默认4次
        :param y_list:要拟合的数据
        :param exp:多项式次数
        :param scale:是否标准化
        :return z:多项式次数长度的list，代表从高到低次数多项式的参数
        """

        length = len(y_list)
        if scale:
            y_list = preprocessing.scale(y_list)
            for i in range(len(y_list)):
                y_list[i] = y_list[i] * 100
        x = np.arange(1,length+1,1)
        y = np.array(y_list)

        z = np.polyfit(x,y,exp)

        yy = np.polyval(z, x)  # 根据多项式求函数值
        # 进行曲线绘制
        fig = plt.figure()
        ax = fig.add_subplot(111)
        x_new = np.linspace(0, len(y_list), 2000)
        f_liner = np.polyval(z, x_new)
        # ax.plot(x,y,color='m',linestyle='',marker='.')
        ax.plot(x, y, 'b', label='1')
        ax.plot(x_new, f_liner, label=u'拟合多项式曲线', color='g', linestyle='-', marker='')
        plt.show()
        return z

    # 用皮尔逊系数咋样？？？？？
    def cal_sim_degree(self,z1,z2):
        """
        计算两多项式曲线的相似度
        :param z1: 曲线1的参数（由高到低）
        :param z2: 曲线2的参数（由高到低）
        """

        score = 0
        for i in range(len(z1)):
            exp = len(z1) - 1 - i
            p1 = z1[i]
            p2 = z2[i]
            curscore = ((1 + p1 * p2) / (np.sqrt(1 + np.square(p1)) * np.sqrt(1 + np.square(p2))))
            # curscore = curscore * np.square(exp) 再乘上幂次的平方
            # cursore = curscore * exp
            # 类似于计算了在这一幂次上两个斜率的夹角余弦 试试看呗
            score = score + curscore

        # score = score / (sum([x*x for x in range(len(z1))]))
        # score = score / (sum([x for x in range(len(z1))]))
        score = score / len(z1)
        return score

    def curve_sim(self,length=30,step=20,exp=4,scale=True):
        """
        求初始化的两条曲线的相似度
        :param length: 窗口长度
        :param step: 窗口选取步长
        :param exp: 多项式拟合次数
        :param scale: 是否正则化
        """

        cut_data_1,cut_data_2 = self.cut(length,step)
        sim = 0
        for i in range(len(cut_data_1)):
            z1 = self.fit(cut_data_1[i],exp=exp,scale=scale)
            z2 = self.fit(cut_data_2[i],exp=exp,scale=scale)
            cur_win_sim = self.cal_sim_degree(z1,z2)
            sim = sim + cur_win_sim
        sim = sim / len(cut_data_1)

        return str(sim)


if __name__ == '__main__':
    path1 = 'C:/Users/wzy/Desktop/暑期实训/data/zhongruan1.xlsx'  # 中国软件
    path2 = 'C:/Users/wzy/Desktop/暑期实训/data/langchao1.xlsx'  # 浪潮软件
    path3 = 'C:/Users/wzy/Desktop/暑期实训/data/langchaoxinxi1.xlsx'  # 浪潮信息
    path4 = 'C:/Users/wzy/Desktop/暑期实训/data/kangtaishengwu1.xlsx'  # 康泰生物

    cal12 = sim_calculater(path1, path2)
    cal13 = sim_calculater(path1, path3)
    cal14 = sim_calculater(path1, path4)
    cal23 = sim_calculater(path2, path3)
    cal24 = sim_calculater(path2, path4)
    cal34 = sim_calculater(path3, path4)
    print("12:" + cal12.curve_sim())
    print("13:" + cal13.curve_sim())
    print("14:" + cal14.curve_sim())
    print("23:" + cal23.curve_sim())
    print("24:" + cal24.curve_sim())
    print("34:" + cal34.curve_sim())

