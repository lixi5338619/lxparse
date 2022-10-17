# -*- coding: utf-8 -*-

from lxparse.readability import Document
from lxml import etree
from html import unescape

class ContentExtractor:
    def extractor(self, html, content_xpath):
        element = etree.HTML(html)
        if content_xpath:
            contentElement = element.xpath(content_xpath)
            content = ''
            for body in contentElement:
                body_html = unescape(etree.tostring(body, encoding='utf-8').decode())
                content += body_html
            return content
        doc = Document(html)
        return doc.summary()
