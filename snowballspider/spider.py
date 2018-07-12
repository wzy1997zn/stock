# coding:utf-8
from urllib import request
import re
import json

# 根据url获取网页html内容
def getHtmlContent(url):

    d = {'key1': 'value1', 'key2': 'value2'}
    r = request.get('http://httpbin.org/get', params=d)
    print(r)

# 从html中解析出所有jpg图片的url
# 百度贴吧html中jpg图片的url格式为：<img ... src="XXX.jpg" width=...>
def getJPGs(html):
    # 解析jpg图片url的正则
    jpgReg = re.compile(r'<img.+?src="(.+?\.jpg)" width')  # 注：这里最后加一个'width'是为了提高匹配精确度
    # 解析出jpg的url列表
    jpgs = re.findall(jpgReg, html)
    return jpgs

# 用图片url下载图片并保存成制定文件名
def downloadJPG(imgUrl, fileName):
    urllib.urlretrieve(imgUrl, fileName)



# 封装：从百度贴吧网页下载图片
def download(url):
    html = getHtmlContent(url)
    jpgs = getJPGs(html)

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
    rjson = json.dumps(re, ensure_ascii=False)
    # print(json.dumps(re, sort_keys=True, indent=4, separators=(',', ': ')))
    json_obj = json.loads(re)
    print(json_obj['count'])


if __name__ == '__main__':
    main()