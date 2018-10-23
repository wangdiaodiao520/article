from html.parser import HTMLParser
from lxml import etree
import datetime
import pymysql
import requests
import time
import re


#db = pymysql.connect(host='localhost',port=3306, user='debian-sys-maint',password='LLmPbgeHXb3YlGbx',db='article',charset='utf8')
#cursor = db.cursor()

head = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    }
def get_url():
    url = 'https://www.autohome.com.cn/all/#pvareaid=3311229'
    response = requests.get(url,headers=head)
    page = etree.HTML(response.text)
    urls = page.xpath('//ul[@class="article"]/li/a/@href')
    return urls
    
def get_page(urls,hour):
    start = int(hour-1)
    end = int(hour)
    for l in urls:
        url = 'https:' + l
        response = requests.get(url,headers=head)
        if response.status_code == 200:            
            html = etree.HTML(response.text)           
            if html.xpath('//a[@id="fanhui2"]') and "返回" in html.xpath('//a[@id="fanhui2"]/text()')[0]:
                id = re.findall('attr.*?_articleurl.*? "(.*?)"',response.text,re.S)[0]
                url = url[:-16] + id
                response = requests.get(url,headers=head)         
                html = etree.HTML(response.text)
            else:
                pass
        else:
            pass
        point_cls = "游记" in ''.join(html.xpath('//div[@class="breadnav fn-left"]/a//text()'))
        point_page = "阅读全文" in ''.join(html.xpath('//span[@class="readall"]/a/text()'))
        point_date =int(''.join(html.xpath('//span[@class="time"]/text()')).strip()[:20].strip()[-5:-3])
        if 0 <= point_date < end:
            if point_cls==False and point_page==False:
                parse_page(html)
            else:
                pass
        elif end <= point_date:
            pass
        else:
            break
         
def parse_page(html):
    title = ''.join(html.xpath('//div[@id="articlewrap"]/h1/text()')).strip()
    author = ''.join(html.xpath('//div[@class="article-info"]/div/a/text()')).strip()
    date = ''.join(html.xpath('//span[@class="time"]/text()')).strip()[:20].strip()
    date = re.sub('年','-',date,re.S)
    date = re.sub('月','-',date,re.S)
    date = re.sub('日','',date,re.S)
    timeArray = time.strptime(date, "%Y-%m-%d %H:%M")
    timestamp = time.mktime(timeArray)
    date_c = int(timestamp)
    source = ''.join(html.xpath('//span[@class="source"]/a/text()')).strip()
    article_frame = html.xpath('//div[@id="articleContent"]/child::*')
    article_list = []
    for article_p in article_frame:
        judge_end = author in (''.join(article_p.xpath('string()')))
        if judge_end == True:
            string = etree.tostring(article_p).decode('utf-8')
            article_list.append(string)
            break
        else:
            string = etree.tostring(article_p).decode('utf-8')
            article_list.append(string)
    txt = ''.join(article_list)
    h = HTMLParser()
    txt = h.unescape(txt)
    article = re.sub('src=\"//','src=\"https://',re.sub('<a.*?href.*?target=.*?>','',txt,re.S),re.S)
    print(title)#,author,date_c,source,article)

def save(title,author,date,source,article):
    sql = "INSERT IGNORE INTO czs_article(title,user_name,created_at,source,content) VALUES('%s','%s','%s','%s','%s');"%(title,author,date_c,source,pymysql.escape_string(article))
    cursor.execute(sql)
    db.commit()    

def main_qczj(hour):
    urls = get_url()
    get_page(urls,hour)
    
if __name__ == "__main__":
    hour = 25
    main_qczj(hour)
 
    
