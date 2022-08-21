# -*- coding: utf-8 -*-
import re

class AuthorExtractor:
    def __init__(self):
        self.AUTHOR_PATTERN = [
            "作者[：|:| |丨|/]\s*([\u4E00-\u9FA5a-zA-Z]{2,20})[^\u4E00-\u9FA5|:|：]",
            "责编[：|:| |丨|/]\s*([\u4E00-\u9FA5a-zA-Z]{2,20})[^\u4E00-\u9FA5|:|：]",
            "责任编辑[：|:| |丨|/]\s*([\u4E00-\u9FA5a-zA-Z]{2,20})[^\u4E00-\u9FA5|:|：]",
            "编辑[：|:| |丨|/]\s*([\u4E00-\u9FA5a-zA-Z]{2,20})[^\u4E00-\u9FA5|:|：]",
            "原创[：|:| |丨|/]\s*([\u4E00-\u9FA5a-zA-Z]{2,20})[^\u4E00-\u9FA5|:|：]",
            "撰文[：|:| |丨|/]\s*([\u4E00-\u9FA5a-zA-Z]{2,20})[^\u4E00-\u9FA5|:|：]",
            "来源[：|:| |丨|/]\s*([\u4E00-\u9FA5a-zA-Z]{2,20})[^\u4E00-\u9FA5|:|：|<]",
    ]

    def extractor(self, element, author_xpath):
        if author_xpath:
            author = ''.join(element.xpath(author_xpath))
            return author
        text = ''.join(element.xpath('.//text()'))
        for pattern in self.AUTHOR_PATTERN:
            author_obj = re.search(pattern, text)
            if author_obj:
                return author_obj.group(1)
        return ''


class SourceExtractor:
    def __init__(self):
        self.SOURCE_PATTERN = [
            "来源[：|:| |丨|/]\s*([\u4E00-\u9FA5a-zA-Z]{2,20})[^\u4E00-\u9FA5|:|：|<]",
            "原创[：|:| |丨|/]\s*([\u4E00-\u9FA5a-zA-Z]{2,20})[^\u4E00-\u9FA5|:|：]",
            "撰文[：|:| |丨|/]\s*([\u4E00-\u9FA5a-zA-Z]{2,20})[^\u4E00-\u9FA5|:|：]",
            '(原创[：|:| |丨|/]\%s*[\u4E00-\u9FA5a-zA-Z、 ]{2,20})[）】)]]?[^\u4E00-\u9FA5|:|：]',
        ]

    def extractor(self, element, source_xpath):
        if source_xpath:
            author = ''.join(element.xpath(source_xpath))
            return author
        text = ''.join(element.xpath('.//text()'))
        for pattern in self.SOURCE_PATTERN:
            author_obj = re.search(pattern, text)
            if author_obj:
                return author_obj.group(1)
        return ''