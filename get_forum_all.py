import get_forum_list
import get_single_thread
import os
import shutil
import signal
import json
from urllib.parse import unquote
from selenium import webdriver
from datetime import datetime
from bs4 import BeautifulSoup

#from selenium import webdriver#没有使用谷歌的chromedriver，因为运行起来意外的慢,而且这个要求本机必须安装有注册的谷歌浏览器
#from selenium.webdriver.chrome.options import Options

#path =r'D:\python3.6.8\Scripts\chromedriver.exe'#有附带chromedriver.exe，但要注意selenium的版本号，这里为了支持PhantomJS.exe,压低版本了(2.53.6)
#chrome_options = Options()
#chrome_options.add_argument('--headless')

def get_forum_list_call(url):
    #get_forum_list.browser = webdriver.Chrome(executable_path=path, options=chrome_options)
    get_forum_list.browser = webdriver.PhantomJS()
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
    info_file_name = unquote(unquote(get_forum_list.get_info_from_query(url, 'kw')))
    if os.path.exists(info_file_name + '/forum_base_info.json'):
        with open(info_file_name + '/forum_base_info.json', 'r', encoding='utf-8') as base_info_file:
            info = json.load(base_info_file)

        for page in range(1, info['total_page'] + 1):
            if os.path.exists(info_file_name + '/' + str(page) + '_thread/tid_info.json'):
                with open(info_file_name + '/' + str(page) + '_thread/tid_info.json', 'r',
                          encoding='utf-8') as thread_info_file:
                    tid_info = json.load(thread_info_file)
                fid = tid_info['fid']
                for tid in tid_info['tid_list']:
                    if not os.path.exists(info_file_name + '/' + str(page) + '_thread/' + tid + '/1.html'):
                        try:
                            print('downloading thread ' + tid + ' in page' + str(page))
                            has_fake_thread = get_single_thread.get_single_thread(tid, fid, info['title'],page)
                            if has_fake_thread:
                                kill_fake_thread(info_file_name + '/' + str(page) + '.html', page, tid)
                            else:
                                shutil.copytree(tid, info_file_name + '/' + str(page) + '_thread/' + tid)
                                shutil.rmtree(tid)
                        except BaseException:
                            print('!!!--error--!!! download error tid:' + tid)

def start(url):
    my_url = url
    print(datetime.now())
    get_forum_list_call(my_url)
    get_threads_from_forum_page(my_url, my_cookie)
    print(datetime.now())

if __name__ == '__main__':
    my_cookie = ""#不知道怎么填
    start("http://tieba.baidu.com/f?kw=%E8%B4%B4%E5%90%A7") #贴吧
    #print(datetime.now())
    #get_forum_list_call(my_url)
    #get_threads_from_forum_page(my_url, my_cookie)
    #print(datetime.now())
