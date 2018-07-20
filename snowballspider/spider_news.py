# coding:utf-8
from urllib import request
import re
import json
import datetime
import os
from dbhelper import dbhelper


class Spider(object):
    coon = dbhelper()
    count_per_page = 20
    news_base_url = ['https://xueqiu.com/statuses/stock_timeline.json?symbol_id=','&count='+str(count_per_page)+'&source=%E8%87%AA%E9%80%89%E8%82%A1%E6%96%B0%E9%97%BB&page=']
    eg_symbol_id = 'SH600756'
    eg_page = '10'

    header = {
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
        'Cookie': 'device_id=da0f8307b45a89862f79ecb4e175993c; _ga=GA1.2.350845951.1531204868; s=e816b0zx53; __utmz=1.1531204902.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); aliyungf_tc=AQAAACBmU1pb0QIAZWev3mAEX0trvAaN; xq_a_token=7443762eee8f6a162df9eef231aa080d60705b21; xq_a_token.sig=3dXmfOS3uyMy7b17jgoYQ4gPMMI; xq_r_token=9ca9ab04037f292f4d5b0683b20266c0133bd863; xq_r_token.sig=6hcU3ekqyYuzz6nNFrMGDWyt4aU; Hm_lvt_1db88642e346389874251b5a1eded6e3=1531204867,1531204931,1531209438,1531359515; u=661531359514743; _gid=GA1.2.858583330.1531359515; __utmc=1; __utma=1.350845951.1531204868.1531359515.1531363195.4; __utmt=1; __utmb=1.2.10.1531363195; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1531364703'
    }

    def __init__(self,stock_index_list):
        self.stock_index_list = stock_index_list

    def get_news(self):
        all_stock_news_list = []
        for each_stock_id in self.stock_index_list:
            cur_stock_title_link_list = []
            cur_stock_json_list = []
            base_url = self.news_base_url[0] + 'SH' + str(each_stock_id) + self.news_base_url[1]
            first_page_json,max_page = self.get_first_page(base_url)
            cur_stock_json_list.append(first_page_json)

            # for i in range(2,max_page+1):
            #     url = base_url + str(i)
            #     try:
            #         page_json = self.get_json(url)
            #         cur_stock_json_list.append(page_json)
            #     except:
            #         pass

            for each_page in cur_stock_json_list:
                news_list = each_page['list']
                for each_news in news_list:
                    # text = each_news['text']
                    # timeBefore = each_news['timeBefore']
                    # content,time = data_preprocessing(text,timeBefore)
                    # ex = date_to_content_dict.get(time, '')
                    # date_to_content_dict[time] = ex + content
                    # print(content, time)

                    title = each_news['title']
                    link = each_news['quote_cards'][0]['target_url']
                    title_link_list = [title,link]
                    cur_stock_title_link_list.append(title_link_list)

            all_stock_news_list.append(cur_stock_title_link_list)
            # save_to_db(self.coon,cur_stock_title_link_list,each_stock_id)
        return all_stock_news_list

    def get_first_page(self,url):
        url = url + '1'
        first_page_json = self.get_json(url)
        return first_page_json,first_page_json['maxPage']

    def get_json(self,url):
        r = request.Request(url, headers=self.header)
        res = request.urlopen(r)
        re = res.read().decode('utf-8')
        print(re)
        json_obj = json.loads(re)
        return json_obj
        # print(json_obj['maxPage'])

def save_to_db(coon,dict,id):
    coon.open('stock')
    # 使用预处理语句创建表
    # sql = 'CREATE TABLE '+ str(id) +' (id INT NOT NULL AUTO_INCREMENT, date INT,value double,' \
    #                                 ' contents mediumtext CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,' \
    #                                 ' vector mediumtext CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,' \
    #                                 ' increasing INT ) ,' \
    #                                 ' ADD PRIMARY KEY (`id`)'

    coon.create(id)
    for key in dict:
        sql = 'insert into sh'+ str(id) +'(date,contents) VALUE ("' + key + '","' + dict[key] + '");'#TODO
        coon.insert(sql)
    coon.close()




def data_preprocessing(text,timeBefore):
    tags = re.compile('<a.*>',re.I)
    content = tags.sub('',text)
    now = datetime.datetime.now().strftime('%Y%m%d')
    date = ''
    if (timeBefore.find('前') != -1) or (timeBefore.find('天') != -1):
        date = now
    else:
        date_temp = timeBefore.split()[0]
        if len(date_temp.split('-')) == 3:
            date = date_temp.replace('-','')
        else:
            date = datetime.datetime.now().strftime('%Y') + date_temp.replace('-','')
    return content,date

def get_indexes(path):
    indexes = []
    for root, dirs, files in os.walk(path):
        # print(root)  # 当前目录路径
        # print(dirs)  # 当前路径下所有子目录
        print(files)  # 当前路径下所有非目录子文件
        for each in files:
            indexes.append(each.split('.')[0])

    return indexes




def main():
    # url = 'http://tieba.baidu.com/p/2256306796'
    # download(url)

    d = {'symbol_id': 'SH600756', 'count': '20', 'source': '%E8%87%AA%E9%80%89%E8%82%A1%E6%96%B0%E9%97%BB','page':'10'}
    # r = requests.get('https://xueqiu.com/statuses/stock_timeline.json', params=d)
    header = {
'Accept': 'application/json, text/plain, */*',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
'Cookie': 'device_id=da0f8307b45a89862f79ecb4e175993c; _ga=GA1.2.350845951.1531204868; s=e816b0zx53; __utmz=1.1531204902.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); aliyungf_tc=AQAAACBmU1pb0QIAZWev3mAEX0trvAaN; xq_a_token=7443762eee8f6a162df9eef231aa080d60705b21; xq_a_token.sig=3dXmfOS3uyMy7b17jgoYQ4gPMMI; xq_r_token=9ca9ab04037f292f4d5b0683b20266c0133bd863; xq_r_token.sig=6hcU3ekqyYuzz6nNFrMGDWyt4aU; Hm_lvt_1db88642e346389874251b5a1eded6e3=1531204867,1531204931,1531209438,1531359515; u=661531359514743; _gid=GA1.2.858583330.1531359515; __utmc=1; __utma=1.350845951.1531204868.1531359515.1531363195.4; __utmt=1; __utmb=1.2.10.1531363195; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1531364703'
}
    r = request.Request('https://xueqiu.com/statuses/stock_timeline.json?symbol_id=SH600756&count=20&source=%E8%87%AA%E9%80%89%E8%82%A1%E6%96%B0%E9%97%BB&page=10', headers=header)
    res = request.urlopen(r)
    re = res.read().decode('utf-8')
    print(re)
    json_obj = json.loads(re)
    # print(json_obj['maxPage'])
    first = json_obj['list'][0]
    contents = first['text']
    time = first['timeBefore']

    print()



if __name__ == '__main__':
    # save_to_db(dbhelper(),{},1)

    # indexes = get_indexes('C:/Users/wzy/Desktop/暑期实训/data/上证A股/上证A股')
    spider = Spider(['000001'])
    lists = spider.get_news()
    print(lists)
    # data_preprocessing('中国网财经7月12日讯 浦发银行12日在京正式推出业内首个API Bank无界开放银行，这是该行建设一流数字生态银行的一项重大工程。浦发银行API Bank无界开放银行将通过API架构驱动，将场景金融融入互联网生态，围绕客户需求和体... <a href="http://finance.sina.com.cn/roll/2018-07-12/doc-ihfefkqr1162079.shtml" title="http://finance.sina.com.cn/roll/2018-07-12/doc-ihfefkqr1162079.shtml" target="_blank" class="status-link">网页链接</a>','今天 08:31')
