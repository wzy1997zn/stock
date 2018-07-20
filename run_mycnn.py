# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import sys
import time
from datetime import timedelta

import numpy as np
import tensorflow as tf
from sklearn import metrics

from my_cnn_model import MyCNNConfig, MyCNN
from data.cnews_loader import read_vocab, read_category, batch_iter, process_file, build_vocab
from dbhelper import dbhelper
from tensorflow.python import debug as tf_debug
import pandas as pd
import datetime
from newsspider import conphantomjs
import threading
import tushare
from news2vec import newsNLP

base_dir = 'data/cnews'
train_dir = os.path.join(base_dir, 'cnews.train.txt')
test_dir = os.path.join(base_dir, 'cnews.test.txt')
val_dir = os.path.join(base_dir, 'cnews.val.txt')
vocab_dir = os.path.join(base_dir, 'cnews.vocab.txt')

save_dir = 'my_checkpoints/textcnn'
save_path = os.path.join(save_dir, 'best_validation')  # 最佳验证结果保存路径


def get_time_dif(start_time):
    """获取已使用时间"""
    end_time = time.time()
    time_dif = end_time - start_time
    return timedelta(seconds=int(round(time_dif)))


def feed_data(x_batch, y_batch, keep_prob):
    feed_dict = {
        model.input_x: x_batch,
        model.input_y: y_batch,
        model.keep_prob: keep_prob
    }
    return feed_dict


def evaluate(sess, x_, y_):
    """评估在某一数据上的准确率和损失"""
    data_len = len(x_)
    batch_eval = batch_iter(x_, y_, 128)
    total_loss = 0.0
    total_acc = 0.0
    for x_batch, y_batch in batch_eval:
        batch_len = len(x_batch)
        feed_dict = feed_data(x_batch, y_batch, 1.0)
        loss, acc = sess.run([model.loss, model.acc], feed_dict=feed_dict)
        total_loss += loss * batch_len
        total_acc += acc * batch_len

    return total_loss / data_len, total_acc / data_len


def getData(type):
    # 从数据库读入
    coon = dbhelper()
    coon.open('stock')
    sql = 'select vector,increasing from dataset order by id asc'
    if type == 'train':
        sql = sql + ' limit 100,200'
    else:
        sql = sql + ' limit 0,100'
    data = coon.select(sql)
    coon.close()
    x = []
    y = []
    for each in data:
        x.append([[np.float32(x) for x in each[0].split()]] * 5)
        ytemp = [0,0]
        ytemp[each[1]] = 1  # 在此划分分类层数
        y.append(ytemp)

    print()
    return x,y

def getData2(type):
    # 从数据库读入
    coon = dbhelper()
    coon.open('stock')
    sql = 'select vector,increasing from merge2 order by id asc'
    if type == 'train':
        sql = sql + ' limit 20000,70000'
    elif type == 'test':
        # sql = sql + ' limit 1500,20000'
        sql = 'select vector,increasing from merge order by date asc'
    elif type == 'predict':
        sql = 'select vector,increasing from merge order by date desc limit 0 , 5'

    else:
        sql = sql + ' limit 0,20000'
    data = coon.select(sql)
    coon.close()
    x = []
    y = []
    if type == 'predict':
        data = list(data)
        data.reverse()
        matrix = []
        for each in data:
            matrix.append(list(np.float32(each[0].split())))
        x.append(matrix)
        y = [[0,0]]
        return x,y

    for i in range(len(data)-5):
        matrix = []
        for j in range(5):
            matrix.append([np.float32(x) for x in data[i+5-j][0].split()])
        # x.append([[np.float32(x) for x in data[i][0].split()]] * 5)
        x.append(matrix)


        ytemp = [0,0]
        ytemp[data[i][1]] = 1  # 在此划分分类层数
        y.append(ytemp)

    print()
    return x,y


def train():
    print("Configuring TensorBoard and Saver...")
    # 配置 Tensorboard，重新训练时，请将tensorboard文件夹删除，不然图会覆盖
    tensorboard_dir = 'my_tensorboard/textcnn'
    if not os.path.exists(tensorboard_dir):
        os.makedirs(tensorboard_dir)

    tf.summary.scalar("loss", model.loss)
    tf.summary.scalar("accuracy", model.acc)
    merged_summary = tf.summary.merge_all()
    writer = tf.summary.FileWriter(tensorboard_dir)

    # 配置 Saver
    saver = tf.train.Saver()
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    print("Loading training and validation data...")
    # 载入训练集与验证集
    start_time = time.time()
    # x_train, y_train = process_file(train_dir, word_to_id, cat_to_id, config.seq_length)
    # x_val, y_val = process_file(val_dir, word_to_id, cat_to_id, config.seq_length)

    # 使用自己的训练集
    x_train,y_train = getData2('train')
    x_val,y_val = getData2('val')

    time_dif = get_time_dif(start_time)
    print("Time usage:", time_dif)

    # 创建session
    session = tf.Session()
    session.run(tf.global_variables_initializer())
    debug_session = tf_debug.LocalCLIDebugWrapperSession(sess=session)
    writer.add_graph(session.graph)

    print('Training and evaluating...')
    start_time = time.time()
    total_batch = 0  # 总批次
    best_acc_val = 0.0  # 最佳验证集准确率
    last_improved = 0  # 记录上一次提升批次
    require_improvement = 3000  # 如果超过1000轮未提升，提前结束训练

    flag = False
    for epoch in range(config.num_epochs):
        print('Epoch:', epoch + 1)
        batch_train = batch_iter(x_train, y_train, config.batch_size)
        for x_batch, y_batch in batch_train:
            feed_dict = feed_data(x_batch, y_batch, config.dropout_keep_prob)

            if total_batch % config.save_per_batch == 0:
                # 每多少轮次将训练结果写入tensorboard scalar
                s = session.run(merged_summary, feed_dict=feed_dict)
                writer.add_summary(s, total_batch)

            if total_batch % config.print_per_batch == 0:
                # 每多少轮次输出在训练集和验证集上的性能
                feed_dict[model.keep_prob] = 1.0
                loss_train, acc_train = session.run([model.loss, model.acc], feed_dict=feed_dict)
                loss_val, acc_val = evaluate(session, x_val, y_val)  # todo

                if acc_val > best_acc_val:
                    # 保存最好结果
                    best_acc_val = acc_val
                    last_improved = total_batch
                    saver.save(sess=session, save_path=save_path)
                    improved_str = '*'
                else:
                    improved_str = ''

                time_dif = get_time_dif(start_time)
                msg = 'Iter: {0:>6}, Train Loss: {1:>6.2}, Train Acc: {2:>7.2%},' \
                      + ' Val Loss: {3:>6.2}, Val Acc: {4:>7.2%}, Time: {5} {6}'
                print(msg.format(total_batch, loss_train, acc_train, loss_val, acc_val, time_dif, improved_str))

            session.run(model.optim, feed_dict=feed_dict)  # 运行优化
            total_batch += 1

            if total_batch - last_improved > require_improvement:
                # 验证集正确率长期不提升，提前结束训练
                print("No optimization for a long time, auto-stopping...")
                flag = True
                break  # 跳出循环
        if flag:  # 同上
            break

def test():
    print("Loading test data...")
    start_time = time.time()
    x_test, y_test = getData2('test')

    session = tf.Session()
    session.run(tf.global_variables_initializer())
    saver = tf.train.Saver()
    saver.restore(sess=session, save_path=save_path)  # 读取保存的模型

    print('Testing...')
    loss_test, acc_test = evaluate(session, x_test, y_test)
    msg = 'Test Loss: {0:>6.2}, Test Acc: {1:>7.2%}'
    print(msg.format(loss_test, acc_test))

    batch_size = 128
    data_len = len(x_test)
    num_batch = int((data_len - 1) / batch_size) + 1

    y_test_cls = np.argmax(y_test, 1)
    y_pred_cls = np.zeros(shape=len(x_test), dtype=np.int32)  # 保存预测结果
    for i in range(num_batch):  # 逐批次处理
        start_id = i * batch_size
        end_id = min((i + 1) * batch_size, data_len)
        feed_dict = {
            model.input_x: x_test[start_id:end_id],
            model.keep_prob: 1.0
        }
        y_pred_cls[start_id:end_id] = session.run(model.y_pred_cls, feed_dict=feed_dict)

    # 输出
    coon = dbhelper()
    coon.open('stock')
    sql = 'select date from merge order by date asc'
    date = coon.select(sql)[-1-len(y_pred_cls):-1]
    dataframe = pd.DataFrame({'date':date,'pred': y_pred_cls.tolist()})
    coon.close()

    dataframe.to_csv("pred.csv", index=False, sep=',')


    # 评估
    print("Precision, Recall and F1-Score...")
    categories = ['涨','跌']
    print(metrics.classification_report(y_test_cls, y_pred_cls, target_names=categories))

    # 混淆矩阵
    print("Confusion Matrix...")
    cm = metrics.confusion_matrix(y_test_cls, y_pred_cls)
    print(cm)

    time_dif = get_time_dif(start_time)
    print("Time usage:", time_dif)


def predict():
    print("Loading test data...")
    start_time = time.time()
    x_test, y_test = getData2('predict')

    session = tf.Session()
    session.run(tf.global_variables_initializer())
    saver = tf.train.Saver()
    saver.restore(sess=session, save_path=save_path)  # 读取保存的模型

    print('Testing...')
    # loss_test, acc_test = evaluate(session, x_test, y_test)
    msg = 'Test Loss: {0:>6.2}, Test Acc: {1:>7.2%}'
    # print(msg.format(loss_test, acc_test))

    batch_size = 1
    data_len = len(x_test)
    num_batch = int((data_len - 1) / batch_size) + 1

    # y_test_cls = np.argmax(y_test, 1)
    y_pred_cls = np.zeros(shape=len(x_test), dtype=np.int32)  # 保存预测结果
    for i in range(num_batch):  # 逐批次处理
        start_id = i * batch_size
        end_id = min((i + 1) * batch_size, data_len)
        feed_dict = {
            model.input_x: x_test[start_id:end_id],
            model.keep_prob: 1.0
        }
        y_pred_cls[start_id:end_id] = session.run(model.y_pred_cls, feed_dict=feed_dict)

    # 输出
    coon = dbhelper()
    coon.open('stock')
    sql = 'select date from merge order by date asc'
    date = coon.select(sql)[-len(y_pred_cls):]
    dataframe = pd.DataFrame({'date':date,'pred': y_pred_cls.tolist()})
    coon.close()

    dataframe.to_csv("pred_tomorrow.csv", index=False, sep=',')


    # # 评估
    # print("Precision, Recall and F1-Score...")
    # categories = ['涨','跌']
    # print(metrics.classification_report(y_test_cls, y_pred_cls, target_names=categories))
    #
    # # 混淆矩阵
    # print("Confusion Matrix...")
    # cm = metrics.confusion_matrix(y_test_cls, y_pred_cls)
    # print(cm)
    #
    # time_dif = get_time_dif(start_time)
    # print("Time usage:", time_dif)


def predict_tomorrow():
    get_contents()
    get_value()
    get_vector()
    predict()

def get_vector():
    news = newsNLP()
    news.get_contents()
    news.get_list_jieba()
    news.Tfidf()
    news.SVD(200)
    news.save_lsa_vector()

def get_value():
    df = tushare.get_index()
    sz_value = df.iat[0,5]
    preclose = df.iat[0,4]
    increasing = 0
    if sz_value > preclose:
        increasing = 1
    today_date = datetime.datetime.now().strftime('%Y%m%d')
    coon = dbhelper()
    coon.open("stock")
    sql2 = 'select date from merge order by date desc limit 1,1'
    last_date = coon.select(sql2)
    sql1 = 'update merge set increasing = ' + str(increasing) + ' where date = ' + str(last_date[0][0])
    coon.insert(sql1)
    sql = 'update merge set value = ' + str(sz_value) + ' where date = ' + str(today_date)
    coon.insert(sql)
    coon.close()

def get_contents():
    cur = conphantomjs()
    conphantomjs.phantomjs_max = 1
    cur.open_phantomjs()
    print("phantomjs num is ", cur.q_phantomjs.qsize())

    # url_list = ["http://www.baidu.com"] * 50

    url_list = cur.get_today_url_by_list()

    cur.getbody(url_list[0])


def get_date(start,end):
    # start = '2016-06-01'
    # end = '2017-01-01'
    datestart = datetime.datetime.strptime(start, '%Y-%m-%d')
    dateend = datetime.datetime.strptime(end, '%Y-%m-%d')
    datelist = []
    while datestart < dateend:
        datestart += datetime.timedelta(days=1)
        date = datestart.strftime('%Y-%m-%d')
        datelist.append(date)
    return datelist

if __name__ == '__main__':
    config = MyCNNConfig()
    model = MyCNN(config)

    # train()
    test()
    # predict_tomorrow()