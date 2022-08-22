# -*- coding: utf-8 -*-
from lxparse.readability import Document
from lxml import etree
from html import unescape

class ContentExtractor:
    def extractor(self, html, content_xpath):
        element = etree.HTML(html)
        if content_xpath:
            body = element.xpath(content_xpath)
            if body:
                content = unescape(etree.tostring(body[0], encoding='utf-8').decode())
                return content
        doc = Document(html)
        return doc.summary()
