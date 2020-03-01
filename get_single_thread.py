import zlib
import time
import os
import shutil#文件操作
import json
import hashlib

from urllib import request as r
from bs4 import BeautifulSoup

pic_name={}

#浏览器的开发者工具network可以找到header
def req_maker(path):
    if path:
        req = r.Request(path)
        req.add_header("User-Agent","Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.104 Safari/537.36")
        req.add_header("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8")
        req.add_header("Accept-Encoding", "gzip, deflate, sdch")
        req.add_header("Accept-Language", "zh-CN,zh;q=0.8,en;q=0.6")
        req.add_header("Cookie", cookie)
        return req
    else:
        return None


def get_response_str(req):
    with r.urlopen(req) as f:
        decompressed_data =zlib.decompress(f.read(), 16 + zlib.MAX_WBITS)
    return str(decompressed_data, "utf-8", errors='replace')
        

def get_now_str():
    return int(float(time.time()) * 1000)


# 单个帖子页面

# 准备好目录
def prepare_folder(tid):
    try:
        os.makedirs(tid)
    except FileExistsError or OSError:
        print('!!!--error--!!! FileExists or OSError return')
        return
    #shutil.copytree('model/res', tid + '/res')
    shutil.copytree('./model/res','./'+tid+'/res')


# 把数据填充进去,造一个模版出来
def inflate_detail_model_with_data(base_info):
    with open('./model/model_detail.html', 'r', encoding='utf-8') as f:
        # parser = etree.HTMLParser()
        html_tree = BeautifulSoup(f, 'lxml')
        # return etree.parse(f.read(), parser=parser)

    meta = html_tree.head.select('meta[furl]')[0]
    meta['furl'] = base_info['meta_furl']
    meta['fname'] = base_info['meta_fname']

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
    html_str = get_response_str(req_maker('https://tieba.baidu.com/p/' + _tid))
    return BeautifulSoup(html_str, 'lxml')


def get_and_save_src(path, save_path):
    try:
        with r.urlopen(req_maker(path)) as f:
            with open(save_path, 'wb') as wf:
                wf.write(f.read())
    except BaseException:
        print('!!!--error--!!! error on download img src:', path)


def get_thread_basic_info(t_tid, t_fid):
    res = {}
    res['tid'] = t_tid
    res['fid'] = t_fid#ok
    
    html_tree = get_thread_basic_info_html(t_tid)

    # meta furl 我也不知道这个是拿来干嘛
    meta = html_tree.head.select('meta[furl]')
    res['meta_furl'] = meta[0].furl
    res['meta_fname'] = meta[0].fname
    
    # 标题
    res['title'] = html_tree.head.title.string.strip()
    #print(res['title'])

    # 贴吧头像部分 plat_card_top
    if html_tree.body.find('img', class_='card_head_img')==None:#有些旧版贴吧贴子有兼容问题，比如贴吧意见反馈吧的贴子
        temp = html_tree.body.find('a', class_='plat_picbox')
        res['card_head_img']=temp.find('img')['src']
    else:
        res['card_head_img'] = html_tree.body.find('img', class_='card_head_img')['src']
    #print(res['card_head_img'])

    # 下载贴吧头像文件
    # res['card_head_img_path'] = res['tid'] + '/' + urlparse(res['card_head_img']).path.split('/')[-1]
    # with open(res['card_head_img_path, 'wb') as img_src:
    #     img_src.write(get_src(res['card_head_img))

    if html_tree.body.find('div', class_='card_title')==None:#有些旧版贴吧贴子有兼容问题，比如贴吧意见反馈吧的贴子
        card_title =html_tree.body.find('div', class_='plat_use_total')
        # 贴吧名称
        res['card_title_fname'] = html_tree.body.find('a', class_='plat_title_h3').string.strip()
        #print(html_tree.body.find('a', class_='plat_title_h3'))
        # 关注和帖子数
        res['card_menNum'] = card_title.find_all('span',class_='plat_post_num')[0].string.strip()
        #print(card_title.find_all('span',class_='plat_post_num')[1].string)
        res['card_infoNum'] = card_title.find_all('span',class_='plat_post_num')[1].string.strip()
        # print(res['card_infoNum'])
    else:
        card_title =html_tree.body.find('div', class_='card_title')
        # 贴吧名称
        res['card_title_fname'] = card_title.find('a', class_='card_title_fname').string.strip()#有些旧版贴吧贴子有兼容问题，比如贴吧意见反馈吧的贴子
        #print(str(res))
        # 关注和帖子数
        res['card_menNum'] = card_title.find('span', class_='card_menNum').string.strip()#有些旧版贴吧贴子有兼容问题，比如贴吧意见反馈吧的贴子
        # print(res['card_menNum'])
        res['card_infoNum'] = card_title.find('span', class_='card_infoNum').string.strip()#有些旧版贴吧贴子有兼容问题，比如贴吧意见反馈吧的贴子
        # print(res['card_infoNum'])

    # 帖子页数,这个比较关键
    l_reply_num_nods = html_tree.find_all('li', class_='l_reply_num')
    for node in l_reply_num_nods:
        if len(node.contents) > 0:
            spans = node.find_all('span', class_='red')
            if len(spans) == 2:
                res['total_page'] = int(spans[1].string.strip())
    #print(res['total_page'])
    return res


# 实际内容和评论列表
def get_thread_by_page(base_info, page):
    html_str = get_response_str(req_maker('http://tieba.baidu.com/p/' + base_info['tid'] + "?ajax=1&pn=" + str(page)))
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


# http://tieba.baidu.com/p/comment?tid=xxxxx&pid=xxxxxxxxx&pn=2,这个一次给10条,不过这里会循环一直到取不到为止
# pid为楼层id

def get_comment_by_floor(tid, pid):
    go_on = True
    page = 1
    res = []
    while go_on:
        go_on = False
        html_str = get_response_str(
            req_maker('http://tieba.baidu.com/p/comment?tid=' + tid + "&pid=" + pid + '&pn=' + str(page)))#有&pn=是取不到内容的
        #print('http://tieba.baidu.com/p/comment?tid=' + tid + "&pid=" + pid + '&pn=' + str(page))
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
        time.sleep(1)

    block_tree = make_reply_block()
    block_tree_node = block_tree.find('ul')
    for add_node in res:
        block_tree_node.append(add_node)
    return block_tree


# 获取单个帖子,按页保存,能够哪个页面坏了删掉那一页重新跑就行
def get_single_thread(tid, fid, title_check,page2):

    if tid is None or fid is None:
        print('!!!--error--!!! lacking basic info, can not continue!')
        return

    thread_tid = tid
    thread_fid = fid
    base_dir = './'+thread_tid + '/'

    # 1.准备好目录
    print('1.prepare thread folder')
    prepare_folder(thread_tid)

    # 2.收集帖子基本信息
    print('2.get thread basic info')
    if os.path.exists(base_dir + 'base_info.json'):
        print('2.get thread basic info from json')
        with open(base_dir + 'base_info.json', 'r', encoding='utf-8') as base_info_file:
            info = json.load(base_info_file)

    else:
        print('2.get thread basic info from html')
        info = get_thread_basic_info(thread_tid, thread_fid)
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

        if not os.path.exists(base_dir + str(page) + '.html'):
            print('getting page:' + str(page))
            # 资源目录
            os.makedirs(base_dir + str(page))
            # 清除模版里的旧数据
            p_postlist = model.find('div', id='j_p_postlist')
            p_postlist.clear()
            thread_theme_5 = model.find('div', id='thread_theme_5')
            thread_theme_5.clear()
            thread_theme_7 = model.find('div', id='thread_theme_7')
            thread_theme_7.clear()
            headpic = model.find('div', class_='card_head')#找到包住吧头像的标签
            headpic2= model.find('img', class_='card_head_img')#先存着吧头像标签
            headpic.clear()#清空包住吧头像的标签
            temp=BeautifulSoup("<a href='"+"../../"+str(page2)+".html'>"+str(headpic2)+"</a>",'lxml')#为吧头像表情增加超链接
            headpic.append(temp)#重新添加回去
            baming = model.find('a', class_='card_title_fname')
            baming['href']='../../'+str(page2)+'.html'#点贴吧名字跳转到主题贴列表
            #tupiantie = get_thread_basic_info_html(thread_tid)#图片贴
            #tupiantie2=tupiantie.find('div', id='ag_container')#图片贴
            #thread_theme_5.append(tupiantie2)
            print('getting page detail ' + str(page))
            # 获取实际内容和评论列表
            content, comment_data = get_thread_by_page(info, page)
            
            # 列表的实际内容
            post_lists = content['content'].find_all('div', class_='l_post')
            for post in post_lists:
                # 取出post数据
                post_data_node = post.find('div', class_="j_d_post_content")
                
                post_data_node2 = post.find('span', class_="j_jb_ele") #解决举报按钮图片
                if post_data_node2:
                   post_data_node2.clear()
                
                post_data_node3 = post.find('span', class_="icon_wrap icon_wrap_theme1 d_pb_icons")#解决星座图片
                if post_data_node3:
                   post_data_node3.clear()

                post_data_node3 = post.find('div', class_="icon_relative").find("a")#解决头像框
                if post_data_node3:
                   post_data_node3['style']=None
                   
                post_data_node4 = post.find('div', class_="post_bubble_top")#
                if post_data_node4:
                   post_data_node4['style'] = None
                post_data_node5 = post.find('div', class_="post_bubble_middle")#
                if post_data_node5:
                   post_data_node5['style'] = None
                post_data_node6 = post.find('div', class_="post_bubble_bottom")#
                if post_data_node6:
                   post_data_node6['style'] = None

                post_data_node7 = post.find_all('img', class_="nicknameEmoji")#昵称,用find_all解决找到前面不找后面
                for temp in post_data_node7:
                    if temp:
                       emoji=temp['src'].split("/")
                       temp['src'] ="res/nickemoji/"+emoji[len(emoji)-1]

                   

                if post_data_node:
                    post_data_id = post_data_node['id'].split('_')[-1]
                    post_data_node_comment = post.find('div', class_="j_lzl_container")
                    if post_data_node_comment!=None:#有些旧版贴吧贴子有兼容问题，比如贴吧意见反馈吧的贴子
                        post_data_node_comment['data-field'] = None
                        post_data_node_comment['style'] = None
                        post_data_node_comment.clear()
                
                    # 送他礼物
                    share_btn_wrapper = post.find('div', class_="share_btn_wrapper")
                    if share_btn_wrapper:
                        share_btn_wrapper.clear()
                    if comment_data.get(post_data_id):
                        # 有评论
                        block_tree = get_comment_by_floor(thread_tid, post_data_id)
                        post_data_node_comment.append(block_tree)
                    p_postlist.append(post)   
                    print('adding a floor ' + str(page))
                else:
                    # 广告!!!
                    print('enconter an ad ' + str(page))

            print('dealing with up index ' + str(page))
            # 头部
            l_thread_info_up = content['up'].find('div', class_='l_thread_info')
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
                        print('!!!--error--!!! TypeError:' + a_node.prettify())
                    except ValueError:
                        print('!!!--error--!!! unknow page:' + a_node.string)
            thread_theme_5.append(l_thread_info_up)

            print('dealing with down index ' + str(page))
            # 尾部
            l_thread_info_down = content['down'].find('div', class_='l_thread_info')
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
                    except TypeError:
                        print('!!!--error--!!! TypeError:' + a_node.prettify())
                    except ValueError:
                        print('!!!--error--!!! unknow page:' + a_node.string)
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
                        #print(src_str+",66666666666")
                        #name=src_str.encode('utf-8')
                        #names1=str(name).split("/item/")#贴吧用户头像
                        #names2=str(name).split("%2Fitem%2F")#贴吧头像
                        #if(len(names1)>1):
                            #names3=names1[1].split("?t=")
                            #link_path = str(page) + '/' + names3[0] + '.jpg'
                            #print('666'+str(names3[0]))
                        #elif(len(names2)>1):
                            #names4=names2[1].split(".jpg'")
                            #link_path = str(page) + '/' + names4[0]+ '.jpg'
                            #print('777'+str(names4[0]))
                        md5 = hashlib.md5()#下载图片 https://blog.csdn.net/qq_38607035/article/details/82591931
                        md5.update(src_str.encode('utf-8'))
                        link_path = str(page) + '/' + md5.hexdigest() + '.jpg'
                        #//imgsa.baidu.com
                        #https://imgsrc.baidu.com/forum/pic/item/
                        if(src_str.find("//tiebapic.baidu.com/forum/")!=-1):#贴子里面的图片
                            sss2=src_str.split("/")
                            src_str="https://tiebapic.baidu.com/forum/pic/item/"+sss2[len(sss2)-1].split(".")[0]+".jpg"#解决签名档偶尔下载不到图片的问题
                            print(src_str)
                            link_path = str(page) + '/' + sss2[len(sss2)-1].split(".")[0]+".jpg"
                        elif(src_str.find("//imgsa.baidu.com/forum/")!=-1):
                            sss2=src_str.split("/")
                            src_str="https://imgsrc.baidu.com/forum/pic/item/"+sss2[len(sss2)-1].split(".")[0]+".jpg"#解决签名档偶尔下载不到图片的问题
                            print(src_str)
                            link_path = str(page) + '/' + sss2[len(sss2)-1].split(".")[0]+".jpg"
                        src_node['src'] = link_path
                        get_and_save_src(src_str, base_dir + link_path)
                        print(str(src_str)+str(base_dir)+str(link_path))
                        print('downloading no.' + str(count) + ' img ' + str(page))
                        count += 1
                        download_list[src_str] = link_path
            download_list.clear()
            # 完成,输出
            with open(base_dir + str(page) + '.html', 'w', encoding='utf-8') as f:
                f.write(str(write_model))
            print('done with page ' + str(page))
            time.sleep(10)#爬完一页后等待10秒再继续


# 有些地方需要登陆,所以cookie自己想办法弄吧

if __name__ == '__main__':
    cookie = ""#不能设为None,会报错
    get_single_thread('6160227969','4536','','1')#2017年以前的贴子正在陆续开放显示之前为暂时隐藏(贴吧吧) 贴子id(https://tieba.baidu.com/p/XXXXXXXX)，贴吧id(用开发者工具翻贴吧主题贴列表首页<head>里面的<script>标签,找‘// 吧的基本信息 PageData.forum’)，贴子名字(不用填)，返回指定页主题贴列表的页数。点击贴吧名返回指定页主题贴列表用（只爬一个贴子时可以不管）
    pass
'''
http://tieba.baidu.com/p/6351272485 【直播】11月15日问题反馈结果（贴吧意见反馈吧） 有bug，例如这个贴子不能获取每个的楼层时间
get_single_thread('6351272485','898666','','1')
楼层https://tieba.baidu.com/mo/q-----1-1-0----/flr?pid=XXXXX&kz=XXXXXXX&pn=0
楼中楼https://tieba.baidu.com/p/comment?tid=xxxxxx&pid=xxxxxxxx&pn=0
这是多行注释，用三个单引号
'''
