from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from lxml import etree
import datetime
import pymongo
import time
import re


#声明数据库
client = pymongo.MongoClient(host='localhost',port=27017)
db = client.wz
collection = db.wz
#声明浏览器
#opt = webdriver.FirefoxOptions()
#opt.set_headless()
#driver = webdriver.Firefox(options=opt)
#driver.set_page_load_timeout(10)


#获取文章列表页文章连接    
def get_table():
    #列表页连接
    url = 'http://news.bitauto.com/'
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
def parse_table(html,hour):
    #获得文章链接
    hrefs = html.xpath('//div[@class="card-list-box clearfix"]/div/div/a/@href')
    #构造时间范围
    start = str(hour)
    end = str(hour + 1)
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
        if html_page.xpath('//*[@id="content_bit"]/article/div[1]/div[2]/div/span[1]/text()'):
            date = ''.join(html_page.xpath('//*[@id="content_bit"]/article/div[1]/div[2]/div/span[1]/text()')).strip()[-5:]
            #当前文章发布时间是否为定义时间内 
            if start <= date < end:
                parse_page_1(html_page)
            #时间不符合，略过
            elif end <= date:
                pass
            #时间不符合，打断循环
            else:
                break          
        else:
            date = ''.join(html_page.xpath('//*[@id="content_bit"]/article/div[1]/text()')).strip()[-5:]
            #当前文章发布时间是否为定义时间内
            if start <= date < end:
                parse_page_2(html_page)
            #时间不符合，略过
            elif end <= date:
                pass
            #时间不符合，打断循环
            else:
                break

#解析文章
def parse_page_1(html_page):
    #获得需求数据
    yc = {}
    yc['title'] = ''.join(html_page.xpath('//*[@id="content_bit"]/article/h1/text()')).strip()
    author = ''.join(html_page.xpath('//*[@id="content_bit"]/article/div[1]/div[1]/div[2]/p/a/text()')).strip()
    yc['author'] = author
    yc['date'] = ''.join(html_page.xpath('//*[@id="content_bit"]/article/div[1]/div[2]/div/span[1]/text()')).strip()
    yc['source'] = ''.join(html_page.xpath('//*[@id="content_bit"]/article/div[1]/div[2]/div/a/text()')).strip()
    #获得文章框
    article_frame = html_page.xpath('//*[@id="openimg_articlecontent"]/child::*')
    article_list = []
    #获得文章html
    for article_p in article_frame:
        string = etree.tostring(article_p).decode('utf-8')
        article_list.append(string)
    txt = ''.join(article_list)
    yc['html'] = re.sub('href.*?"','',txt,re.S)
    save(yc)
    
#解析文章
def parse_page_2(html_page):
    #获得需求数据
    yc = {}
    yc['title'] = ''.join(html_page.xpath('//*[@id="content_bit"]/article/h1/text()')).strip()
    author = ''.join(html_page.xpath('//*[@id="content_bit"]/article/div[6]/a/text()')).strip()
    yc['author'] = author
    yc['date'] = ''.join(html_page.xpath('//*[@id="content_bit"]/article/div[1]/text()')).strip()
    yc['source'] = ''.join(html_page.xpath('//*[@id="content_bit"]/article/div[1]/span[1]/a/text()')).strip()
    #获得文章框
    article_frame = html_page.xpath('//*[@id="openimg_articlecontent"]/child::*')
    article_list = []
    #获得文章html
    for article_p in article_frame:
        string = etree.tostring(article_p).decode('utf-8')
        article_list.append(string)
    txt = ''.join(article_list)
    yc['html'] = re.sub('href.*?"','',txt,re.S)
    save(yc)

#保存
def save(yc):
    collection.insert_one(yc)


def main_yc(hour,driver):
    html = get_table()
    parse_table(html,hour)
    driver.quit()
    
if __name__ == "__main__":
    main_yc(hour)

























        
