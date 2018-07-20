# -*- coding: utf-8 -*-

import pymysql
import queue
from selenium import webdriver
import threading
import time
import sys
sys.path.append(r'D:\study\stokespider\ths')
from dbhelper import dbhelper
import datetime

class conphantomjs:
    phantomjs_max = 1  ##同时开启phantomjs个数
    jiange = 0.00001  ##开启phantomjs间隔
    timeout = 20  ##设置phantomjs超时时间
    path = "C:\python27\Scripts\phantomjs.exe"  ##phantomjs路径
    service_args = ['--load-images=no', '--disk-cache=yes']  ##参数设置

    def __init__(self):
        self.q_phantomjs = queue.Queue()  ##存放phantomjs进程队列

    def getbody(self, url):
        '''
        利用phantomjs获取网站源码以及url
        '''
        d = self.q_phantomjs.get()
        # try:
        d.get(url)
        self.save_data(d)

        # except:
        #     print("Phantomjs Open url Error")

        url = d.current_url

        self.q_phantomjs.put(d)

        print (url)

    def save_data(self,d):
        ul = d.find_element_by_xpath("/html/body/div[8]/div[1]/div[2]/ul")
        lis = ul.find_elements_by_tag_name("li")
        date = d.current_url.split("/")[-2]
        contents = ""
        for each in lis:
            title = each.find_element_by_tag_name("span").find_element_by_tag_name("a").text
            abstract = each.find_element_by_tag_name("a").text
            contents = contents + title + "。" + abstract + "。"
            # print each.text

        # coon = pymysql.connect(
        #     host='127.0.0.1', user='root', passwd='',
        #     port=3306, db='stoke', charset='utf8'
        #     # port必须写int类型
        #     # charset必须写utf8，不能写utf-8
        # )
        # cur = coon.cursor()  # 建立游标
        # cur.execute('insert into stokenews(date,contents) VALUE ("' + date + '","' + contents + '");')
        # coon.commit()
        # res = cur.fetchall()  # 获取结果
        # print(res)
        # cur.close()  # 关闭游标
        # coon.close()  # 关闭连接

        coon = dbhelper()
        coon.open('stock')
        sql = 'insert into merge(date,contents) VALUE ("' + date + '","' + contents + '");'
        coon.insert(sql)
        coon.close()

    def open_phantomjs(self):
        '''
        多线程开启phantomjs进程
        '''

        def open_threading():
            d = webdriver.PhantomJS(conphantomjs.path, service_args=conphantomjs.service_args)
            d.implicitly_wait(conphantomjs.timeout)  ##设置超时时间
            d.set_page_load_timeout(conphantomjs.timeout)  ##设置超时时间

            self.q_phantomjs.put(d)  # 将phantomjs进程存入队列

        th = []
        for i in range(conphantomjs.phantomjs_max):
            t = threading.Thread(target=open_threading)
            th.append(t)
        for i in th:
            i.start()
            time.sleep(conphantomjs.jiange)  # 设置开启的时间间隔
        for i in th:
            i.join()

    def close_phantomjs(self):
        '''
        多线程关闭phantomjs对象
        '''
        th = []

        def close_threading():
            d = self.q_phantomjs.get()
            d.quit()

        for i in range(self.q_phantomjs.qsize()):
            t = threading.Thread(target=close_threading)
            th.append(t)
        for i in th:
            i.start()
        for i in th:
            i.join()


    def set_url_list(self):
        url_list = []
        year = 2017
        month = 7
        day = 10
        url_patten = "http://news.10jqka.com.cn/cjzx_list/"
        for i in range(3):
            month_str = str(month)
            if month < 10:
                month_str = "0" + month_str
            day_str = str(day)
            if day < 10:
                day_str = "0" + day_str
            year_str = str(year)
            url_list.append(url_patten + year_str + month_str + day_str + "/")
            day = day+1
            if month in [1,3,5,7,8,10,12] and day > 31:
                day = 1
                month = month+1
            elif month in [4,6,9,11] and day > 30:
                day = 1
                month = month+1
            elif month==2 and year%4!=0 and day > 28:
                day = 1
                month = month+1
            if month == 13:
                month = 1
                year = year+1
        return url_list

    def get_today_url_by_list(self):
        url_patten = "http://news.10jqka.com.cn/cjzx_list/"
        now = datetime.datetime.now().strftime('%Y%m%d')
        url = url_patten + now + "/"
        return [url]

    def get_date(self,start,end):
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

if __name__ == "__main__":
    '''
    用法：
    1.实例化类
    2.运行open_phantomjs 开启phantomjs进程
    3.运行getbody函数，传入url
    4.运行close_phantomjs 关闭phantomjs进程
    '''
    cur = conphantomjs()
    conphantomjs.phantomjs_max = 10
    cur.open_phantomjs()
    print("phantomjs num is ", cur.q_phantomjs.qsize())

    # url_list = ["http://www.baidu.com"] * 50

    url_list = cur.set_url_list()


    th = []
    for i in url_list:
        t = threading.Thread(target=cur.getbody, args=(i,))
        th.append(t)
    for i in th:
        i.start()
    for i in th:
        i.join()
    cur.close_phantomjs()
    print("phantomjs num is ", cur.q_phantomjs.qsize())
