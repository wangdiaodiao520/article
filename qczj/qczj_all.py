from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from lxml import etree
import datetime
import pymysql
import pymysql
import time
import re


#声明数据库
#client = pymongo.MongoClient(host='localhost',port=27017)
#db = client.wz
#collection = db.test
db = pymysql.connect(host='localhost',port=3306, user='root',password='wangyunlong',db='article',charset='utf8')
cursor = db.cursor()

#声明浏览器
#opt = webdriver.FirefoxOptions()
#opt.set_headless()
#driver = webdriver.Firefox(options=opt)
driver = webdriver.Chrome()
#driver = webdriver.Firefox()
#driver.set_page_load_timeout(10)

#获取文章列表页文章连接    
def get_table(offset):
    #列表页连接
    url_base = 'https://www.autohome.com.cn/all/{offset}/#liststart'
    if offset == 1:
        url = url_base.format(offset=offset)
        driver.get(url)
        #下拉三次
        js="var q=document.documentElement.scrollTop=100000"
        for i in range(3):
            driver.execute_script(js)
            time.sleep(1)
            #获得列表页代码
            html = etree.HTML(driver.page_source)
            return html
                 
    elif offset > 1:
        url = url_base.format(offset=offset)
        driver.get(url)
        html = etree.HTML(driver.page_source)
        return html

#解析列表页，解析文章链接
def parse_table(html):
    #获得文章链接
    hrefs = html.xpath('//*[@id="auto-channel-lazyload-article"]/ul/li/a/@href')
    #请求单个文章链接
    for href in hrefs:
        #构造url
        url = 'https:' + href
        #请求文章链接并获得文章页代码
        driver.get(url)
        html_page = etree.HTML(driver.page_source)
        #文章内容判断
        #判断是否是特殊页面
        if etree.HTML(driver.page_source).xpath('//*[@id="fanhui2"]/text()'):
            #如果是，返回普通页面并获得页面代码
            url = ''.join(html_page.xpath('//*[@id="fanhui2"]/@href'))
            driver.get(url)
            html_page = etree.HTML(driver.page_source)
        else:
            pass
        #获取文章类别
        clas = ''.join(html_page.xpath('//*[@id="articleContent"]/p[1]/a/text()'))
        page = ''.join(html_page.xpath('//*[@id="articlewrap"]/div[6]/div[2]/text()'))
        point_2 = '翻页' in page
        #判断文章是否是游记类型
        point_1 = '游记' in clas
        #文章不为游记类，解析文章
        if point_1 == False and point_2 == False:
            parse_page(html_page)
        #类别不符合，pass
        else:
            pass       
        time.sleep(1)

#解析文章
def parse_page(html_page):
    #获得需求数据
    title = ''.join(html_page.xpath('//*[@id="articlewrap"]/h1/text()')).strip()
    author = ''.join(html_page.xpath('//*[@id="articlewrap"]/div[1]/div/a/text()')).strip()
    date = ''.join(html_page.xpath('//*[@id="articlewrap"]/div[1]/span[1]/text()')).strip()
    date = re.sub('年','-',date,re.S)
    date = re.sub('月','-',date,re.S)
    date = re.sub('日','',date,re.S)
    timeArray = time.strptime(date, "%Y-%m-%d %H:%M")
    timestamp = time.mktime(timeArray)
    date_c = int(timestamp)
    source = ''.join(html_page.xpath('//*[@id="articlewrap"]/div[1]/span[3]/a/text()')).strip()
    #获得文章主题
    article_frame = html_page.xpath('//*[@id="articleContent"]/child::*')
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
    html = re.sub('href.*?"','',txt,re.S)
    save(title,author,date_c,source,html)
    

#保存
def save(title,author,date_c,source,html):
    print('正在保存：'+title)
    print(date_c)
    sql = "INSERT IGNORE INTO czs_article(title,user_name,time,source,content) VALUES('%s','%s','%s','%s','%s');"%(title,author,date_c,source,pymysql.escape_string(html))
    cursor.execute(sql)
    db.commit()

def main():
    for offset in range(1000):
        if offset <= 39:
            pass
        elif offset > 39 :
            print('正在采集第',offset,'页文章')
            html = get_table(offset)
            parse_table(html)
        
    
if __name__ == "__main__":
    main()
























