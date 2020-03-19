import zlib
import time
import sys
import os
import shutil  # 文件操作
import logging  # 引入logging模块
import random
import threading
import json
import hashlib
import socket
import urllib.error
import http.client
import re

from urllib import request as r
from bs4 import BeautifulSoup
from datetime import datetime

timeout = 31
socket.setdefaulttimeout(timeout)  # 这里对整个socket层设置超时时间。后续文件中如果再使用到socket，不必再设置
timer = None
'''
https://www.jianshu.com/p/d8585f0d9eb8
python 远程主机强迫关闭了一个现有的连接 socket 超时设置 errno 10054
'''
# 计划：整合下用户头像和贴子表情来减小体积(目前是采用部分下载webp格式来减小体积，用户头像和贴子表情要全部修改路径才能有效)，同时弄一个图片下载失败记录（目前是超时尝试下载第二次，第二次失败放弃下载，直接重下整个网页）
# http://imgsrc.baidu.com
# sss="https://imgsa.baidu.com/forum/w%3D580/sign=6a01e88176ec54e741ec1a1689399bfd/40155ed9bc3eb13578c4d204ab1ea8d3fd1f442a.jpg"
# sss2=sss.split("/")
# print(sss.find("none"))
# print(sss2)
# print(len(sss2))

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


pic_name = {}

# 浏览器的开发者工具network可以找到header


def req_maker(path):
    if path:
        req = r.Request(path)
        req.add_header(
            "User-Agent", "Mozilla/5.0 (X11; U; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.124 Safari/537.36")
        req.add_header(
            "Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8")
        req.add_header("Accept-Encoding", "gzip, deflate, br")
        req.add_header("Accept-Language", "zh-CN,zh;q=0.8,en;q=0.6")
        req.add_header("Cookie", cookie)
        return req
    else:
        return None


def get_response_str(req):
    try:
        with r.urlopen(req, timeout=30) as f:
            decompressed_data = zlib.decompress(f.read(), 16 + zlib.MAX_WBITS)
        return str(decompressed_data, "utf-8", errors='replace')
    except socket.timeout as e:
        print('socket.timeout:', str(e))
        logger.error('socket.timeout:'+str(e))
        time.sleep(random.choice(range(8, 15)))
    except socket.error as e:
        print('socket.error:', str(e))
        logger.error('socket.error:'+str(e))
        time.sleep(random.choice(range(20, 60)))
    except http.client.BadStatusLine as e:
        print('http.client.BadStatusLine:', str(e))
        logger.error('http.client.BadStatusLine:'+str(e))
        time.sleep(random.choice(range(30, 80)))
    except http.client.IncompleteRead as e:
        print('http.client.IncompleteRead:', str(e))
        logger.error('http.client.IncompleteRead:'+str(e))
        time.sleep(random.choice(range(5, 15)))
    return False
    '''
    except urllib.error.URLError as e:
        #if isinstance(e1.reason, socket.timeout):
        print('urllib.error.URLError:',str(e))
        logger.error('urllib.error.URLError:',str(e))
        return False
    except UnicodeDecodeError as e: 
        print('UnicodeDecodeError url:',str(e))
        logger.error('UnicodeDecodeError url:',str(e))
    except socket.timeout as e:
        logger.error("socket timout:",str(e))
        print("第一次，"+str(datetime.now())+'TIME OUT')
        time.sleep(5)
        try:
            with r.urlopen(req,timeout=30) as f:
                decompressed_data =zlib.decompress(f.read(), 16 + zlib.MAX_WBITS)
            return str(decompressed_data, "utf-8", errors='replace')
        except socket.timeout as e2:  
            if isinstance(e2.reason, socket.timeout):
                print("第二次，"+str(datetime.now())+'TIME OUT')
                logger.error("第二次，"+str(datetime.now())+'TIME OUT')
            else:
                logger.error(str(e)) 
            return False
    作者：朝畫夕拾
    链接：https://www.jianshu.com/p/d8585f0d9eb8
    来源：简书
    著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。
    '''
    # finally:
    # print(datetime.now())
    '''
    try:
	response = urllib.request.urlopen('http://httpbin.org/get',timeout=0.1)
except urllib.error.URLError as e:
	if isinstance(e.reason, socket.timeout):
		print('TIME OUT')
    '''
    # 版权声明：本文为CSDN博主「菜鸟也想要高飞」的原创文章，遵循 CC 4.0 BY-SA 版权协议，转载请附上原文出处链接及本声明。
    # 原文链接：https://blog.csdn.net/qq_36365528/article/details/96589973


def get_now_str():
    return int(float(time.time()) * 1000)


# 单个帖子页面

# 准备好目录
def prepare_folder(tid):
    try:
        os.makedirs(tid)
    except FileExistsError or OSError as err:
        logger.error(
            '!!!--error--!!! FileExists or OSError return,'+str(err)+tid)
        print('!!!--error--!!! FileExists or OSError return,'+str(err)+tid)
    folder = os.path.exists("./"+tid+"/jsonbackup")
    if folder == False:
        os.makedirs("./"+tid+"/jsonbackup")  # 创建备份base_info.json文件夹
    # 先判断贴子有没有被删除再决定删不删base_info.json
    if get_thread_basic_info_html(tid) == False:
        logger.error("无法获取到贴子信息，可能已被删除!"+tid)
        print("无法获取到贴子信息，可能已被删除!"+tid)
        return False
    folder2 = os.path.exists("./"+tid+"/base_info.json")
    if folder2 == True:
        if os.path.exists("./"+tid+"/jsonbackup/base_info.json") == True:
            os.remove("./"+tid+"/jsonbackup/base_info.json")
        shutil.move("./"+tid+"/base_info.json", "./"+tid +
                    "/jsonbackup")  # 把base_info.json移动到备份文件夹中
    folder3 = os.path.exists('./'+tid+'/res')
    if folder3 == False:
        shutil.copytree('./model/res', './'+tid+'/res')
    folder4 = os.path.exists('./'+tid+'/error.txt')
    if folder4 == True:
        fp = open("./"+tid+"/error.txt", 'r+')
        read = fp.readline()
        fp.close()
        os.remove("./"+tid+"/error.txt")
        print("错误页数:"+read)
        folder5 = os.path.exists("./"+tid+"/"+read)
        folder6 = os.path.exists("./"+tid+"/"+read+".html")
        if folder5 == True:
            shutil.rmtree("./"+tid+"/"+read)
        if folder6 == True:
            os.remove("./"+tid+"/"+read+".html")
        return True
    folder7 = os.path.exists("./"+tid+"/frinsh.txt")
    if folder7 == True:
        fp = open("./"+tid+"/frinsh.txt", 'r+')
        read = fp.readline()
        print("完成页数:"+read)
        fp.close()
        folder8 = os.path.exists("./"+tid+"/"+read)
        folder9 = os.path.exists("./"+tid+"/"+read+".html")
        folder10 = os.path.exists("./"+tid+"/tiezibackup")
        if folder10 == False:
            os.makedirs("./"+tid+"/tiezibackup")  # 创建备份最后完成的页数文件夹
        else:
            # 有这个文件夹就删除先再创建,这个工具也做不到及时捕捉
            shutil.rmtree("./"+tid+"/tiezibackup")
            os.makedirs("./"+tid+"/tiezibackup")  # 创建备份最后完成的页数文件夹
        if folder8 == True:
            shutil.move('./'+tid+'/'+read, "./"+tid +
                        "/tiezibackup")  # 移动文件到备份文件夹中
            # shutil.rmtree("./"+tid+"/"+read)
        if folder9 == True:
            shutil.move('./'+tid+'/'+read+".html", "./"+tid+"/tiezibackup")
            # os.remove("./"+tid+"/"+read+".html")
        os.remove("./"+tid+"/frinsh.txt")
        return True
    #shutil.copytree('model/res', tid + '/res')
    '''
    https://blog.csdn.net/silentwolfyh/article/details/74931123
    python 移动文件或文件夹操作
    '''

# 把数据填充进去,造一个模版出来


def inflate_detail_model_with_data(base_info):
    with open('./model/model_detail.html', 'r', encoding='utf-8') as f:
        # parser = etree.HTMLParser()
        html_tree = BeautifulSoup(f, 'lxml')
        # return etree.parse(f.read(), parser=parser)

    #meta = html_tree.head.select('meta[furl]')[0]
    #meta['furl'] = base_info['meta_furl']
    #meta['fname'] = base_info['meta_fname']

    title = html_tree.head.title
    title.clear()
    title.append(base_info['title'])

    title_show = html_tree.body.find('h3', class_='core_title_txt')
    title_show.clear()
    title_show['title'] = base_info['title'].split('_')[0]
    title_show.append(base_info['title'].split('_')[0])

    card_head_img = html_tree.body.find('img', class_='card_head_img')
    card_head_img['src'] = base_info['card_head_img']

    card_title = html_tree.body.find('div', class_='card_title')

    card_title_fname = card_title.find('a', class_='card_title_fname')
    card_title_fname.clear()
    card_title_fname.append(base_info['card_title_fname'])

    card_menNum = card_title.find('span', class_='card_menNum')
    card_menNum.clear()
    card_menNum.append(base_info['card_menNum'])

    card_infoNum = card_title.find('span', class_='card_infoNum')
    card_infoNum.clear()
    card_infoNum.append(base_info['card_infoNum'])

    return html_tree


def get_thread_basic_info_html(_tid):
    html_str = get_response_str(
        req_maker('https://tieba.baidu.com/p/' + _tid))  # 整个贴子
    if html_str == False:
        return False
    else:
        temp = BeautifulSoup(html_str, 'lxml')
        # temp2=temp.title.get_text()
        temp2 = temp.body.attrs  # 可能会得到{}
        # print(str(temp2))
        if len(temp2) != 0:
            print(str(temp2['class'][0]))
            if str(temp2['class'][0]) == "page404":
                return False
        return BeautifulSoup(html_str, 'lxml')
        '''
        https://www.jb51.net/article/152899.htm
        python3爬虫获取html内容及各属性值的方法
        #python3
        from bs4 import BeautifulSoup
        html="<html>
        <head>
        <title class='ceshi'>test</title>
        </head>
        <body>
        233
        <p class='sister'>
        666
        </p>
        </body>
        </html>"
        #用BeautifulSoup解析数据 python3 必须传入参数二'html.parser' 得到一个对象，接下来获取对象的相关属性
        html=BeautifulSoup(html,'html.parser')
        # 读取title内容
        print(html.title)
        # 读取title属性
        attrs=html.title.attrs
        print(attrs)
        # 获取属性attrs['class'] ---->['ceshi'] 这是一个list 通过下标可以获取值
        print(attrs['class'][0])
        # 读取body
        print(html.body)
        读取数据还可以通过BeautifulSoup的select方法
        html.select()
        #按标签名查找 
        soup.select('title')
        soup.select('body')
        # 按类名查找
        soup.select('.sister')
        # 按id名查找
        # p标签中id为link的标签
        soup.select('p #link')
        #取标签里面的值
        soup.p.string
        #取标签里属性值 通过href获取
        html['href']
        '''


def get_and_save_src(path, save_path):
    try:
        with r.urlopen(req_maker(path)) as f1:
            # print(str(f1.info()))
            #print(str(f1.info()).find("Content-Type: image/gif"))
            if str(f1.info()).find("Content-Type: image/gif") != -1:
                with open(save_path, 'wb') as wf1:
                    wf1.write(f1.read())
                return
        temp = path
        if temp.find("gsp0.baidu.com") == -1 and temp.find("tb2.bdstatic.com") == -1 and temp.find("gss0.bdstatic.com") == -1 and temp.find("gss3.bdstatic.com") == -1:
            if temp.find(".jpg") != -1:
                temp = temp.split(".jpg")[0]+".webp"
            else:
                temp = temp.split(".png")[0]+".webp"
        print(temp)
        with r.urlopen(req_maker(temp)) as f2:
            with open(save_path, 'wb') as wf2:
                wf2.write(f2.read())
    except BaseException as err:
        logger.error(
            '!!!--error--!!! error on download img src:' + str(err) + ","+path)
        print('!!!--error--!!! error on download img src:' + str(err) + ","+path)


def get_thread_basic_info(t_tid, t_fid):  # 制造base_info.json文件
    res = {}
    res['tid'] = t_tid
    res['fid'] = t_fid  # ok

    html_tree = get_thread_basic_info_html(t_tid)
    # html_tree=False
    if html_tree == False:  # 如果返回false，阻止继续往下运行，否则报错
        return False
    # meta furl 我也不知道这个是拿来干嘛
    # 获取均为null
    #meta = html_tree.head.select('meta[furl]')
    #res['meta_furl'] = meta[0].furl
    #res['meta_fname'] = meta[0].fname

    # 标题
    res['title'] = html_tree.head.title.string.strip()
    # print(res['title'])

    # 贴吧头像部分
    res['card_head_img'] = html_tree.body.find(
        'img', class_='card_head_img')['src']
    # print(res['card_head_img'])

    # 下载贴吧头像文件
    # res['card_head_img_path'] = res['tid'] + '/' + urlparse(res['card_head_img']).path.split('/')[-1]
    # with open(res['card_head_img_path, 'wb') as img_src:
    #     img_src.write(get_src(res['card_head_img))

    card_title = html_tree.body.find('div', class_='card_title')

    # 贴吧名称
    res['card_title_fname'] = card_title.find(
        'a', class_='card_title_fname').string.strip()
    # print(str(res))

    # 贴吧关注和帖子数
    res['card_menNum'] = card_title.find(
        'span', class_='card_menNum').string.strip()
    # print(res['card_menNum'])
    res['card_infoNum'] = card_title.find(
        'span', class_='card_infoNum').string.strip()
    # print(res['card_infoNum'])

    # 帖子页数,这个比较关键
    l_reply_num_nods = html_tree.find_all('li', class_='l_reply_num')
    for node in l_reply_num_nods:
        if len(node.contents) > 0:
            spans = node.find_all('span', class_='red')
            if len(spans) == 2:
                res['reply_page'] = int(spans[0].string.strip())
                res['total_page'] = int(spans[1].string.strip())
    # print("回复数："+str(res['reply_page']))
    # print("贴子页数"+str(res['total_page']))
    return res


# 实际内容和评论列表,这个page是实际的贴子页数
def get_thread_by_page(tid, base_info, page):
    html_str = get_response_str(req_maker(
        'http://tieba.baidu.com/p/' + base_info['tid'] + "?ajax=1&pn=" + str(page)))  # 楼层
    print('http://tieba.baidu.com/p/' +
          base_info['tid'] + "?ajax=1&pn=" + str(page))
    # html_str=False
    if html_str == False:
        fp = open("./"+tid+"/error.txt", 'w')  # 直接打开一个文件，如果文件不存在则创建文件
        fp.write(str(page))
        fp.close()
        return False, False
    else:
        html_tree = BeautifulSoup(html_str, 'lxml')
    content = {}
    content['content'] = html_tree.find('div', id='j_p_postlist')
    # <div id="ajax-content"><div class="p_postlist" id="j_p_postlist">直接换
    content['up'] = html_tree.find('div', id='thread_theme_5')
    # <div id="ajax-up"><div class="p_thread thread_theme_5" id="thread_theme_5">这个得处理一下
    content['down'] = html_tree.find('div', id='ajax-down')
    # <div id="ajax-down"><div class="p_thread thread_theme_7" id="thread_theme_7">这个也得处理一下

    # 评论列表,这个是json格式,目标是知道哪个楼有回复,同时拿到comment_num也就是总回复数
    # http://tieba.baidu.com/p/totalComment?tid=4736198966&fid=738100&pn=2&see_lz=0
    json_str = get_response_str(req_maker('http://tieba.baidu.com/p/totalComment?tid='
                                          + base_info['tid'] + '&fid=' + base_info['fid'] + '&pn=' + str(page)))
    print('http://tieba.baidu.com/p/totalComment?tid='
          + base_info['tid'] + '&fid=' + base_info['fid'] + '&pn=' + str(page))  # 总楼中楼
    if json_str == False:
        fp = open("./"+tid+"/error.txt", 'w')  # 直接打开一个文件，如果文件不存在则创建文件
        fp.write(str(page))
        fp.close()
        return False, False
    else:
        json_data = json.loads(json_str)
    # print(json_data)
    comment_data = {}
    for key in json_data['data']['comment_list']:
        comment_data[key] = json_data['data']['comment_list'][key]['comment_num']

    return content, comment_data


# 回复,这个比较麻烦
def make_reply_block():
    # 这个块区添加到对应的div class="j_lzl_container core_reply_wrapper"内部去
    # 评论放到<ul class="j_lzl_m_w" style="display:">里面
    block_str = '''
    <div class="core_reply_border_top">
    </div>
	<div class="j_lzl_c_b_a core_reply_content">
		<ul class="j_lzl_m_w" style="display:">
        </ul>
		<div class="lzl_editor_container j_lzl_e_c lzl_editor_container_s" style="display:none;">
		</div>
	</div>
	<div class="core_reply_border_bottom"></div>
    '''
    return BeautifulSoup(block_str, 'lxml')


# http://tieba.baidu.com/p/comment?tid=3042881140&pid=50510635824&pn=2,这个一次给10条,不过这里会循环一直到取不到为止
# pid为楼层id

def get_comment_by_floor(tid, pid, page2):
    go_on = True
    page = 1
    res = []
    while go_on:
        go_on = False
        html_str = get_response_str(
            req_maker('http://tieba.baidu.com/p/comment?tid=' + tid + "&pid=" + pid + '&pn=' + str(page)))  # 有&pn=是取不到内容的
        print('http://tieba.baidu.com/p/comment?tid=' +
              tid + "&pid=" + pid + '&pn=' + str(page))  # 楼中楼
        if html_str == False:
            fp = open("./"+tid+"/error.txt", 'w')  # 直接打开一个文件，如果文件不存在则创建文件
            fp.write(str(page2))
            fp.close()
            return False
        else:
            html_tree = BeautifulSoup(html_str, 'lxml')
        page += 1
        li_nodes = html_tree.find_all('li')
        for node in li_nodes:
            for count in range(len(node['class'])):
                if node['class'][count] == 'lzl_single_post':
                    res.append(node)
                    go_on = True
                if node['class'][count] == 'first_no_border':
                    node['class'][count] = ''
        time.sleep(random.choice(range(2, 5)))

    block_tree = make_reply_block()
    block_tree_node = block_tree.find('ul')
    for add_node in res:
        block_tree_node.append(add_node)
    return block_tree


# 获取单个帖子,按页保存,能够哪个页面坏了删掉那一页重新跑就行
def get_single_thread(tid, fid, title_check, page):
    if tid is None or fid is None:
        logger.error(
            '!!!--error--!!! lacking basic info, can not continue!'+tid)
        print('!!!--error--!!! lacking basic info, can not continue!'+tid)
        return

    thread_tid = tid
    thread_fid = fid
    base_dir = './'+thread_tid + '/'

    # 1.准备好目录
    print('1.prepare thread folder')
    if prepare_folder(thread_tid) == False:
        return

    # 2.收集帖子基本信息
    print('2.get thread basic info')
    if os.path.exists(base_dir + 'base_info.json'):
        print('2.get thread basic info from json')
        with open(base_dir + 'base_info.json', 'r', encoding='utf-8') as base_info_file:
            info = json.load(base_info_file)

    else:
        print('2.get thread basic info from html')
        info = get_thread_basic_info(thread_tid, thread_fid)
        if info == False:
            logger.error("制造base_info.json文件失败"+tid)
            print("制造base_info.json文件失败"+tid)
            return False
        with open(base_dir + 'base_info.json', 'w', encoding='utf-8') as base_info_file:
            base_info_file.write(json.dumps(info))

    # print(str(info['title']))
    # print('66666666666666666666666666666666666666666')
    '''
    #发现这个有问题，tieba的api改版了，这个会删掉有用的
    if title_check:
        #贴吧里面会混入别的贴吧的信息,通过校验title干掉大部分这些恶心的东西
        if info['title'].find(title_check) == -1:
            print("fake thread found!!!")
            shutil.rmtree(thread_tid)#Python os.removedirs() 和shutil.rmtree() 用于删除文件夹
            return True
    '''
    # 构造模版,并填充基本数据
    print('3.inflate model with info')
    model = inflate_detail_model_with_data(info)

    print('4.start getting pages')
    for page in range(1, info['total_page'] + 1):  # range(1,a.total_page + 1)
        if os.path.exists(base_dir + str(page) + '.html') == True and os.path.exists(base_dir + str(page)) == False:  # 如果出现有网页没目录的情况
            os.remove(base_dir + str(page) + '.html')  # 删除网页
        if not os.path.exists(base_dir + str(page) + '.html'):
            print('getting page:' + str(page))
            # 资源目录
            if os.path.exists(base_dir + str(page)) == False:  # 检查有没有文件夹
                os.makedirs(base_dir + str(page))  # 没有创建
            else:
                shutil.rmtree(base_dir + str(page))  # 有即删除
                os.makedirs(base_dir + str(page))  # 再创建
            # 清除模版里的旧数据
            p_postlist = model.find('div', id='j_p_postlist')
            p_postlist.clear()
            thread_theme_5 = model.find('div', id='thread_theme_5')
            thread_theme_5.clear()
            thread_theme_7 = model.find('div', id='thread_theme_7')
            thread_theme_7.clear()
            headpic = model.find('div', class_='card_head')  # 找到包住吧头像的标签
            headpic2 = model.find('img', class_='card_head_img')  # 先存着吧头像标签
            headpic.clear()  # 清空包住吧头像的标签
            temp = BeautifulSoup("<a href='"+"../../"+str(page) +
                                 ".html'>"+str(headpic2)+"</a>", 'lxml')  # 为吧头像表情增加超链接
            headpic.append(temp)  # 重新添加回去
            baming = model.find('a', class_='card_title_fname')
            baming['href'] = '../../'+str(page)+'.html'  # 点贴吧名字跳转到主题贴列表
            # tupiantie = get_thread_basic_info_html(thread_tid)#图片贴
            # tupiantie2=tupiantie.find('div', id='ag_container')#图片贴
            # thread_theme_5.append(tupiantie2)
            print('getting page detail ' + str(page))
            # 获取实际内容和评论列表
            content, comment_data = get_thread_by_page(tid, info, page)
            if content == False and comment_data == False:
                logger.error("获取实际内容和评论列表失败!"+tid)
                print("获取实际内容和评论列表失败!"+tid)
                return False
            # 列表的实际内容
            post_lists = content['content'].find_all('div', class_='l_post')
            for post in post_lists:
                # 取出post数据
                post_data_node = post.find('div', class_="j_d_post_content")

                post_data_node2 = post.find(
                    'span', class_="j_jb_ele")  # 解决举报按钮图片
                if post_data_node2:
                    post_data_node2.clear()

                post_data_node3 = post.find(
                    'span', class_="icon_wrap icon_wrap_theme1 d_pb_icons")  # 解决星座图片
                if post_data_node3:
                    post_data_node3.clear()

                post_data_node3 = post.find(
                    'div', class_="icon_relative").find("a")  # 解决头像框
                if post_data_node3:
                    post_data_node3['style'] = None

                post_data_node4 = post.find('div', class_="post_bubble_top")
                if post_data_node4:
                    post_data_node4['style'] = None
                post_data_node5 = post.find('div', class_="post_bubble_middle")
                if post_data_node5:
                    post_data_node5['style'] = None
                post_data_node6 = post.find('div', class_="post_bubble_bottom")
                if post_data_node6:
                    post_data_node6['style'] = None

                post_data_node7 = post.find_all(
                    'img', class_="nicknameEmoji")  # 昵称,用find_all解决找到前面不找后面
                for temp in post_data_node7:
                    if temp:
                        emoji = temp['src'].split("/")
                        temp['src'] = "res/nickemoji/"+emoji[len(emoji)-1]

                if post_data_node:
                    post_data_id = post_data_node['id'].split('_')[-1]
                    post_data_node_comment = post.find(
                        'div', class_="j_lzl_container")
                    post_data_node_comment['data-field'] = None
                    post_data_node_comment['style'] = None
                    post_data_node_comment.clear()

                    # 送他礼物
                    share_btn_wrapper = post.find(
                        'div', class_="share_btn_wrapper")
                    if share_btn_wrapper:
                        share_btn_wrapper.clear()

                    if comment_data.get(post_data_id):
                        # 有评论
                        block_tree = get_comment_by_floor(
                            thread_tid, post_data_id, page)
                        if block_tree == False:
                            logger.error("获取评论失败!"+tid)
                            print("获取评论失败!"+tid)
                            return False
                        post_data_node_comment.append(block_tree)

                    p_postlist.append(post)
                    print('adding a floor ' + str(page))
                else:
                    # 广告!!!
                    print('enconter an ad ' + str(page))
                #time.sleep(random.choice(range(5, 10)))

            print('dealing with up index ' + str(page))
            # 头部
            l_thread_info_up = content['up'].find(
                'div', class_='l_thread_info')
            a_nodes_up = l_thread_info_up.find_all('a')
            for a_node in a_nodes_up:
                a_node['href'] = None
                if a_node.string == '首页':
                    a_node['href'] = '1.html'
                elif a_node.string == '尾页':
                    a_node['href'] = str(info['total_page']) + '.html'
                elif a_node.string == '上一页':
                    a_node['href'] = str(page - 1) + '.html'
                elif a_node.string == '下一页':
                    a_node['href'] = str(page + 1) + '.html'
                else:
                    try:
                        num = int(a_node.string)
                        a_node['href'] = str(num) + '.html'
                        #a_node['href'] ='1.html'
                        print(str(a_node))
                    except TypeError:
                        logger.error('!!!--error--!!! TypeError:' +
                                     a_node.prettify()+tid)
                        print('!!!--error--!!! TypeError:' +
                              a_node.prettify()+tid)  # 会报错，但似乎没有影响
                    except ValueError:
                        logger.error(
                            '!!!--error--!!! unknow page:' + a_node.string+tid)
                        print('!!!--error--!!! unknow page:' + a_node.string+tid)
            thread_theme_5.append(l_thread_info_up)

            print('dealing with down index ' + str(page))
            # 尾部
            l_thread_info_down = content['down'].find(
                'div', class_='l_thread_info')
            a_nodes_down = l_thread_info_down.find_all('a')
            for a_node in a_nodes_down:
                a_node['href'] = None
                if a_node.string == '首页':
                    a_node['href'] = '1.html'
                elif a_node.string == '尾页':
                    a_node['href'] = str(info['total_page']) + '.html'
                elif a_node.string == '上一页':
                    a_node['href'] = str(page - 1) + '.html'
                elif a_node.string == '下一页':
                    a_node['href'] = str(page + 1) + '.html'
                else:
                    try:
                        num = int(a_node.string)
                        a_node['href'] = str(num) + '.html'
                        print(str(a_node))
                    except TypeError:
                        logger.error('!!!--error--!!! TypeError:' +
                                     a_node.prettify()+tid)
                        print('!!!--error--!!! TypeError:' +
                              a_node.prettify()+tid)
                    except ValueError:
                        logger.error(
                            '!!!--error--!!! unknow page:' + a_node.string+tid)
                        print('!!!--error--!!! unknow page:' + a_node.string+tid)
            thread_theme_7.append(l_thread_info_down)

            print('clear thread_recommend ad ' + str(page))
            # 又一个广告
            AD2 = model.find('div', class_='thread_recommend')
            if AD2:
                AD2.clear()

            print('clear staff under name ' + str(page))
            # 一个奇怪的样式,会挂在名字底下
            d_pb_icons = model.find('span', class_='d_pb_icons')
            if d_pb_icons:
                d_pb_icons.clear()

            # 处理资源,这里再弄一份是因为model突然搜不到带src的标签,我也不知道为什么,重新构造一份才行
            write_model = BeautifulSoup(str(model), 'lxml')
            src_nodes = write_model.select('img[src]')
            print('dealing with src ' + str(page))
            count = 1
            download_list = {}
            for src_node in src_nodes:
                # 部分头像是用这个加载
                lazy_load = src_node.get('data-tb-lazyload')
                if lazy_load:
                    src_node['src'] = lazy_load
                src_str = src_node['src']
                if src_str.find('http') != -1:
                    if download_list.get(src_str):
                        src_node['src'] = download_list.get(src_str)
                    else:
                        # print(src_str+",66666666666")
                        # name=src_str.encode('utf-8')
                        # names1=str(name).split("/item/")#贴吧用户头像
                        # names2=str(name).split("%2Fitem%2F")#贴吧头像
                        # if(len(names1)>1):
                            # names3=names1[1].split("?t=")
                            #link_path = str(page) + '/' + names3[0] + '.jpg'
                            # print('666'+str(names3[0]))
                        # elif(len(names2)>1):
                            # names4=names2[1].split(".jpg'")
                            #link_path = str(page) + '/' + names4[0]+ '.jpg'
                            # print('777'+str(names4[0]))
                        md5 = hashlib.md5()  # 下载图片 https://blog.csdn.net/qq_38607035/article/details/82591931
                        md5.update(src_str.encode('utf-8'))
                        link_path = str(page) + '/' + md5.hexdigest() + '.jpg'
                        # //imgsa.baidu.com
                        # https://imgsrc.baidu.com/forum/pic/item/
                        if(src_str.find("//tiebapic.baidu.com/forum/") != -1):  # 贴子里面的图片
                            sss2 = src_str.split("/")
                            src_str = "http://tiebapic.baidu.com/forum/pic/item/" + \
                                sss2[len(sss2)-1].split(".")[0] + \
                                ".jpg"  # jpg 解决签名档偶尔下载不到图片的问题
                            print(src_str)
                            link_path = str(page) + '/' + \
                                sss2[len(sss2)-1].split(".")[0]+".jpg"
                        elif(src_str.find("//imgsa.baidu.com/forum/") != -1):
                            sss2 = src_str.split("/")
                            src_str = "http://imgsrc.baidu.com/forum/pic/item/" + \
                                sss2[len(sss2)-1].split(".")[0] + \
                                ".jpg"  # jpg 解决签名档偶尔下载不到图片的问题
                            print(src_str)
                            link_path = str(page) + '/' + \
                                sss2[len(sss2)-1].split(".")[0]+".jpg"
                        src_node['src'] = link_path
                        get_and_save_src(src_str, base_dir + link_path)
                        print(str(src_str)+str(base_dir)+str(link_path))
                        print('downloading no.' +
                              str(count) + ' img ' + str(page))
                        count += 1
                        download_list[src_str] = link_path
            download_list.clear()
            # 完成,输出
            with open(base_dir + str(page) + '.html', 'w', encoding='utf-8') as f:
                f.write(str(write_model))
            print('done with page ' + str(page))
            time.sleep(random.choice(range(1, 5)))
    fp = open("./"+tid+"/frinsh.txt", 'w')  # 直接打开一个文件，如果文件不存在则创建文件
    fp.write(str(info['total_page']))
    fp.close()
    return True


def start(url):
    # https://tieba.baidu.com/p/XXXXXXXX?pn=XX
    tid = str(url).split("/p/")[1].split("?pn=")[0]
    tid2 = re.search(r'^[0-9]*$', tid).group(0)  # 正则表达式判断是不是全是数字
    # print(tid)
    # print(tid2)
    if(tid2 != None):
        if get_single_thread(tid2, '', '', '1') == True:
            return True
        else:
            return False
    else:
        print('贴子链接无效！'+tid)
        return False
    # Python3 正则表达式 | 菜鸟教程
    # https://www.runoob.com/python3/python3-reg-expressions.html
    #数字正则表达式 - miyaye - 博客园
    # https://www.cnblogs.com/webskill/p/7422876.html


def usejson():
    # 读取JSON配置文件
    filename = "./tiezi.json"
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
    tiezilists = jsontemp['tiezi']
    for x in tiezilists:
        if x[2] == True:
            print('链接:'+x[0]+',标题'+x[1])
            start(x[0])
        else:
            print('链接:'+x[0]+","+str(x[2])+",该贴不更新！")
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
    timeoutx = 1800+random.choice(range(1, 10))
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
    cookie = ""
    try:  # 不用bat启动会报错所以，设计成这样，报错后默认使用单次运行
        if sys.argv[1] == "1":
            print("开始周期运行！")
            starttimer()  # 周期运行
        else:
            usejson()  # 单次运行
    except Exception as err:
        usejson()  # 单次运行
'''
http://tieba.baidu.com/p/6351272485 【直播】11月15日问题反馈结果（贴吧意见反馈吧） 有bug，例如这个贴子不能获取每个的楼层时间
get_single_thread('6351272485','898666','','1')
楼层https://tieba.baidu.com/mo/q-----1-1-0----/flr?pid=XXXXX&kz=XXXXXXX&pn=0
楼中楼https://tieba.baidu.com/p/comment?tid=xxxxxx&pid=xxxxxxxx&pn=0
这是多行注释，用三个单引号
'''