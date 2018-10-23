from bs4 import BeautifulSoup
from lxml import etree
import datetime
import pymysql
import requests
import time
import json
import re
import sys


#db = pymysql.connect(host='localhost',port=3306, user='debian-sys-maint',password='LLmPbgeHXb3YlGbx',db='article',charset='utf8')
#cursor = db.cursor()

head = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    }
def get_url():
    url = 'http://news.bitauto.com/views3/news/tagnewsjsonlist?cid=1088&callback=getTagNewsData&pageIndex=1'
    response = requests.get(url,headers=head)
    js = json.loads(str(response.text[15:-1]))
    urls = [i.get('url') for i in js]
    return urls
    
def get_page(urls,hour):
    start = int(hour)
    end = int(hour+1)
    for url in urls:
        response = requests.get(url,headers=head)
        soup = BeautifulSoup(response.text,'lxml')
        '''
        if soup.select('.page-new-sty div a'):
            print(soup.select('.page-new-sty div a')[-1].get_text().strip())
            response = requests.get(soup.select('.page-new-sty div a')[-1][href],headers=head)
            soup = BeautifulSoup(response.text,'lxml')
        else:
            pass
       '''
        date = soup.select('.t-box span')[0].string
        point_date = int(date[-5:-3])
        if start <= point_date < end:
            parse_page(soup)
        elif end <= point_date:
            pass
        else:
            break

def parse_page(soup):
    title = soup.select('.tit-h1')[0].get_text().strip()
    author = soup.select('.p-n a')[0].get_text().strip()
    date = soup.select('.t-box span')[0].string
    date = re.sub('年','-',date,re.S)
    date = re.sub('月','-',date,re.S)
    date = re.sub('日','',date,re.S)
    imeArray = time.strptime(date, "%Y-%m-%d %H:%M")
    timestamp = time.mktime(timeArray)
    date_c = int(timestamp)
    source = soup.select('.t-box a')[0].get_text().strip()
    article_str = str(soup.select('#openimg_articlecontent')[0])[78:-17]
    if 'hr' in article_str:
        article_hr = soup.select('#openimg_articlecontent hr')
        if len(article_hr) == 1:
            article_str = re.sub('<hr>.*?','',article_str,re.S)
        elif len(article_hr) == 2:
            article_str = re.sub('<hr>.*?<hr>','',article_str,re.S)
        elif len(article_hr) > 2:
            article_str = re.sub('<p>&nbsp;</p>','',re.sub('<hr>','',article_str,re.S),re.S)
            article_str = article_str[:-198]
        else:
            pass
    else:
        pass
    article = re.sub('<a.*?href.*?title.*?>','',article_str,re.S)
    print(title,author,date_c,source,article)
   
def save(title,author,date,source,article):
    sql = "INSERT IGNORE INTO czs_article(title,user_name,created_at,source,content) VALUES('%s','%s','%s','%s','%s');"%(title,author,date_c,source,pymysql.escape_string(article))
    cursor.execute(sql)
    db.commit()
    
  
    
if __name__ == "__main__":
    hour = datetime.datetime.now().hour
    urls = get_url()
    get_page(urls,hour)
    
