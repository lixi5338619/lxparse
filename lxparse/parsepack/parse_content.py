# -*- coding: utf-8 -*-

from lxparse.readability import Document
from lxml import etree

class ContentExtractor:
    def extractor(self, html, content_xpath):
        element = etree.HTML(html)
        if content_xpath:
            content = ''.join(element.xpath(content_xpath))
            return content
        doc = Document(html)
        return doc.summary()
