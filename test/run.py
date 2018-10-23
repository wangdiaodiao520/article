from yc_linux_html import main_yc
from qczj_linux_html import main_qczj

import sys
import threading
import datetime

hour = datetime.datetime.now().hour
def qczj():
    main_qczj(hour)
def yc():
    main_yc(hour)
    
thread_qczj = threading.Thread(target=qczj)
thread_yc = threading.Thread(target=yc)

thread_qczj.start()
thread_yc.start()
thread_yc.join()
thread_qczj.join()

sys.exit()
