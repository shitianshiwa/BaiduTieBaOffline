import get_forum_list
import get_single_thread
import os
import sys
import shutil  # 文件操作
import logging  # 引入logging模块
import signal
import json
import time
import random
import threading
import re

from urllib.parse import unquote
from selenium import webdriver
from datetime import datetime
from bs4 import BeautifulSoup
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# from selenium import webdriver#没有使用谷歌的chromedriver，因为运行起来意外的慢,而且这个要求本机必须安装有注册的谷歌浏览器
#from selenium.webdriver.chrome.options import Options

# path =r'D:\python3.6.8\Scripts\chromedriver.exe'#有附带chromedriver.exe，但要注意selenium的版本号，这里为了支持PhantomJS.exe,压低版本了(2.53.6)
#chrome_options = Options()
# chrome_options.add_argument('--headless')

cookie = ""

# 第一步，创建一个logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Log等级总开关
# 第二步，创建一个handler，用于写入日志文件
rq = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
if os.path.exists("./logs") == False:
    os.makedirs("./logs")  # 创建logs文件夹用来存放日志
log_path = "./logs/"
log_name = log_path + rq + '.log'
logfile = log_name
fh = logging.FileHandler(logfile, mode='w')
fh.setLevel(logging.DEBUG)  # 输出到file的log等级的开关
# 第三步，定义handler的输出格式
formatter = logging.Formatter(
    "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)
# 第四步，将logger添加到handler里面
logger.addHandler(fh)
# 日志
#logger.debug('this is a logger debug message')
#logger.info('this is a logger info message')
#logger.warning('this is a logger warning message')
#logger.error('this is a logger error message')
#logger.critical('this is a logger critical message')
# python中logging日志模块详解
# https://www.cnblogs.com/xianyulouie/p/11041777.html

def getSource():
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Content-Encoding': 'gzip,deflate,br',
        'Content-Type': 'text/html; charset=utf-8',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
        'Cookie':''  
    }
    #使用copy()防止修改原代码定义dict
    cap = DesiredCapabilities.PHANTOMJS.copy() 
 
    for key, value in headers.items():
        cap['phantomjs.page.customHeaders.{}'.format(key)] = value
 
    # 不载入图片，爬页面速度会快很多
    cap["phantomjs.page.settings.loadImages"] = False
 
    driver = webdriver.PhantomJS(desired_capabilities=cap)#注意selenium的版本，高版本才支持chromedriver.exe.这里selenium==2.53.6
    return driver

def get_forum_list_call(url):
    #get_forum_list.browser = webdriver.Chrome(executable_path=path, options=chrome_options)
    get_forum_list.browser = getSource()
    get_forum_list.get_forum_list(url)
    get_forum_list.browser.service.process.send_signal(signal.SIGTERM)
    get_forum_list.browser.quit()


def kill_fake_thread(page_path, page, tid):
    with open(page_path, 'r', encoding='utf-8') as f:
        html_tree = BeautifulSoup(f, 'lxml')
    target_node = html_tree.find('a', href=str(page) + '_thread/' + tid + '/1.html')
    if target_node:
        for parent in target_node.parents:
            try:
                if 'j_thread_list' in parent['class']:
                    print('found you!')
                    parent.decompose()
                    found = True
                    break
            except BaseException:
                print('continue find!')
        if found:
            os.remove(page_path)
            with open(page_path, 'w', encoding='utf8') as f:
                f.write(str(html_tree))
            print('kill success!')
        else:
            print('!!!--error--!!! kill fail')
    else:
        print('!!!--error--!!! kill fail')


def get_threads_from_forum_page(url, cookie):
    get_single_thread.cookie = cookie
    info_file_name = unquote(
        unquote(get_forum_list.get_info_from_query(url, 'kw')))
    if os.path.exists(info_file_name + '/forum_base_info.json'):
        with open(info_file_name + '/forum_base_info.json', 'r', encoding='utf-8') as base_info_file:
            info = json.load(base_info_file)

        for page in range(1, info['total_page'] + 1):
            if os.path.exists(info_file_name + '/' + str(page) + '_thread/tid_info.json'):
                with open(info_file_name + '/' + str(page) + '_thread/tid_info.json', 'r',encoding='utf-8') as thread_info_file:
                    tid_info = json.load(thread_info_file)
                fid = tid_info['fid']
                for tid in tid_info['tid_list']:
                    if not os.path.exists(info_file_name + '/' + str(page) + '_thread/' + tid + '/1.html'):
                        try:
                            print('downloading thread ' +
                                  tid + ' in page' + str(page))
                            has_fake_thread = get_single_thread.get_single_thread(tid, fid, info['title'], str(page),True)
                            if has_fake_thread:
                                kill_fake_thread(info_file_name + '/' + str(page) + '.html', page, tid)
                            else:
                                shutil.copytree(tid, info_file_name + '/' + str(page) + '_thread/' + tid)
                                shutil.rmtree(tid)
                        except BaseException:
                            print('!!!--error--!!! download error tid:' + tid)
def start(url):
    print(datetime.now())
    get_forum_list_call(url)
    get_threads_from_forum_page(url, cookie)
    print(datetime.now())
    # Python3 正则表达式 | 菜鸟教程
    # https://www.runoob.com/python3/python3-reg-expressions.html
    #数字正则表达式 - miyaye - 博客园
    # https://www.cnblogs.com/webskill/p/7422876.html


def usejson():
    # 读取JSON配置文件
    filename = "./tieba.json"
    jsontemp = None
    f_obj = None
    try:
        f_obj = open(filename, encoding="utf-8")
        jsontemp = json.load(f_obj)
        f_obj.close()
    except Exception as err:  # FileExistsError or OSError:
        print("读取配置文件失败！ "+str(err))
        f_obj.close()
        exit()
    tiebalists = jsontemp['tieba']
    for x in tiebalists:
        if x[2] == True:
            print('链接:'+x[0]+',标题'+x[1])
            start(x[0])
        else:
            print('链接:'+x[0]+","+str(x[1])+",该贴吧不更新！")
        time.sleep(random.choice(range(5, 10)))
    '''
    https://www.cnblogs.com/lpdeboke/p/11414254.html
    python中json的基本使用
    https://jingyan.baidu.com/article/c74d6000d138fb0f6b595d45.html
    如何使用python的json模块从json文件读取数据听语音
    https://blog.csdn.net/weixin_41931602/article/details/80557416
    python ： 'gbk' codec can't decode byte 0xbe in position 18: illegal multibyte sequenc
    '''


def starttimer():
    global timer
    # timer.cancel()
    # print("2233")
    usejson()
    timeoutx = 7200+random.choice(range(1, 10))
    print("延迟："+str(timeoutx)+"s,下次运行时间："+str(time.strftime("%Y-%m-%d %H:%M:%S %a",time.localtime(time.time()+timeoutx))))#接收时间戳（1970纪元后经过的浮点秒数）并返回当地时间下的时间元组t（t.tm_isdst可取0或1，取决于当地当时是不是夏令时）。
    timer = threading.Timer(timeoutx, starttimer)
    timer.start()
    '''
    格式化日期
    我们可以使用 time 模块的 strftime 方法来格式化日期，：

    time.strftime(format[, t])
    实例演示：

    实例(Python 2.0+)
    #!/usr/bin/python
    # -*- coding: UTF-8 -*-
    
    import time
    
    # 格式化成2016-03-20 11:45:39形式
    print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
    
    # 格式化成Sat Mar 28 22:24:24 2016形式
    print time.strftime("%a %b %d %H:%M:%S %Y", time.localtime()) 
    
    # 将格式字符串转换为时间戳
    a = "Sat Mar 28 22:24:24 2016"
    print time.mktime(time.strptime(a,"%a %b %d %H:%M:%S %Y"))
    #Python 日期和时间 https://www.runoob.com/python/python-date-time.html
    '''


if __name__ == '__main__':
    # 不能设为None,会报错,有些地方需要登陆,所以cookie自己想办法弄吧(并不知道是那个cookie，也不知道怎么写，把自己的cookie弄上去也许号可能会没了)
    #global cookie
    #cookie =""
    try:  # 不用bat启动会报错所以，设计成这样，报错后默认使用单次运行
        if sys.argv[1] == "1":
            print("开始周期运行！")
            starttimer()  # 周期运行
        else:
            usejson()  # 单次运行
    except Exception as err:
        usejson()  # 单次运行
    '''
    # print(datetime.now())
    # get_forum_list_call(my_url)
    #get_threads_from_forum_page(my_url, my_cookie)
    # print(datetime.now())
    '''