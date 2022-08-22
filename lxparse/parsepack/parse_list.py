# -*- coding: utf-8 -*-

from lxparse.readability import Document
from lxml import etree
import re,math

class ListExtractor:
    def __init__(self):
        self.ARTICLE_NUMS = None
        self.LINK_NUMS = None

    def extractor(self, html, xpath_list,article_nums,link_nums):
        self.ARTICLE_NUMS = article_nums
        self.LINK_NUMS = link_nums
        self.html = html
        element = etree.HTML(html)
        if xpath_list:
            if not xpath_list.endswith('/@href'):
                xpath_list += '/@href'
            return element.xpath(xpath_list)
        data = self.filter_url(html)
        if not data:return []
        result = self.rinse_url(data)
        return self.filter_list_url(result)


    def filter_url(self,html):
        doc = Document(html)
        e = etree.HTML(doc.summary_list())

        xpath_lists = ['//h6/a', '//h5/a', '//h4/a', '//h3/a', '//h2/a', '//h1/a',
                       '//article//a', '//ul/li//a', '//tr/td//a',
                       '//div/a'
                       ]
        lens_table = 0
        table = []
        for xpath_list in xpath_lists:
            if lens_table>self.LINK_NUMS:
                break
            first = e.xpath(xpath_list + '/@href')
            if first and len(''.join(e.xpath(xpath_list+'//text()')))>5:
                table += first
            lens_table += len(table)
        return list(set(table))


    def compute_cosine(self,text_a,text_b):
        # Cosine similarity solution = = > URL similarity
        words1 = text_a.split('/')
        words2 = text_b.split('/')
        words1_dict = {}
        words2_dict = {}
        for word in words1:
            word = re.sub('[^a-zA-Z]', '', word)
            word = word.lower()
            if word != '' and word in words1_dict:
                num = words1_dict[word]
                words1_dict[word] = num + 1
            elif word != '':
                words1_dict[word] = 1
            else:
                continue
        for word in words2:
            word = re.sub('[^a-zA-Z]', '', word)
            word = word.lower()
            if word != '' and word in words2_dict:
                num = words2_dict[word]
                words2_dict[word] = num + 1
            elif word != '':
                words2_dict[word] = 1
            else:
                continue
        # 排序
        dic1 = sorted(words1_dict.items(), key=lambda asd: asd[1], reverse=True)
        dic2 = sorted(words2_dict.items(), key=lambda asd: asd[1], reverse=True)
        # 得到词向量
        words_key = []
        for i in range(len(dic1)):
            # 向数组中添加元素
            words_key.append(dic1[i][0])
        for i in range(len(dic2)):
            if dic2[i][0] in words_key:
                pass
            else:
                # 合并
                words_key.append(dic2[i][0])
        vect1 = []
        vect2 = []
        for word in words_key:
            if word in words1_dict:
                vect1.append(words1_dict[word])
            else:
                vect1.append(0)
            if word in words2_dict:
                vect2.append(words2_dict[word])
            else:
                vect2.append(0)
        # 计算余弦相似度
        sum = 0
        sq1 = 0
        sq2 = 0
        for i in range(len(vect1)):
            sum += vect1[i] * vect2[i]
            sq1 += pow(vect1[i], 2)
            sq2 += pow(vect2[i], 2)
        try:
            result = round(float(sum) / (math.sqrt(sq1) * math.sqrt(sq2)), 2)
        except ZeroDivisionError:
            result = 0.0
        return result


    def rinse_url(self,data):
        # Return the URL array with high similarity in the list
        new = []
        for i in range(len(data)):
            ss=[]
            text1 = data[i].replace(' ','')
            k = 1
            for j in range(len(data)):
                text2 = data[j].replace(' ','')
                if text1==text2:continue
                result = self.compute_cosine(text1,text2)
                if result<1 and result>0.7:result=1
                if result==1:
                    if k >= self.ARTICLE_NUMS-1:
                        ss.append(text1)
                        break
                    k += 1
            new+=ss
        return new

    def filter_list_url(self,result:list):
        stp = False
        for url in result:
            if 'news' in url or 'detail' in url:
                stp = True
                break
        if stp:
            for url in result:
                if 'news' not in url or 'detail' not in url:
                    result.remove(url)
        return result
