import os
import shutil
import json
import hashlib
import signal

from datetime import datetime
from urllib import request as r
from urllib.parse import urlparse
from urllib.parse import unquote
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
#from selenium.webdriver.chrome.options import Options

#path =r'D:\python3.6.8\Scripts\chromedriver.exe'
#chrome_options = Options()

browser = None

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

# 1.准备根目录
def prepare_home_base_dir(home_base_dir):
    #print(home_base_dir+'model/res')
    #print(home_base_dir + 'res')
    try:
        os.makedirs(home_base_dir)
    except Exception as err:#FileExistsError or OSError:
        print(err)
        print(datetime.now())
        return
        #print('!!!--error--!!! FileExists or OSError return')
        
    shutil.copytree('./model/res',home_base_dir+'res')
    


# 获取单个页面
def get_single_list_page(url):
    browser.get(url)
    return BeautifulSoup(str(browser.page_source), 'lxml')


def get_and_save_src(path, save_path):
    try:
        with r.urlopen(path) as f:
            with open(save_path, 'wb') as wf:
                wf.write(f.read())
    except BaseException:
        print('!!!--error--!!! error on download img src:', path)


def get_info_from_query(url, key):
    query_str = urlparse(url).query
    for query_pair in query_str.split('&'):
        if query_pair.split('=')[0] == key:
            return query_pair.split('=')[1]


# 获取贴吧基本信息,注意不要拿最后一页的地址,因为需要计算楼层数
def get_forum_basic_info(base_url):
    html_tree = get_single_list_page(base_url)
    # with open('model/model_list.html', 'r', encoding='utf-8') as f:
    #     html_tree = BeautifulSoup(f, 'lxml')
        
    res = {}

    # 标题
    res['title'] = html_tree.head.title.string.strip()
    # print(res['title'])

    # 贴吧头像部分
    res['card_head_img'] = html_tree.body.find('img', class_='card_head_img')['src']
    # print(res['card_head_img'])

    card_title = html_tree.body.find('div', class_='card_title')

    # 贴吧名称
    res['card_title_fname'] = card_title.find('a', class_='card_title_fname').string.strip()
    # print(res['card_title_fname'])

    # 关注和帖子数
    res['card_menNum'] = card_title.find('span', class_='card_menNum').string.strip()
    # print(res['card_menNum'])
    res['card_infoNum'] = card_title.find('span', class_='card_infoNum').string.strip()
    # print(res['card_infoNum'])

    # 贴吧口号(目录不要了)
    if html_tree.find('p', class_='card_slogan')!=None:
        res['card_slogan'] = html_tree.find('p', class_='card_slogan').string
    else:
        res['card_slogan'] =''
    # print(res['card_slogan'])

    thread_list_bottom = html_tree.body.find('div', class_='thread_list_bottom')
    # 贴吧页数,这个也很关键
    floor_group = thread_list_bottom.find('div', id='frs_list_pager')
    if floor_group:
        floor_nodes = floor_group.find_all('a')
        last_page = floor_nodes[-1]
        page_link = last_page['href']
        ori_num = int(get_info_from_query(page_link, 'pn'))
        if ori_num == 0:
            res['total_page'] = 1
        else:
            res['total_page'] = int(ori_num / 50 + 1)
    else:
        res['total_page'] = 1
    # print(res['total_page'])

    th_footer_l = thread_list_bottom.find('div', class_='th_footer_l')
    th_footer_l_nodes = th_footer_l.find_all('span')

    # 帖子数
    res['total_thread_num'] = int(th_footer_l_nodes[0].string.strip())
    # print(res['total_thread_num'])
    # 楼层总数
    res['total_floor_num'] = int(th_footer_l_nodes[1].string.strip())
    # print(res['total_floor_num'])
    # 会员数
    res['total_member_num'] = int(th_footer_l_nodes[2].string.strip())
    # print(res['total_member_num'])

    # 贴吧id,从script 源代码中拿
    script_nodes = html_tree.head.find_all('script')
    for script in script_nodes:
        script_str = str(script)
        if script_str.find('PageData.forum') != -1:
            # 切割js源代码,非常恶心
            str1 = script_str[script_str.find('PageData.forum'):-1]
            str2 = str1[0: str1.find('}') + 1]
            str3 = str2[str2.find(':') + 1:str2.find(',')]  # 认为id会写在第一个
            res['fid'] = str3.strip()

    # print(res['fid'])

    return res


def inflate_detail_model_with_list_data(base_info):
    with open('./model/model_list.html', 'r', encoding='utf-8') as f:
        # parser = etree.HTMLParser()
        html_tree = BeautifulSoup(f, 'lxml')

    title = html_tree.head.title
    title.clear()
    title.append(base_info['title'])

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

    card_slogan = html_tree.find('p', class_='card_slogan')
    card_slogan.clear()
    if base_info['card_slogan']:
        card_slogan.append(base_info['card_slogan'])

    return html_tree


# 列表页不需要登录,所以不用cookie,但是因为有恶心的bigpipe,所以要靠selenium和PhantomJS,这个得提前装好

# 贴吧所有列表页,帖子页分开来弄
def get_forum_list(base_url):
    quote_base_dir = get_info_from_query(base_url, 'kw')
    if quote_base_dir is None:
        print('!!!--error--!!! fatal error, can not find forum name!')
        return
    else:
        base_dir = './'+unquote(unquote(quote_base_dir))
        base_dir += '/'
        #print(base_dir)

    # 1.准备根目录
    print('1.prepare forum folder')
    prepare_home_base_dir(base_dir)

    # 2.收集贴吧基本信息
    print('2.get forum basic info')
    if os.path.exists(base_dir + 'forum_base_info.json'):
        print('2.get forum basic info from json')
        with open(base_dir + 'forum_base_info.json', 'r', encoding='utf-8') as base_info_file:
            info = json.load(base_info_file)

    else:
        print('2.get forum basic info from web')
        info = get_forum_basic_info(base_url)
        with open(base_dir + 'forum_base_info.json', 'w', encoding='utf-8') as base_info_file:
            base_info_file.write(json.dumps(info))

    # print(info)
    # 构造模版,并填充基本数据
    print('3.inflate model with info')
    model = inflate_detail_model_with_list_data(info)

    print('4.start getting pages')
    for page in range(1, info['total_page'] + 1):
        if not os.path.exists(base_dir + str(page) + '.html'):
            print('getting page:' + str(page))
            # 资源目录
            os.makedirs(base_dir + str(page))
            # 清除模版里的旧数据
            thread_list = model.find('ul', id='thread_list')
            thread_list.clear()
            thread_list_bottom = model.find('div', class_='thread_list_bottom')
            thread_list_bottom.clear()
            headpic = model.find('div', class_='card_head')#找到包住吧头像的标签
            headpic2= model.find('img', class_='card_head_img')#先存着吧头像标签
            headpic.clear()#清空包住吧头像的标签
            temp=BeautifulSoup("<a href='"+"http://tieba.baidu.com/f?kw=" + quote_base_dir + "&ie=utf-8"+"'>"+str(headpic2)+"</a>",'lxml')#为吧头像表情增加超链接
            headpic.append(temp)#重新添加回去
            baming = model.find('a', class_='card_title_fname')
            baming['href']="http://tieba.baidu.com/f?kw=" + quote_base_dir + "&ie=utf-8"#点贴吧名字跳转到活的贴吧链接

            print('getting page detail ' + str(page))

            # 获取实际内容
            content = get_single_list_page(
                "http://tieba.baidu.com/f?kw=" + quote_base_dir + "&ie=utf-8&pn=" + str(int((page - 1) * 50)))

            # 帖子列表
            tid_list = []
            thread_list_data = content.find('ul', id='thread_list')

            #username2=content.find('div',class_='threadlist_author')
            #print(username2)
            #username2.clear()

            for thread_list_node in thread_list_data:
                try:
                    if "thread_top_list_folder" in thread_list_node['class']:
                        # 置顶
                        # j_thread_hidden = thread_list_node.find_all('a', class_="j_thread_hidden")
                        # for j_thread_hidden_node in j_thread_hidden:
                        #     tid_str = j_thread_hidden_node['data-field']
                        #     tid_list.append(tid_str[tid_str.find(':') + 1:tid_str.find('}')])

                        j_th_tit = thread_list_node.find_all('a', class_="j_th_tit")
                        if j_th_tit:
                            for j_th_tit_node in j_th_tit:
                                tid_str = ((j_th_tit_node['href']).split('/'))[-1]
                                tid_list.append(tid_str)
                                # 修改帖子指向地址
                                j_th_tit_node['href'] = str(page) + '_thread/' + tid_str + '/1.html'
                        else:
                            print('something wrong maybe')

                        username2=thread_list_node.find_all('div', class_='threadlist_author')#去掉星座图片
                        for temp in username2:
                            if temp:
                                temp.find('span', class_='icon_wrap').clear()

                        thread_list.append(thread_list_node)#主题贴列表相关，注释掉后就仅剩帖子了

                    elif "j_thread_list" in thread_list_node['class']:
                        # 普通帖子
                        # tid_str1 = thread_list_node['data-field']
                        # tid_str2 = tid_str1[tid_str1.find('id') + 3: -1]
                        # tid_str3 = tid_str2[0:tid_str2.find(',')]
                        # tid_list.append(tid_str3.replace(':', '').strip())

                        # 置顶也会被搜进这里来
                        j_th_tit = thread_list_node.find('a', class_="j_th_tit")
                        if j_th_tit:
                            tid_str = j_th_tit['href'].split('/')[-1]
                            tid_list.append(tid_str)
                            # 修改帖子指向地址
                            j_th_tit['href'] = str(page) + '_thread/' + tid_str + '/1.html'
                        else:
                            print('something wrong on a_target maybe')
                            
                        username2=thread_list_node.find('div', class_='threadlist_author').find_all('span', class_='icon_wrap')#去掉星座图片
                        for temp in username2:
                            if temp:
                                temp.clear()
                                
                        thread_list.append(thread_list_node)#主题贴列表相关，注释掉后就仅剩置顶帖了

                    else:
                        # 广告!!!
                        print('enconter an ad ' + str(page))

                    username=thread_list_node.find('span', class_='tb_icon_author').find_all('img', class_='nicknameEmoji')#主题贴楼主昵称图片
                    for temp in username:
                        if username:
                            emoji=temp['src'].split("/")
                            temp['src'] ="res/nickemoji/"+emoji[len(emoji)-1]
                        
                    username=thread_list_node.find('span', class_='tb_icon_author_rely').find_all('img', class_='nicknameEmoji')#最后回贴人的昵称图片
                    for temp in username:
                        if username:
                            emoji=temp['src'].split("/")
                            temp['src'] ="res/nickemoji/"+emoji[len(emoji)-1]

                except BaseException:
                    # 解析帖子列表的时候会混进很多奇怪的东西,不管
                    print('enconter an exception but it is expected')

            # 保存列表中的详情id数据
            thread_id_data = {}
            thread_id_data['fid'] = info['fid']
            thread_id_data['tid_list'] = tid_list
            os.makedirs(base_dir + str(page) + '_thread')
            with open(base_dir + str(page) + '_thread/' + 'tid_info.json', 'w', encoding='utf-8') as tid_info_file:
                tid_info_file.write(json.dumps(thread_id_data))
            
            # 底部页码
            thread_list_bottom_data = content.find('div', class_='thread_list_bottom')
            for pagination_item in thread_list_bottom_data.find_all('a', class_='pagination-item'):
                pagination_item['href'] = None
                if pagination_item.string == '首页':
                    pagination_item['href'] = '1.html'
                elif pagination_item.string == '尾页':
                    pagination_item['href'] = str(info['total_page']) + '.html'
                elif pagination_item.string.find('上一页') != -1:
                    pagination_item['href'] = str(page - 1) + '.html'
                elif pagination_item.string.find('下一页') != -1:
                    pagination_item['href'] = str(page + 1) + '.html'
                else:
                    try:
                        num = int(pagination_item.string)
                        pagination_item['href'] = str(num) + '.html'
                    except TypeError:
                        print('!!!--error--!!! TypeError:' + pagination_item.prettify())
                    except ValueError:
                        print('!!!--error--!!! unknow page:' + pagination_item.string)

            thread_list_bottom.replace_with(thread_list_bottom_data)

            # 处理资源,这里再弄一份是因为model突然搜不到带src的标签,我也不知道为什么,重新构造一份才行
            write_model = BeautifulSoup(str(model), 'lxml')
 
            src_nodes = write_model.select('img')
            print('dealing with src ' + str(page))
            count = 1
            download_list = {}
            for src_node in src_nodes:
                # 有些大图放在bpic里面,直接去下大图太大了。。。还是要data-original这个是小图
                try:
                    if src_node['src'] is None or src_node['src'] == '':
                        src_node['src'] = src_node['data-original']
                        src_node['style'] = 'display: inline; width: 90px; height: 90px;'
                    src_str = src_node['src']
                    if src_str.find('http') != -1:
                        if download_list.get(src_str):
                            src_node['src'] = download_list.get(src_str)
                        else:
                            md5 = hashlib.md5()
                            md5.update(src_str.encode('utf-8'))
                            link_path = str(page) + '/' + md5.hexdigest() + '.png'
                            src_node['src'] = link_path
                            get_and_save_src(src_str, base_dir + link_path)
                            print('downloading no.' + str(count) + ' img ' + str(page))
                            count += 1
                            download_list[src_str] = link_path
                except BaseException:
                    print('!!!--error--!!! invalid img tag!')
            download_list.clear()
                
            # 完成,输出
            with open(base_dir + str(page) + '.html', 'w', encoding='utf-8') as f:
                f.write(str(write_model))
            print('done with page ' + str(page))


if __name__ == '__main__':
    #browser = webdriver.Chrome()
    browser = getSource()#webdriver.PhantomJS()
    get_forum_list("https://tieba.baidu.com/f?ie=utf-8&kw=%E8%B4%B4%E5%90%A7")#贴吧
    browser.service.process.send_signal(signal.SIGTERM)
    browser.quit()
