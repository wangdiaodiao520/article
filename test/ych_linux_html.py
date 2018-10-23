from bs4 import BeautifulSoup
from lxml import etree
import datetime
import pymysql
import requests
import time
import json
import re


#声明数据库
#db = pymysql.connect(host='localhost',port=3306, user='debian-sys-maint',password='LLmPbgeHXb3YlGbx',db='article',charset='utf8')
#cursor = db.cursor()
#headers
head = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    }

#文章列表页链接函数
def get_url():
    url = 'http://hao.yiche.com/'
    response = requests.get(url,headers=head)
    soup = BeautifulSoup(response.text,'lxml')
    urls = soup.select('.content h4 a')
    return urls

#文章判断函数    
def get_page(urls,hour):
    start = int(hour - 1)
    end = int(hour)
    for url in urls:
        url = url['href']
        #是否为视频
        if "vplay" in url:
            pass
        else:
            response = requests.get(url,headers=head)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text,'lxml')  
                #是否有阅读全文按钮
                if soup.select('.page-new-sty div a'):
                    response = requests.get(soup.select('.page-new-sty div a')[-1]['href'],headers=head)
                    soup = BeautifulSoup(response.text,'lxml')
                else:
                    pass
                #发布时间
                try:
                    date = soup.select('.t-box span')[1].string
                except IndexError:
                    date = '25:00'
                point_date = int(date[-5:-3]) 
                #判断发布时间
                if 0 <= point_date < end:
                    parse_page(soup)
                elif end <= point_date:
                    pass
                else:
                    break
            else:
                pass
 
#文章解析函数 
def parse_page(soup):
    title = soup.select('.tit-h1')[0].get_text().strip()#题目
    author = soup.select('.p-n a')[0].get_text().strip()#作者
    date = soup.select('.t-box span')[1].string#时间，并转成时间戳
    date = re.sub('年','-',date,re.S)
    date = re.sub('月','-',date,re.S)
    date = re.sub('日','',date,re.S)
    timeArray = time.strptime(date, "%Y-%m-%d %H:%M")
    timestamp = time.mktime(timeArray)
    date_c = int(timestamp)
    source = "易车" + author#来源
    article_str = str(soup.select('#openimg_articlecontent')[0])[78:-17]#文章html
    '''
    if 'hr' in article_str:
        article_hr = soup.select('#openimg_articlecontent hr')
        if len(article_hr) == 1:
                                     #<hr.*?p>.*?p>
            article_str = re.sub('<hr/>.*?p>.*?p>','',article_str,re.S)
        elif len(article_hr) == 2:
            article_str = re.sub('<hr.*?<hr/>','',article_str,re.S)
        elif len(article_hr) > 2:
            article_str = re.sub('<p.*?nbsp.*?p>','',re.sub('<hr/>','',article_str,re.S),re.S)
            article_str = article_str[:-198]
        else:
            article_str = article_str
    else:
        article_str = article_str
    if 'height:173' in article_str:
        article_im = str(soup.select('#openimg_articlecontent p')[-1])
        article_str = article_str.replace(article_im,'')
    else:
        article_str = article_str
    if '延伸阅读' in article_str:
        article_str = re.sub('<p><span style="text-indent.*?p>.*?p>','',article_str,re.S)
    else:
        article_str = article_str
    article_str = re.sub('<a.*?href.*?>','',article_str,re.S)
    article = re.sub('<a.*?href.*?>','',article_str,re.S) +"<div class="lef-box">内容仅代表作者观点</div>"
    '''
    article = article_str + '<div class="lef-box">内容仅代表作者观点</div>'
    print(title,author,date_c,source,article)     
 
#保存函数 
def save(title,author,date,source,article):
    sql = "INSERT IGNORE INTO czs_article(title,user_name,created_at,source,content) VALUES('%s','%s','%s','%s','%s');"%(title,author,date_c,source,pymysql.escape_string(article))
    cursor.execute(sql)
    db.commit()
    
def main_ych(hour):
    urls = get_url()
    get_page(urls,hour)             
        
        
if __name__ == "__main__":
    #hour = 18
    main_ych()