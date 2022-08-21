# -*- coding: utf-8 -*-


import re
import string
from html import unescape


class StringReplacement():
    def __init__(self, pattern, replaceWith):
        self.pattern = pattern
        self.replaceWith = replaceWith

    def replaceAll(self, string):
        if not string:
            return ''
        return string.replace(self.pattern, self.replaceWith)


class TitleExtractor():
    def getElementsByTag(self,node, tag=None, attr=None, value=None, childs=False, use_regex=False) -> list:
        # descendant-or-self 选取当前节点的所有后代元素（子、孙等）以及当前节点本身
        selector = 'descendant-or-self::%s' % (tag or '*')
        if attr and value:
            if use_regex:
                selector = '%s[re:test(@%s, "%s", "i")]' % (selector, attr, value)
            else:
                trans = 'translate(@%s, "%s", "%s")' % (attr, string.ascii_uppercase, string.ascii_lowercase)
                selector = '%s[contains(%s, "%s")]' % (selector, trans, value.lower())

        elems = node.xpath(selector)

        if node in elems and (tag or childs):
            elems.remove(node)
        return elems


    def innerTrim(self,value):
        if isinstance(value, str):
            value = re.sub(re.compile(r'[\s\t]+'), ' ', value)
            value = ''.join(value.splitlines())
            return value.strip()
        return ''


    def getText(self,node):
        txts = [i for i in node.itertext()]
        return self.innerTrim(' '.join(txts).strip())


    def getAttribute(self,node, attr=None):
        if attr:
            attr = node.attrib.get(attr, None)
        if attr:
            attr = unescape(attr)
        return attr


    def get_meta_content(self,doc, metaname):

        meta = doc.cssselect(metaname)
        content = None
        if meta is not None and len(meta) > 0:
            content = self.getAttribute(meta[0], 'content')
        if content:
            return content.strip()
        return ''


    def get_title(self,doc,h1_priority=False):
        title,filter_title_text,title_text_h1 = '','',''
        title_text = False
        title_element = self.getElementsByTag(doc, tag='title')
        filter_regex = re.compile(r'[^\u4e00-\u9fa5a-zA-Z0-9\ ]')

        if title_element or len(title_element) != 0:
            title_text = self.getText(title_element[0])
            filter_title_text = filter_regex.sub('', title_text).lower()


        title_element_h1_list = self.getElementsByTag(doc,tag='h1') or []
        title_text_h1_list = [self.getText(tag) for tag in
                              title_element_h1_list]

        title_text_fb = (
        self.get_meta_content(doc, 'meta[property="og:title"]') or
        self.get_meta_content(doc, 'meta[name="og:title"]') or '')


        if title_text_h1_list:
            title_text_h1_list.sort(key=len, reverse=True)
            title_text_h1 = title_text_h1_list[0]

            if title_element or title_text_fb:
                if not h1_priority and len(title_text_h1.split(' ')) <= 2:
                    title_text_h1 = ''

            title_text_h1 = ' '.join([x for x in title_text_h1.split() if x])


        if not title_element and not title_text_h1_list and not title_text_fb:
            return

        filter_title_text_h1 = filter_regex.sub('', title_text_h1).lower()
        filter_title_text_fb = filter_regex.sub('', title_text_fb).lower()


        # 筛选更好的 title 方案

        # 如果 title 和 title_text_h1 和相同
        if title_text and title_text_h1 == title_text:
            title_text = title_text

        # 如果 h1 和 fb 相同
        elif filter_title_text_h1 and filter_title_text_h1 == filter_title_text_fb:
            title_text = title_text_h1

        elif filter_title_text_h1 and filter_title_text_h1 in filter_title_text \
                and filter_title_text_fb and filter_title_text_fb in filter_title_text \
                and len(title_text_h1) > len(title_text_fb):
            title_text = title_text_h1

        elif filter_title_text_h1 and filter_title_text_h1 in filter_title_text and len(title_text_h1) < len(title_text_fb):
            title_text = title_text_h1

        elif filter_title_text_fb and filter_title_text_fb != filter_title_text \
                and filter_title_text.startswith(filter_title_text_fb):
            title_text = title_text_fb

        # 如果h1 和 fb 都存在，并且h1比fb完整 则选h1
        elif filter_title_text_h1 and filter_title_text_fb and len(title_text_h1) > len(title_text_fb):
            title_text = title_text_h1

        # 如果 fb 存在，则选fb
        elif filter_title_text_fb and filter_title_text_fb != filter_title_text:
            title_text = title_text_fb


        elif filter_title_text_h1 and filter_title_text_h1 != filter_title_text:
            title_text = title_text_h1


        MOTLEY_REPLACEMENT = StringReplacement("&#65533;", "")
        title = MOTLEY_REPLACEMENT.replaceAll(title_text)

        # 在某些情况下，最终的标题非常类似于title_text_h1
        filter_title = filter_regex.sub('', title).lower()
        if filter_title_text_h1 == filter_title:
            title = title_text_h1
        return title


    def extractor(self,element,title_xpath):
        if title_xpath:
            title = ''.join(element.xpath(title_xpath))
            return title
        title = ''.join(element.xpath('//meta[@name="ArticleTitle"]/@content'))
        if not title:
            title = self.get_title(element,h1_priority=True)
        if title and len(title)<10:
           title_list = element.xpath('(//h1//text() | //h2//text() | //h3//text())')
           if title_list:title = title_list[0]
        return title