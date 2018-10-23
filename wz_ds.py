from selenium.common.exceptions import TimeoutException
from html.parser import HTMLParser
from selenium import webdriver
from lxml import etree
import datetime
import pymysql
import time
import re
import sys


#声明数据库
#db = pymysql.connect(host='localhost',port=3306, user='debian-sys-maint',password='LLmPbgeHXb3YlGbx',db='article',charset='utf8')
#cursor = db.cursor()
#client = pymongo.MongoClient(host='localhost',port=27017)
#db = client.wz
#collection = db.test
#声明浏览器
#opt = webdriver.FirefoxOptions()
#opt.set_headless()
#driver = webdriver.Firefox(options=opt)
#driver = webdriver.Chrome()
driver = webdriver.Firefox()
driver.set_page_load_timeout(3)

###############################################################################

#获取文章列表页文章连接    
def zj_get_table():
    #列表页连接
    url = 'https://www.autohome.com.cn/all/#pvareaid=3311229'
    try:
        driver.get(url)
    except TimeoutException:
        pass
    #下拉三次
    js="var q=document.documentElement.scrollTop=100000"
    for i in range(3):
        driver.execute_script(js)
        time.sleep(1)
    #获得列表页代码
    html = etree.HTML(driver.page_source)
    return html

#解析列表页，解析文章链接
def zj_parse_table(html,hour):
    #获得文章链接
    hrefs = html.xpath('//ul[@class="article"]/li[@data-artidanchor]/a/@href')
    #构造时间范围
    start = hour - 1
    end = hour
    #请求单个文章链接
    for href in hrefs:
        #构造url
        url = 'https:' + href
        #请求文章链接并获得文章页代码
        try:
            driver.get(url)
        except TimeoutException:
            html_page = etree.HTML(driver.page_source)
        else:
            html_page = etree.HTML(driver.page_source)
        #文章内容判断
        #判断是否是特殊页面
        if html_page.xpath('//*[@id="fanhui2"]/text()'):
            #如果是，返回普通页面并获得页面代码
            url = ''.join(html_page.xpath('//*[@id="fanhui2"]/@href'))
            try:
                driver.get(url)
            except TimeoutException:
                html_page = etree.HTML(driver.page_source)
            else:
                html_page = etree.HTML(driver.page_source)
        else:
            pass
        #获取发布时间
        date = int(''.join(html_page.xpath('//section[@class="article-detail"]/header/div[@class="user"]/div[@class="date"]/text()')).strip()[-5:-3])
        #获取文章类别
        clas = ''.join(html_page.xpath('//section[@class="article-detail"]/div[@class="details"]/p[1]/a/text()'))
        #判断是否为多页
        page = ''.join(html_page.xpath('//section[@class="article-detail"]/section[@class="athm-page"]/a/text()'))
        point_2 = '一页' in page
        #判断文章是否是游记类型
        point = '游记' in clas
        #当前文章发布时间是否为定义时间内
        if start == date:
            #如时间是，并且文章不为游记类且单页，解析文章
            if point==False and point_2==False:
                zj_parse_page(html_page)
            #类别不符合，pass
            else:
                pass
        #时间不符合，略过
        elif end <= date:
            pass
        #时间不符合，打断循环
        else:
            break
        time.sleep(1)

#解析文章
def zj_parse_page(html_page):
    #获得需求数据
    title = ''.join(html_page.xpath('//section[@class="article-detail"]/header[@class="header"]/h1/text()')).strip()
    author = ''.join(html_page.xpath('//section[@class="article-detail"]/header[@class="header"]/div[@class="user"]/div[@class="name"]/a/text()')).strip()
    date = ''.join(html_page.xpath('//section[@class="article-detail"]/header[@class="header"]/div[@class="user"]/div[@class="date"]/text()')).strip()
    date = re.sub('年','-',date,re.S)
    date = re.sub('月','-',date,re.S)
    date = re.sub('日','',date,re.S)
    timeArray = time.strptime(date, "%Y-%m-%d %H:%M")
    timestamp = time.mktime(timeArray)
    date_c = int(timestamp)
    source = '汽车之家'
    #获得文章主题
    article_frame = html_page.xpath('//section[@class="article-detail"]/div[@class="details"]/child::*')
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
    h = HTMLParser()
    txt = h.unescape(txt)
    html = re.sub('src=\"//','src=\"https://',re.sub('<a.*?href.*?target=.*?>','',txt,re.S),re.S)
    save(title,author,date_c,source,html)

###############################################################################

#获取文章列表页文章连接    
def yc_get_table():
    #列表页连接
    url = 'http://news.bitauto.com/'
    try:
        driver.get(url)
    except TimeoutException:
        pass
    #下拉三次
    js="var q=document.documentElement.scrollTop=100000"
    for i in range(3):
        driver.execute_script(js)
        time.sleep(1)
    #获得列表页代码
    html = etree.HTML(driver.page_source)
    return html

#解析列表页，解析文章链接
def yc_parse_table(html,hour):
    #获得文章链接
    hrefs = html.xpath('//div[@class="card-list-box clearfix"]/div/div/a/@href')
    #构造时间范围
    start = hour - 1
    end = hour 
    #请求单个文章链接
    for href in hrefs:
        #构造url
        url = href
        #请求文章链接并获得文章页代码
        try:
            driver.get(url)
        except TimeoutException:
            html_page = etree.HTML(driver.page_source)
        else:
            html_page = etree.HTML(driver.page_source)
        #文章内容判断
        #获取发布时间
        date = int(''.join(html_page.xpath('//*[@id="content_bit"]/article/div[1]/div[2]/div/span[1]/text()')).strip()[-5:-3])
        #章发布时间是否为定义时间内
        if start == date:
            yc_parse_page(html_page)
        #时间不符合，略过
        elif end <= date:
            pass
        #时间不符合，打断循环
        else:
            break          
        time.sleep(1)

#解析文章
def yc_parse_page(html_page):
    #获得需求数据
    title = ''.join(html_page.xpath('//*[@id="content_bit"]/article/h1/text()')).strip()
    author = ''.join(html_page.xpath('//*[@id="content_bit"]/article/div[1]/div[1]/div[2]/p/a/text()')).strip()
    date = ''.join(html_page.xpath('//*[@id="content_bit"]/article/div[1]/div[2]/div/span[1]/text()')).strip()
    date = re.sub('年','-',date,re.S)
    date = re.sub('月','-',date,re.S)
    date = re.sub('日','',date,re.S)
    timeArray = time.strptime(date, "%Y-%m-%d %H:%M")
    timestamp = time.mktime(timeArray)
    date_c = int(timestamp)
    source = ''.join(html_page.xpath('//*[@id="content_bit"]/article/div[1]/div[2]/div/a/text()')).strip()
    #获得文章框
    article_frame = html_page.xpath('//*[@id="openimg_articlecontent"]/child::*')
    article_list = []
    #获得文章html
    for article_p in article_frame:
        pp = ''.join(article_p.xpath('@style')) == 'position: relative;'
        if pp == True:
            pass
        else: 
            string = etree.tostring(article_p).decode('utf-8')
            article_list.append(string)
    txt = ''.join(article_list)
    h = HTMLParser()
    txt = h.unescape(txt)
    txt = re.sub('<a.*?href.*?>','',txt,re.S)
    print(article_frame)

###############################################################################

#保存
def save(title,author,date_c,source,html):
    sql = "INSERT IGNORE INTO czs_article(title,user_name,created_at,source,content) VALUES('%s','%s','%s','%s','%s');"%(title,author,date_c,source,pymysql.escape_string(html))
    cursor.execute(sql)
    db.commit()
       
def main_qczj(hour):
    html = zj_get_table()
    zj_parse_table(html,hour)

def main_yc(hour):
    html = yc_get_table()
    yc_parse_table(html,hour)

def main(hour):
    #main_qczj(hour)
    main_yc(hour)
    driver.quit()
    
if __name__ == "__main__":
    #hour = datetime.datetime.now().hour
    hour = 11
    main(hour)
    sys.exit()



















    
