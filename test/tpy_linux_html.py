from bs4 import BeautifulSoup
from lxml import etree
import datetime
import pymysql
import requests
import time
import json
import re
import sys


#声明数据库
#db = pymysql.connect(host='localhost',port=3306, user='debian-sys-maint',password='LLmPbgeHXb3YlGbx',db='article',charset='utf8')
#cursor = db.cursor()
#浏览器头
head = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    }
    
#文章列表页函数
def get_url():
    #请求列表页，并编码解析
    url = 'https://www.pcauto.com.cn/news/'
    response = requests.get(url,headers=head)
    soup = BeautifulSoup(response.content,"lxml",from_encoding="GB18030")
    #四个文章块节点
    frames = soup.select('.pic-txt-list')
    #文章连接列表
    urls = []
    #偶尔会得到一个空的frame，判定并忽略报错
    try:
        for frame in frames:
            #文章块内第一块判断
            #是否为连载，是判断是否结尾，是拿到连接，否pass
            title_t =  frame.select('div dl dt a')[0].get_text().strip()
            if ("(上)" in title_t) or ("(中)" in title_t):
                pass
            else:
                urls.append(frame.select('div dl dt a')[0]['href'])            
            #文章块内第二块判断
            #拿到连接列表
            url_li_s = frame.select('ul li')
            for url_li in url_li_s:
                #是否为连载，是判断是否结尾，是拿到连接，否pass
                title_t =  url_li.select('a')[0].get_text().strip()
                if ("(上)" in title_t) or ("(中)" in title_t):
                    pass
                else:             
                    urls.append(url_li.select('a')[0]['href'])
    except IndexError:
        pass
    return urls

#文章页解析函数    
def get_page(urls,hour):
    #构造抓取范围
    start = int(hour - 1)
    end = int(hour)
    #得到当前日期
    date_p = time.strftime("%Y-%m-%d",time.localtime()) 
    #迭代每一个文章链接
    for url in urls:
        #判定文章链接是否自带http，如有下一步，如无加入下一步
        if 'http' in url:
            pass
        else:
            url = 'https:' + url
        #请求文章，并解析
        response = requests.get(url,headers=head)
        soup = BeautifulSoup(response.content,"lxml",from_encoding="GB18030")
        #请求状态判定
        if response.status_code == 200:
            #当前文章发布日期
            date_all =  soup.select('#pubtime_baidu')[0].get_text().strip()
            date = date_all[:11]
            #判定文章是否为当天发布，如否过，如是进一步解析
            if date_p == date:
                #得到文章发布时间
                date_t = date_all[11:13]
                #判定文章时间
                if start <= date_t < end:
                    #判定文章是否为全页，是pass，否请求全页，并重定义soup
                    if soup.select('.pageViewGuidedd a'):
                        if "浏览全文" in soup.select('.pageViewGuidedd a')[0].get_text():
                            soup = BeautifulSoup((requests.get("https:" + soup.select('.pageViewGuidedd a')[0]['href'],headers=head)).content,"lxml",from_encoding="GB18030")
                        else:
                            pass
                    else:
                        pass
                    #日期、时间符合条件，且为全页，解析文章html
                    parse_page(soup)
                #用pass筛出时间不符合文章，不打断，因4块文章，时间排序非线性
                else:
                    pass
            #用pass筛出日期不符合文章，不打断，因4块文章，日期排序非线性
            else:
                pass
        else:
            pass
        
#解析文章函数
def parse_page(soup):
    title = soup.select('.artTit .tit')[0].get_text().strip()#标题
    author = soup.select('.artPic a span')[0].get_text().strip().replace("作者：","")#作者
    #得到发布时间，并构造时间戳
    date = soup.select('#pubtime_baidu')[0].string
    date = re.sub('年','-',date,re.S)
    date = re.sub('月','-',date,re.S)
    date = re.sub('日','',date,re.S)
    timeArray = time.strptime(date, "%Y-%m-%d %H:%M")
    timestamp = time.mktime(timeArray)
    date_c = int(timestamp)
    source = soup.select('#source_baidu')[0].get_text().strip().replace("来源：","")#来源
    


if __name__ == "__main__":
    hour = 25
    urls = get_url()
    get_page(urls,hour)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    