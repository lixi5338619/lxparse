import requests
from lxparse import LxParse

headers={
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
}

# 测试demo，返回详情页内容
url_list = [
    'https://news.gmw.cn/2022-08/20/content_35966384.htm',
    'https://blog.csdn.net/weixin_43582101/article/details/122611705?',
    'http://www.lxspider.com/?p=121',
    'https://www.pncs.cn/News/2020-01-16/82.aspx',
    'http://www.gritek.com/s/7031-16390-640274.html',
    'http://www.nsig.com/news/20',
    'http://www.gokemicro.com/News/info.aspx?itemid=285',
    'https://legal.gmw.cn/2022-08/19/content_35964299.htm'
    'https://blog.51cto.com/lixi/5257464',
    'https://www.cnblogs.com/stars-one/p/16592706.html'
]

lx = LxParse()

for url in url_list:
    res=requests.get(url,headers=headers)
    res.encoding = res.apparent_encoding
    print(lx.parse_detail(res.text))
