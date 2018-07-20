# -*- coding: utf-8 -*-


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans,DBSCAN
from sklearn import decomposition,manifold
import time

def get_data():

    df = pd.read_csv('tags.csv', header=None, sep=',')
    plot(df)


def plot(data,n_cluster):


    X = pd.DataFrame(data)
    # X=data.drop([0, 0],inplace=False)

    pca=decomposition.PCA(n_components=2) # 利用PCA库来创建一个PCA降维模型，输入参数为降维目标，打算降到二维聚类，方便可视化
    pca.fit(X) # 对数据集X进行降维
    X_r=pca.transform(X) # 将转换得到的新的X数据集赋值出来

    # X_r = X

    # mds = manifold.MDS(n_components=10) # 类似的，使用MDS库创建MDS降维模型
    # X_r = mds.fit_transform(X) # 降维并输出

    estimator = KMeans(n_clusters=n_cluster)  # 构造聚类器 输入参数为目标类别数
    time_start = time.time()
    estimator.fit(X_r)  # 对降维后的数据集聚类
    time_end = time.time()

    # 采用sklearn库提供的DBSCAN方法
    # clst = DBSCAN(eps=0.2,min_samples=5)
    # predict_labels = clst.fit_predict(X_r)

    label_pred = estimator.labels_  # 获取聚类标签
    Y = label_pred
    # Y = predict_labels
    # print(X_r)
    # show(X_r,Y)

    return Y

def show(X_r,Y):
    # 用plt库来进行可视化
    fig = plt.figure()  # 生成绘图区
    ax = fig.add_subplot(1, 1, 1)  # 创建坐标系
    colors = (
    (1, 0, 0), (0, 1, 0), (0, 0, 1), (0.5, 0.5, 0), (0, 0.5, 0.5), (0.5, 0, 0.5), (0.4, 0.6, 0), (0.6, 0.4, 0),
    (0, 0.6, 0.4), (0.5, 0.3, 0.2),)  # 提供颜色选择
    for label, color in zip(np.unique(Y), colors):  # 对每个类别匹配一个颜色
        position = Y == label
        #      print(position)
        ax.scatter(X_r[position, 0], X_r[position, 1], label="target=%d" % label, color=color)  # 绘制聚类结果的点
    ax.set_xlabel("X[0]")  # 坐标轴标注
    ax.set_ylabel("Y[0]")
    ax.legend(loc="best")  # 图例
    ax.set_title("tags")  # 题目
    plt.show()  # 显示

if __name__ == "__main__":
    # 程序字符编码处理

    get_data()