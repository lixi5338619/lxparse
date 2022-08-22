# -*- coding: utf-8 -*-
# Author: lx
# Website: lxspider.com
# Wechat official account: Pythonlx

from lxml import etree
from lxpy import html_format
from lxparse.parsepack import *

# Resolution ListURL and ArticleDetail.

class LxParse():
    def __init__(self):
        self.html = None
        self.element = None


    def parse_list(self,html,xpath_list=None,article_nums=7,link_nums=150):
        """
           xpath_list : self specified list xpath
           article_nums : Number of list page URLs
           link_nums : ListPage MAX Links
        """
        result = list_parse.extractor(html,xpath_list,article_nums,link_nums)
        return result


    def parse_detail(self,html,item={}):
        """
            item: self specified list xpath
                  (xpath_title、xpath_source、xpath_date、xpath_author、xpath_content)
        """
        self.html = html
        self.element = etree.HTML(html)
        result = {}
        result['title'] = title_parse.extractor(self.element,title_xpath=item.get('xpath_title'))
        result['author'] = author_parse.extractor(self.element,author_xpath=item.get('xpath_author'))
        result['date'] = date_parse.extractor(self.element,date_xpath=item.get('xpath_date'))
        result['sources'] = source_parse.extractor(self.element,source_xpath=item.get('xpath_source'))
        result['content'] = content_parse.extractor(self.html,content_xpath=item.get('xpath_content'))
        result['content_format'] = html_format(result['content'])
        return result


    def parse_domain(self,detail_url,index_url):
        """
            detail_url : detail page url
            index_url  : website url
        """
        return parse_loc(detail_url,index_url)
