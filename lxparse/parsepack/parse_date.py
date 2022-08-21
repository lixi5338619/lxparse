# -*- coding: utf-8 -*-

import re
from lxml.html import HtmlElement
import datetime
from lxpy import DateGo



class DateExtractor:
    def __init__(self):
        self.DATETIME_PATTERN = [
            "(\d{4}[-|/|.]\d{1,2}[-|/|.]\d{1,2}\s*?[0-1]?[0-9]:[0-5]?[0-9]:[0-5]?[0-9])",
            "(\d{4}[-|/|.]\d{1,2}[-|/|.]\d{1,2}\s*?[2][0-3]:[0-5]?[0-9]:[0-5]?[0-9])",
            "(\d{4}[-|/|.]\d{1,2}[-|/|.]\d{1,2}\s*?[0-1]?[0-9]:[0-5]?[0-9])",
            "(\d{4}[-|/|.]\d{1,2}[-|/|.]\d{1,2}\s*?[2][0-3]:[0-5]?[0-9])",
            "(\d{4}[-|/|.]\d{1,2}[-|/|.]\d{1,2}\s*?[1-24]\d时[0-60]\d分)([1-24]\d时)",
            "(\d{2}[-|/|.]\d{1,2}[-|/|.]\d{1,2}\s*?[0-1]?[0-9]:[0-5]?[0-9]:[0-5]?[0-9])",
            "(\d{2}[-|/|.]\d{1,2}[-|/|.]\d{1,2}\s*?[2][0-3]:[0-5]?[0-9]:[0-5]?[0-9])",
            "(\d{2}[-|/|.]\d{1,2}[-|/|.]\d{1,2}\s*?[0-1]?[0-9]:[0-5]?[0-9])",
            "(\d{2}[-|/|.]\d{1,2}[-|/|.]\d{1,2}\s*?[2][0-3]:[0-5]?[0-9])",
            "(\d{2}[-|/|.]\d{1,2}[-|/|.]\d{1,2}\s*?[1-24]\d时[0-60]\d分)([1-24]\d时)",
            "(\d{4}年\d{1,2}月\d{1,2}日\s*?[0-1]?[0-9]:[0-5]?[0-9]:[0-5]?[0-9])",
            "(\d{4}年\d{1,2}月\d{1,2}日\s*?[2][0-3]:[0-5]?[0-9]:[0-5]?[0-9])",
            "(\d{4}年\d{1,2}月\d{1,2}日\s*?[0-1]?[0-9]:[0-5]?[0-9])",
            "(\d{4}年\d{1,2}月\d{1,2}日\s*?[2][0-3]:[0-5]?[0-9])",
            "(\d{4}年\d{1,2}月\d{1,2}日\s*?[1-24]\d时[0-60]\d分)([1-24]\d时)",
            "(\d{2}年\d{1,2}月\d{1,2}日\s*?[0-1]?[0-9]:[0-5]?[0-9]:[0-5]?[0-9])",
            "(\d{2}年\d{1,2}月\d{1,2}日\s*?[2][0-3]:[0-5]?[0-9]:[0-5]?[0-9])",
            "(\d{2}年\d{1,2}月\d{1,2}日\s*?[0-1]?[0-9]:[0-5]?[0-9])",
            "(\d{2}年\d{1,2}月\d{1,2}日\s*?[2][0-3]:[0-5]?[0-9])",
            "(\d{2}年\d{1,2}月\d{1,2}日\s*?[1-24]\d时[0-60]\d分)([1-24]\d时)",
            "(\d{1,2}月\d{1,2}日\s*?[0-1]?[0-9]:[0-5]?[0-9]:[0-5]?[0-9])",
            "(\d{1,2}月\d{1,2}日\s*?[2][0-3]:[0-5]?[0-9]:[0-5]?[0-9])",
            "(\d{1,2}月\d{1,2}日\s*?[0-1]?[0-9]:[0-5]?[0-9])",
            "(\d{1,2}月\d{1,2}日\s*?[2][0-3]:[0-5]?[0-9])",
            "(\d{1,2}月\d{1,2}日\s*?[1-24]\d时[0-60]\d分)([1-24]\d时)",
            "(\d{4}年\d{1,2}月\d{1,2}日)",
            "(\d{2}年\d{1,2}月\d{1,2}日)",
            "(\d{1,2}月\d{1,2}日)",
            "(\d{4}[-|/|.]\d{1,2}[-|/|.]\d{1,2})",
            "(\d{2}[-|/|.]\d{1,2}[-|/|.]\d{1,2})",
            "(\d\d [a-zA-Z]{3,10} \d{4})"  # 英文时间 28 February 2022
        ]
        self.PUBLISH_TIME_META = [
            '//meta[starts-with(@property, "rnews:datePublished")]/@content',
            '//meta[starts-with(@property, "article:published_time")]/@content',
            '//meta[starts-with(@property, "og:published_time")]/@content',
            '//meta[starts-with(@property, "og:release_date")]/@content',
            '//meta[starts-with(@itemprop, "datePublished")]/@content',
            '//meta[starts-with(@itemprop, "dateUpdate")]/@content',
            '//meta[starts-with(@name, "OriginalPublicationDate")]/@content',
            '//meta[starts-with(@name, "article_date_original")]/@content',
            '//meta[starts-with(@name, "og:time")]/@content',
            '//meta[starts-with(@name, "apub:time")]/@content',
            '//meta[starts-with(@name, "publication_date")]/@content',
            '//meta[starts-with(@name, "sailthru.date")]/@content',
            '//meta[starts-with(@name, "PublishDate")]/@content',
            '//meta[starts-with(@name, "publishdate")]/@content',
            '//meta[starts-with(@name, "PubDate")]/@content',
            '//meta[starts-with(@name, "pubtime")]/@content',
            '//meta[starts-with(@name, "_pubtime")]/@content',
            '//meta[starts-with(@name, "weibo: article:create_at")]/@content',
            '//meta[starts-with(@pubdate, "pubdate")]/@content',
        ]

    def extractor(self, element: HtmlElement, date_xpath) -> str:
        publish_time = (self.extract_from_user_xpath(date_xpath, element)
                        or self.extract_from_meta(element)
                        or self.extract_from_text(element))
        return publish_tools(publish_time)


    def extract_from_user_xpath(self, publish_time_xpath: str, element: HtmlElement) -> str:
        if publish_time_xpath:
            publish_time = ''.join(element.xpath(publish_time_xpath))
            return publish_time
        return ''


    def extract_from_text(self, element: HtmlElement) -> str:
        text = ''.join(element.xpath('.//text()'))
        for dt in self.DATETIME_PATTERN:
            dt_obj = re.search(dt, text)
            if dt_obj:
                return dt_obj.group(1)
        else:
            return ''


    def extract_from_meta(self, element: HtmlElement) -> str:
        for xpath in self.PUBLISH_TIME_META:
            publish_time = element.xpath(xpath)
            if publish_time:
                return ''.join(publish_time)
        return ''


def validate_datetime(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d %H:%M:%S')
        return date_text
    except:
        return None


def publish_tools(publish_time:str):
    """
    desc: 处理那些奇怪的时间
    :return: 返回日期时间格式
    """
    if not publish_time:
        return
    publish_time = publish_time.replace('\n\t\t\t\t\t\t\t\t',' ').replace('\n','').rstrip().lstrip()
    publish_time = publish_time.replace('Februaryruary','February').replace('uesday,','').replace('hursday,','').replace(' 12:00pm','')
    publish_time = publish_time.replace('Februar ','February ').replace('Januar ','January ').replace('März ','March ').replace('juni ','January ').replace('Marchch ','March ').replace('Sept ','September ')
    publish_time = publish_time.replace(' Jan ', ' January ').replace(' Feb ', ' February ').replace(' Mar ', ' March ').replace(' Apr ', ' April ').replace(' May ', ' May ').replace(' Jun ', ' June ').replace(' Jul ', ' July ').replace(' Aug ', ' August ').replace(' Sept ',' September ').replace(' Oct ', ' October ').replace(' Nov ', ' November ').replace(' Dec ', ' December ').replace(' Sep ', ' September ')
    publish_time = publish_time.replace(' Juli ',' July ').replace(' juni ',' June ')
    month = {
        'Jan': 'January',
        'Feb': 'February',
        'Mar': 'March',
        'Apr': 'April',
        'May': 'May',
        'Jun': 'June',
        'Jul': 'July',
        'Aug': 'August',
        'Sept': 'September',
        'Oct': 'October',
        'Nov': 'November',
        'Dec': 'December',
        'Sep': 'September',
    }
    if publish_time[0].isupper() and publish_time[:3].isalpha() and publish_time[3]==' ':
        try:
            publish_time = month[publish_time[:3]]+publish_time[3:]
            publish_time = datetime.datetime.strptime(publish_time, '%B %d, %Y')
            return str(publish_time)
        except:return publish_time

    if ' PM EST' in publish_time or ' AM EST' in publish_time:
        publish_time = publish_time.replace(' PM EST','').replace('on ','').replace(' AM EST','')
        publish_time = datetime.datetime.strptime(publish_time, '%B %d, %Y %H:%M')
        return str(publish_time)
    if ' AM' in publish_time:
        publish_time = publish_time.replace(' AM', '')
        if re.findall('\d\d/\d\d/\d{4} \d\d:\d\d',publish_time):
            publish_time = datetime.datetime.strptime(publish_time, '%m/%d/%Y %H:%M')
            return publish_time
        else:
            publish_time = datetime.datetime.strptime(publish_time, '%d/%m/%Y  %H:%M')
            return str(publish_time)
    if ' PM' in publish_time:
        publish_time = publish_time.replace(' PM','')
        publish_time = datetime.datetime.strptime(publish_time, '%d/%m/%Y  %H:%M')
        return str(publish_time)
    if ' EST' in publish_time:
        publish_time = publish_time.replace(' EST','').replace('on ','')
        publish_time = datetime.datetime.strptime(publish_time, '%B %d, %Y %H:%M')
        return publish_time

    try:
        if re.findall('\w+ \d\d, \d{4}, \d\d:\d\d',publish_time):
            # Monday, December 20, 2021, 10:05
            publish_time = publish_time.split(', ', 1)[1][:-7]
        if re.findall('\d\d\. [a-zA-Z]+ \d{4}',publish_time):
            publish_time = publish_time.replace('.','')
            publish_time = datetime.datetime.strptime(publish_time, '%d %B %Y')
            return str(publish_time)
        if re.findall('\d{1,2} [a-zA-Z]+ \d{4}',publish_time):
            publish_time = datetime.datetime.strptime(publish_time, '%d %B %Y')
            return str(publish_time)
        if re.findall('^[a-zA-Z]+ \d\d, \d{4}',publish_time):
            publish_time = datetime.datetime.strptime(publish_time, '%B %d, %Y')
            return str(publish_time)
        if re.findall('^[a-zA-Z]+ \d{1,2}, \d{4}',publish_time):
            publish_time = datetime.datetime.strptime(publish_time, '%B %d, %Y')
            return str(publish_time)
        if re.findall('^[a-zA-Z]+- \d{1,2}, \d{4}',publish_time):
            publish_time = publish_time.replace('-','')
            publish_time = datetime.datetime.strptime(publish_time, '%B %d, %Y')
            return str(publish_time)
        if re.findall('^[a-zA-Z]+, [a-zA-Z]+ \d{1,2}, \d{4}',publish_time):
            publish_time = publish_time.split(',',1)[1].lstrip()
            publish_time = datetime.datetime.strptime(publish_time, '%B %d, %Y')
            return str(publish_time)
        if re.findall('\d{2}-\w{3}-\d{4}',publish_time):
            publish_time = publish_time[:3]+month[publish_time[3:6]]+publish_time[6:]
            publish_time = datetime.datetime.strptime(publish_time, '%d-%B-%Y')
            return str(publish_time)
    except:
        ...

    if '日期：' in publish_time and '　来源：' in publish_time:
        publish_time = publish_time.split('　来源：')[0].replace('日期：','')
    elif '发布时间：' in publish_time and '&nbsp;&nbsp;|&nbsp;&nbsp;' in publish_time:
        publish_time = publish_time.split('&nbsp;&nbsp;|&nbsp;&nbsp;')[0].replace('发布时间：','')
    elif '发布时间 ：' in publish_time:
        publish_time = publish_time.replace('发布时间 ：','')
    elif '发布时间 :' in publish_time:
        publish_time = publish_time.split('发布时间 :')[1]
    elif '发布时间：' in publish_time and '  |  来源：' in publish_time:
        publish_time = publish_time.split('  |  来源')[0].replace('发布时间：','')
    elif '政策发布时间：' in publish_time:
        publish_time = publish_time.replace('政策发布时间：','')
    elif '来源：' in publish_time and '发布者：' in publish_time and '期：' in publish_time:
        publish_time = publish_time.split('期：')[1]
    elif '信息来源：教科办' in publish_time and '浏览次数：' in publish_time:
        publish_time = publish_time.split('时间：')[1].split('浏览次数')[0].rstrip()
    elif '发布于：' in publish_time and re.findall('\d{4} - \d\d - \d\d \d\d : \d\d',publish_time):
        publish_time = publish_time.replace('发布于：','').replace(' ','')
        publish_time = publish_time[:10]+' '+publish_time[10:]
    elif '来源：' in publish_time and re.findall('\d{4}-\d\d-\d\d \d\d:\d\d:\d\d来源：',publish_time):
        publish_time = publish_time.replace('来源：','')
    elif re.findall('发布日期：.*?年.*?月.*?日', publish_time):
        return publish_tools(''.join(re.findall('发布日期：(.*?年.*?月.*?日)', publish_time)))


    publish_time = publish_time.replace('年', '-').replace('月', '-').replace('日', '').replace('/', '-')
    publish_time = publish_time.replace('T',' ').replace('Z','').replace('.','-').replace('∶',':')
    publish_time = publish_time.replace('.000Z','')

    if len(publish_time)>19:
        # .replace('+00:00','').replace('+0000','').replace('+0200','').replace('+0400','').replace('+01:00','').replace('-05:00','')
        jiajian = re.findall('\+\d\d:\d\d|\-\d\d:\d\d|\+\d{4,}|\-\d{4,}|\-\d{3,}',publish_time)
        if jiajian:
            publish_time = publish_time.replace(jiajian[0],'')
        publish_time = publish_time.replace('-000','').replace('+0800','')


    year = str(datetime.datetime.now().year)
    if len(publish_time) == 10:
        if re.findall('\d{4}-\d\d-\d\d',publish_time):
            publish_time += ' 00:00:00'
        elif re.findall('\d\d-\d\d-\d{4}',publish_time):
            if int(publish_time[:2])>12 or int(publish_time[3:5])>31:
                return None
            else:
                publish_time += ' 00:00:00'
    elif len(publish_time) == 3 and re.findall('\d-\d',publish_time):
        p = publish_time.split('-')
        publish_time = f'{year}-0{p[0]}-0{p[1]} 00:00:00'
    elif len(publish_time) == 4 and re.findall('\d-\d\d',publish_time):
        p = publish_time.split('-')
        publish_time = f'{year}-0{p[0]}-{p[1]} 00:00:00'
    elif len(publish_time) == 4 and re.findall('\d\d-\d',publish_time):
        p = publish_time.split('-')
        year = datetime.datetime.now().year
        publish_time = f'{year}-{p[0]}-0{p[1]} 00:00:00'
    elif len(publish_time) == 5 and re.findall('\d\d-\d\d',publish_time):
        p = publish_time.split('-')
        year = datetime.datetime.now().year
        publish_time = f'{year}-{p[0]}-{p[1]} 00:00:00'
    elif len(publish_time)==8:
        if re.findall('\d\d-\d\d-\d\d',publish_time):
            publish_time = year+'-'+publish_time[:5]+' 00:00:00'
        elif re.findall('\d{4}-\d-\d',publish_time):
            publish_time = publish_time[:5] + '0' + publish_time[5] + '-' +'0' +publish_time[7]+' 00:00:00'
    elif len(publish_time) == 16:
        if re.findall('\d{4}-\d\d-\d\d \d\d:\d\d',publish_time):
            publish_time += ':00'
        elif re.findall('\d{4}-\d-\d \d:\d\d:\d\d',publish_time):
            publish_time = publish_time[:5]+'0'+publish_time[5:7]+'0'+publish_time[7:9]+'0'+publish_time[9:]

    elif len(publish_time)==14:
        if re.findall('\d{4}-\d-\d \d{2}:\d{2}',publish_time):
            publish_time = publish_time[:5] + '0' + publish_time[5] + '-'+'0'+publish_time[7:]+':00'
        elif re.findall('\d\d-\d\d-\d\d \d\d:\d',publish_time):
            publish_time = '20'+ publish_time+':00'
    elif len(publish_time)==17:
        if re.findall('\d{4}-\d-\d \d{2}',publish_time):
            publish_time = publish_time[:5] + '0' + publish_time[5] + '-'+'0'+publish_time[7:]
        elif re.findall('\d{4}-\d-\d{2} \d{1}:',publish_time):
            publish_time = publish_time[:5] + '0' + publish_time[5:10] + '0'+publish_time[10:]
        elif re.findall('\d{4}-\d{2}-\d \d{1}:',publish_time):
            publish_time = publish_time[:8] + '0' + publish_time[8] + ' 0'+ publish_time[10:]
    elif len(publish_time)==18:
        if re.findall('\d{4}-\d-\d\d \d{2}',publish_time):
            publish_time = publish_time[:5] + '0' + publish_time[5:]
        elif re.findall('\d{4}-\d\d-\d \d{2}',publish_time):
            publish_time = publish_time[:8] + '0' +publish_time[8:]
    elif len(publish_time) == 15:
        if re.findall('\d{4}-\d-\d\d.*?', publish_time):
            publish_time = publish_time[:5] + '0' + publish_time[5:] + ':00'
        elif re.findall('\d{4}-\d\d-\d ', publish_time):
            publish_time = publish_time[:8] + '0' + publish_time[8:] + ':00'
    elif len(publish_time) == 9:
        if re.findall('\d{4}-\d-.*?', publish_time):
            publish_time = publish_time[:5] + '0' + publish_time[5:] + ' 00:00:00'
        elif re.findall('\d{4}-\d\d-.*?', publish_time):
            publish_time = publish_time[:8] + '0' + publish_time[8:] + ' 00:00:00'
    elif len(publish_time) == 25:
        if 'T' in publish_time:
            publish_time = publish_time[:-6].replace('T', ' ')
        elif re.findall('\d\d-\d\d-\d{4} - \d\d:\d\d',publish_time):
            res = re.findall('(\d\d-\d\d)-(\d{4}) - (\d\d:\d\d)',publish_time)[0]
            publish_time = res[1]+'-'+res[0]+' '+res[2]+':00'
        elif re.findall('\d{4}-\d\d-\d\d \d\d:\d\d:\d\d-\d{4}',publish_time):
            publish_time = publish_time[:-5]
    elif len(publish_time) == 32:
        if re.findall('\d{4}-\d\d-\d\d \d\d:\d{6}-\d\d-\d\d',publish_time):
            publish_time = publish_time[:16]+':00'
    elif len(publish_time)==44:
        publish_time = publish_time[:19]


    est = re.findall('on (.*? \d, \d{4}) ', publish_time)
    if est:
        publish_time = str(datetime.datetime.strptime(est[0], '%B %d, %Y'))

    if '天前' in publish_time or '周前' in publish_time or '月前' in publish_time or '小时前' in publish_time or '分钟前' in publish_time or '刚刚' in publish_time:
        return DateGo.youku_date(publish_time)

    return validate_datetime(str(publish_time))