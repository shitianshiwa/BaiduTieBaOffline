# BaiduTieBaOffline
python贴吧爬虫玩具，把整个贴吧html（除了我认为不需要的，比如广告＝。＝，不愧是某厂，这东西一点都不少）都爬下来，保留基本贴吧页面样式

分为两个部分，爬取贴吧帖子列表和爬取单个帖子所有楼层，保存为本地html包括资源，提供两个模版，基本照着贴吧的样式

帖子列表由于是bigpipe动态加载的，所以用了selenium＋PhantomJS，请保证这两个东西事先装好，跑程序只用传入贴吧首页地址即可，跑完之后会生成贴吧名字的文件夹，里面有1～n页的帖子列表页内容（只是列表页）

帖子详情页由于没有用bigpipe所以直接用urllib请求的，但是需要登录cookie所以这个自己搞个账号自己抓包吧，模拟登陆目前没做，跑程序需要贴吧id和帖子id，可以在帖子第一页源代码里找，或者列表页模块生成出列表页之后也会爬出这些数据，程序跑完之后会生成帖子id的文件夹，里面有帖子第1～n页的所有内容

你也可以在保证selenium＋PhantomJS和登陆cookie的情况下直接传一个贴吧首页地址，它能把整个贴吧爬下来，之后大概长这样(杰钢队长吧为例):

列表页:
页头
![image](https://github.com/ytinrete/BaiduTieBaOffline/raw/master/show_pic/l1.png)
页尾巴
![image](https://github.com/ytinrete/BaiduTieBaOffline/raw/master/show_pic/l2.png)
第二页头
![image](https://github.com/ytinrete/BaiduTieBaOffline/raw/master/show_pic/l3.png)

详情页:
头部
![image](https://github.com/ytinrete/BaiduTieBaOffline/raw/master/show_pic/d1.png)
评论也被爬下来的，但是没有分页，直接有多少贴多少这样
![image](https://github.com/ytinrete/BaiduTieBaOffline/raw/master/show_pic/d2.png)

(本来想拿一两页样本放git上不过两页就100+M。。。,因为包括所有帖子内容,这么大不奇怪,所以还是算了)

## (我只是随便选取的页面,要是你是其中某人而不想被帖在这些图里,给我发邮件立即就删)

无论是列表模块还是详情模块都能根据已知的进度继续爬,所以要是出错了删掉最新的那一页,再继续运行就好,对于要爬整个贴吧还有问题,我请求的时候是不带时间参数的,若是很活跃的贴吧估计帖子数可能会有出入,重复,少掉等这些都不好说,这一部分要优化还得做一些工作,但是我没有这样的需求呀

上面爬下来的都是带资源和做好下一页跳转修正的，也就是基本可以当作拿到整个离线内容了，爬完之后用浏览器就能在本地看帖了，然而并没有什么意义，写这个只是拿来保存我的个人贴吧而已XD

这个玩具爬比较简单的小贴吧应该是没有多大问题（比如说我自己的那个），其他可能会出问题，特别是里面抓取数据代码写的不够灵活，很多地方可以用多线程去做也没做，没优化，因为对我而言也够用了，之后百度api改了那也没办法，总之我已经玩够了2333，不过要真有人用这个遇到问题随时欢迎讨论 --2016.8.25

special thanks:
曾经一起度过美好时光的贴吧吧友们～

---
图片内容可使用tiebapic.baidu.com/forum/pic/item/或者imgsrc.baidu.com/forum/pic/item/+图片名字 去查询

使用的第三方库或软件：

python3 -m pip install selenium==2.53.6（这个版本很低，如果以后换浏览器记得升级下）

PhantomJS（https://github.com/ariya/phantomjs） ，下载后放在python根目录的Scripts文件夹里。这是一个不显示内容的浏览器

python3 -m pip install beautifulsoup4

python3 -m pip install lxml

python3 -m pip install --upgrade pip

//pip3 install --upgrade pip

python版本：Python 3.5.1/3.6.8

单个贴子删除base_info.json文件可以继续更新（注意备份，防止因为原贴已被删除导致丢失了 ）

获取楼层失败可以通过删除失败的楼层文件夹来解决

要爬取单个贴子的话，修改get_single_thread.py里的get_single_thread('贴子id（数字，贴子链接后面的数字）','','','1')即可（支持多行）

要爬取整个贴吧的话，修改get_forum_all.py里的my_url = "https://tieba.baidu.com/f?ie=utf-8&kw=xxxxxxxxxxxx"即可（支持多行）

2020-2-25


