from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from lxml import etree
import datetime
import pymongo
import time
import re


hour = datetime.datetime.now().hour
#声明数据库
client = pymongo.MongoClient(host='localhost',port=27017)
db = client.wz
collection = db.wz
#声明浏览器
#opt = webdriver.FirefoxOptions()
#opt.set_headless()
driver = webdriver.Firefox()#options=opt)
#driver.set_page_load_timeout(10)

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
def parse_table(html,hour):
    #获得文章链接
    hrefs = html.xpath('//ul[@class="article"]/li[@data-artidanchor]/a/@href')
    #构造时间范围
    start = str(hour)
    end = str(hour + 1)
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
            driver.get(url)
            html_page = etree.HTML(driver.page_source)
        else:
            pass
        #获取发布时间
        date = ''.join(html_page.xpath('//*[@id="articlewrap"]/div[1]/span[1]/text()')).strip()[-5:]
        #获取文章类别
        clas = ''.join(html_page.xpath('//*[@id="articleContent"]/p[1]/a/text()'))
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
        #时间不符合，略过
        elif end <= date:
            pass
        #时间不符合，打断循环
        else:
            break

#解析文章
def parse_page(html_page):
    #获得需求数据
    qczj = {}
    qczj['title'] = ''.join(html_page.xpath('//*[@id="articlewrap"]/h1/text()'))
    author = ''.join(html_page.xpath('//*[@id="articlewrap"]/div[1]/div/a/text()'))
    qczj['author'] = author
    qczj['date'] = ''.join(html_page.xpath('//*[@id="articlewrap"]/div[1]/span[1]/text()'))
    qczj['source'] = ''.join(html_page.xpath('//*[@id="articlewrap"]/div[1]/span[3]/a/text()'))
    #获得文章主题
    article_frame = html_page.xpath('//*[@id="articleContent"]/child::*')[:-2]
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
    

def main_qczj(hour):
    html = get_table()
    parse_table(html,hour)
    driver.quit()

if __name__ == "__main__":
    main_qczj(hour)
    
