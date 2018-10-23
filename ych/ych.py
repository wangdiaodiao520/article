from selenium.common.exceptions import TimeoutException
from html.parser import HTMLParser
from selenium import webdriver
from lxml import etree
import datetime
import requests
import pymysql
import time
import sys
import re


url = 'http://hao.yiche.com/article/articlelist?pageindex={offset}&pagesize=20&_={time_c}'

#构造url，1构造offset，2构造时间戳，时间戳为当前时间-8小时

def get_time():
    t = int((str(time.time()).replace('.',''))[:-3])
    time = t
    return time

def 
    
    
