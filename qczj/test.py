from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium import webdriver
from lxml import etree
import datetime
import pymysql
import time
import html
import re

driver = webdriver.Firefox()
driver.set_page_load_timeout(3)
try:
    driver.get('http://news.bitauto.com/xinchexiaoxi/20180921/1008287945.html')
except TimeoutException:
    html_page = etree.HTML(driver.page_source)




article_frame = html_page.xpath('//*[@id="openimg_articlecontent"]/child::*')
article_list = []
for article_p in article_frame:
    print(article_p)

