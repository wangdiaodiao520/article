import datetime
import time

#from qczj.qczj_html import main_qczj
import wz



#定时启动时间为每小时的59分，在当前时间间隔内最后一分拿到当前时间点，采集此时间内文章
hour = datetime.datetime.now().hour
    
wz.main(hour)

    
