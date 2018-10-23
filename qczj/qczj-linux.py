from selenium.webdriver.common.by import By
from selenium import webdriver
from lxml import etree
import datetime
import pymongo
import time
import re

#声明数据库
client = pymongo.MongoClient(host='192.168.3.199',port=27017)
db = client.wz
collection = db.qczj
#声明浏览器
driver = webdriver.Chrome()

#获取当前时间
def get_time():
    hour = datetime.datetime.now().hour
    return hour

#获取文章列表页文章连接    
def get_table():
    #列表页连接
    url = 'https://www.autohome.com.cn/all/#pvareaid=3311229'
    driver.get(url)
    #下拉三次
    js="var q=document.documentElement.scrollTop=100000"
    for i in range(3):
        driver.execute_script(js)
        time.sleep(1)
    #获得列表页代码
    html = etree.HTML(driver.page_source)
    return html

#解析列表页，解析文章链接
def parse_table(html):
    #获得文章链接
    hrefs = html.xpath('//ul[@class="article"]/li[@data-artidanchor]/a/@href')
    #构造时间范围
    start = str(get_time())
    end = str(int(start) + 1)
    #请求单个文章链接
    for href in hrefs:
        #构造url
        url = 'https:' + href.replace('//www','m')
        #请求文章链接并获得文章页代码
        driver.get(url)
        html_page = etree.HTML(driver.page_source)
        #文章内容判断
        #获取发布时间
        date = str(''.join(html_page.xpath('/html/body/section[1]/section[5]/header/div/div[3]/text()')).strip()[-5:])
        #获取文章类别
        clas = ''.join(html_page.xpath('/html/body/section[1]/section[5]/div[3]/p[1]/a[1]/text()'))
        #判断文章是否是游记类型
        point = '游记' in clas
        #当前文章发布时间是否为定义时间内
        if start <= date <end:
            #如时间是，并且文章不为游记类，解析文章
            if point==False:
                parse_page(html_page)
            #类别不符合，pass
            else:
                pass
        #时间不符合，打断循环
        else:
            break

#解析文章
def parse_page(html_page):
    #获得需求数据
    qczj = {}
    qczj['title'] = ''.join(html_page.xpath('/html/body/section[1]/section[5]/header/h1/text()'))
    author = ''.join(html_page.xpath('/html/body/section[1]/section[5]/header/div/div[2]/a/text()'))
    qczj['author'] = author
    qczj['date'] = ''.join(html_page.xpath('/html/body/section[1]/section[5]/header/div/div[3]/text()'))
    qczj['source'] = '汽车之家'
    #获得文章主题
    article_frame = html_page.xpath('/html/body/section/section/div[@class="details"]/child::*')[:-2]
    article_list = []
    #判断文章内容
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
    qczj['html'] = re.sub('href.*?"','',txt,re.S)
    save(qczj)

#保存
def save(qczj):
    collection.insert_one(qczj)
    

def main():
    html = get_table()
    parse_table(html)

if __name__ == "__main__":
    main()
