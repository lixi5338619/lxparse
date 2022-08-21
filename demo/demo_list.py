import requests
from lxparse import LxParse

headers={
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
}

# 简单的测试demo，返回列表页url
url_list = [
    'http://www.saiyuan-hp.com/news.asp',
    'https://www.greenwheel.com.cn/index/news/fid/128/cid/229.html#id',
    'http://www.levdeo.com/zh/news.html',
    'https://www.kaiyihome.com/perspective/news',
    'https://www.pncs.cn/News.aspx',
    'https://www.jht-design.com/xwdt',
    'https://www.ai-ways.com/news/',
    'http://www.hftc.com.cn/news.html',
    'http://www.kingsemi.com/xwzx/',
    'http://www.nsig.com/news',
    'http://www.siemenseda-pcb.cn/news',
    'http://www.hwatsing.com/xinwenzhongxin',
    'http://www.gokemicro.com/News/list.aspx',
    'http://www.gritek.com/6007.html',
    'http://www.hftc.com.cn/news.html',
    'http://www.kingsemi.com/xwzx/',
    'http://www.nsig.com/news',
    'http://www.siemenseda-pcb.cn/news',
    'https://blog.csdn.net/weixin_43582101',
    #'http://www.lxspider.com' # 一个错误示例
]

lx = LxParse()

for url in url_list:
    html=requests.get(url,headers=headers).text
    detail_url_list = lx.parse_list(html,article_nums=4)
    # 需要注意，parse_domain 方法不一定准确
    urls = [lx.parse_domain(detail_url,url) for detail_url in detail_url_list]
    print(urls)
