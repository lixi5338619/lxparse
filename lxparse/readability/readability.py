#!/usr/bin/env python
import re
import sys
from lxml.etree import tounicode
from lxml.html import document_fromstring
from lxml.html import fragment_fromstring
from .cleaners import clean_attributes
from .cleaners import html_cleaner
from .htmls import build_doc
from lxml.etree import tostring

bytes_ = bytes
str_ = str
def tostring_(s):
    return tostring(s, encoding='utf-8')


REGEXES = {
    "unlikelyCandidatesRe": re.compile(
        r"combx|comment|community|disqus|extra|foot|header|menu|remark|rss|shoutbox|sidebar|sponsor|ad-break|agegate|pagination|pager|popup|tweet|twitter",
        re.I,
    ),
    "okMaybeItsACandidateRe": re.compile(r"and|article|body|column|main|shadow", re.I),
    "positiveRe": re.compile(
        r"article|body|content|entry|hentry|main|page|pagination|post|text|blog|story",
        re.I,
    ),
    "negativeRe": re.compile(
        r"combx|comment|com-|contact|foot|footer|footnote|masthead|media|meta|outbrain|promo|related|scroll|shoutbox|sidebar|sponsor|shopping|tags|tool|widget",
        re.I,
    ),
    "divToPElementsRe": re.compile(
        r"<(a|blockquote|dl|div|img|ol|p|pre|table|ul)", re.I
    ),
    #'replaceBrsRe': re.compile(r'(<br[^>]*>[ \n\r\t]*){2,}',re.I),
    #'replaceFontsRe': re.compile(r'<(\/?)font[^>]*>',re.I),
    #'trimRe': re.compile(r'^\s+|\s+$/'),
    #'normalizeRe': re.compile(r'\s{2,}/'),
    #'killBreaksRe': re.compile(r'(<br\s*\/?>(\s|&nbsp;?)*){1,}/'),
    "videoRe": re.compile(r"https?:\/\/(www\.)?(youtube|vimeo)\.com", re.I),
    # skipFootnoteLink:      /^\s*(\[?[a-z0-9]{1,2}\]?|^|edit|citation needed)\s*$/i,
}


def clean(text):
    # Many spaces make the following regexes run forever
    text = re.sub(r"\s{255,}", " " * 255, text)
    text = re.sub(r"\s*\n\s*", "\n", text)
    text = re.sub(r"\t|[ \t]{2,}", " ", text)
    return text.strip()


def text_length(i):
    return len(clean(i.text_content() or ""))


def compile_pattern(elements):
    if not elements:
        return None
    elif isinstance(elements, re._pattern_type):
        return elements
    elif isinstance(elements, (str_, bytes_)):
        if isinstance(elements, bytes_):
            elements = str_(elements, "utf-8")
        elements = elements.split(u",")
    if isinstance(elements, (list, tuple)):
        return re.compile(u"|".join([re.escape(x.strip()) for x in elements]), re.U)
    else:
        raise Exception("Unknown type for the pattern: {}".format(type(elements)))
        # assume string or string like object


class Document:
    """Class to build a etree document out of html."""
    def __init__(
        self,
        input,
        positive_keywords=None,
        negative_keywords=None,
        url=None,
        min_text_length=10,
        retry_length=250,
        xpath=False,
        handle_failures="discard",
    ):
        self.input = input
        self.html = None
        self.encoding = None
        self.positive_keywords = compile_pattern(positive_keywords)
        self.negative_keywords = compile_pattern(negative_keywords)
        self.url = url
        self.min_text_length = min_text_length
        self.retry_length = retry_length
        self.xpath = xpath
        self.handle_failures = handle_failures

    def _html(self, force=False):
        if force or self.html is None:
            self.html = self._parse(self.input)
            if self.xpath:
                root = self.html.getroottree()
                for i in self.html.getiterator():
                    i.attrib["x"] = root.getpath(i)
        return self.html

    def _parse(self, input):
        doc, self.encoding = build_doc(input)
        doc = html_cleaner.clean_html(doc)
        base_href = self.url
        if base_href:
            # trying to guard against bad links like <a href="http://[http://...">
            try:
                # such support is added in lxml 3.3.0
                doc.make_links_absolute(
                    base_href,
                    resolve_base_href=True,
                    handle_failures=self.handle_failures,
                )
            except TypeError:  # make_links_absolute() got an unexpected keyword argument 'handle_failures'
                # then we have lxml < 3.3.0
                # please upgrade to lxml >= 3.3.0 if you're failing here!
                doc.make_links_absolute(
                    base_href,
                    resolve_base_href=True,
                    handle_failures=self.handle_failures,
                )
        else:
            doc.resolve_base_href(handle_failures=self.handle_failures)
        return doc



    def get_clean_html(self):
        """
        An internal method, which can be overridden in subclasses, for example,
        to disable or to improve DOM-to-text conversion in .summary() method
        """
        return clean_attributes(tounicode(self.html, method="html"))


    def summary_list(self, html_partial=False):
        try:
            ruthless = True
            while True:
                self._html(True)
                for i in self.tags(self.html, "script", "style"):
                    i.drop_tree()
                for i in self.tags(self.html, "body"):
                    i.set("id", "readabilityBody")
                if ruthless:
                     self.remove_unlikely_candidates()
                self.transform_misused_divs_into_paragraphs()
                # 得分的标签
                candidates = self.score_paragraphs(detail=False)

                best_candidate = self.select_best_candidate(candidates)

                if best_candidate:
                    article = self.get_article(
                        candidates, best_candidate, html_partial=html_partial
                    )
                else:
                    if ruthless:
                        ruthless = False
                        continue
                    else:
                        article = self.html.find("body")
                        if article is None:
                            article = self.html
                cleaned_article = self.sanitize(article, candidates)

                article_length = len(cleaned_article or "")
                retry_length = self.retry_length
                of_acceptable_length = article_length >= retry_length
                if ruthless and not of_acceptable_length:
                    ruthless = False
                    continue
                else:
                    return cleaned_article
        except Exception as e:
            if sys.version_info[0] == 2:
                from .compat.two import raise_with_traceback
            else:
                ...

    def summary(self, html_partial=True):
        """
        Given a HTML file, extracts the text of the article.
        :param html_partial: return only the div of the document, don't wrap
                             in html and body tags.
        Warning: It mutates internal DOM representation of the HTML document,
        so it is better to call other API methods before this one.
        """
        try:
            ruthless = True
            while True:
                self._html(True)
                for i in self.tags(self.html, "script", "style"):
                    i.drop_tree()
                for i in self.tags(self.html, "body"):
                    i.set("id", "readabilityBody")
                if ruthless:
                    self.remove_unlikely_candidates()
                self.transform_misused_divs_into_paragraphs()
                candidates = self.score_paragraphs(detail=True)

                best_candidate = self.select_best_candidate(candidates)

                if best_candidate:
                    article = self.get_article(
                        candidates, best_candidate, html_partial=html_partial
                    )
                else:
                    if ruthless:
                        ruthless = False
                        continue
                    else:
                        article = self.html.find("body")
                        if article is None:
                            article = self.html
                cleaned_article = self.sanitize(article, candidates)

                article_length = len(cleaned_article or "")
                retry_length = self.retry_length
                of_acceptable_length = article_length >= retry_length
                if ruthless and not of_acceptable_length:
                    ruthless = False
                    continue
                else:
                    return cleaned_article
        except Exception as e:
            raise e


    def get_article(self, candidates, best_candidate, html_partial=False):
        # Now that we have the top candidate, look through its siblings for
        # content that might also be related.
        # Things like preambles, content split by ads that we removed, etc.
        sibling_score_threshold = max([10, best_candidate["content_score"] * 0.2])
        # create a new html document with a html->body->div
        if html_partial:
            output = fragment_fromstring("<div/>")
        else:
            output = document_fromstring("<div/>")
        best_elem = best_candidate["elem"]
        parent = best_elem.getparent()
        siblings = parent.getchildren() if parent is not None else [best_elem]

        if html_partial:sibling_tag = 'p'
        else:sibling_tag = 'a'

        for sibling in siblings:
            # in lxml there no concept of simple text
            # if isinstance(sibling, NavigableString): continue
            append = False
            if sibling is best_elem:
                append = True
            sibling_key = sibling  # HashableElement(sibling)
            if (
                sibling_key in candidates
                and candidates[sibling_key]["content_score"] >= sibling_score_threshold
            ):
                append = True

            if sibling.tag == sibling_tag:
                link_density = self.get_link_density(sibling)
                node_content = sibling.text or ""
                node_length = len(node_content)

                if node_length > 80 and link_density < 0.25:
                    append = True
                elif (
                    node_length <= 80
                    and link_density == 0
                    and re.search(r"\.( |$)", node_content)
                ):
                    append = True

            if append:
                if html_partial:
                    output.append(sibling)
                else:
                    output.getchildren()[0].getchildren()[0].append(sibling)
        return output

    def select_best_candidate(self, candidates):
        if not candidates:
            return None

        sorted_candidates = sorted(
            candidates.values(), key=lambda x: x["content_score"], reverse=True
        )
        for candidate in sorted_candidates[:5]:
            elem = candidate["elem"]

        best_candidate = sorted_candidates[0]
        return best_candidate

    def get_link_density(self, elem):
        link_length = 0
        for i in elem.findall(".//a"):
            link_length += text_length(i)
        # if len(elem.findall(".//div") or elem.findall(".//p")):
        #    link_length = link_length
        total_length = text_length(elem)
        return float(link_length) / max(total_length, 1)

    def score_paragraphs(self,detail=False):
        MIN_LEN = self.min_text_length
        candidates = {}
        ordered = []
        if not detail:
            for elem in self.tags(self._html(), "ul", "li","a","article","td","div"):
                parent_node = elem.getparent()
                if parent_node is None:
                    continue
                grand_parent_node = parent_node.getparent()

                inner_text = clean(elem.text_content() or "")
                inner_text_len = len(inner_text)

                # 如果这个标签内的文字小于MIN_LEN个字符，则不是标题
                if inner_text_len < MIN_LEN:
                    continue

                # 给elem的父级标签打分
                if parent_node not in candidates:
                    candidates[parent_node] = self.score_node(parent_node)
                    ordered.append(parent_node)

                if grand_parent_node is not None and grand_parent_node not in candidates:
                    candidates[grand_parent_node] = self.score_node(grand_parent_node)
                    ordered.append(grand_parent_node)

                content_score = 1
                content_score += len(inner_text.split(","))
                content_score += min((inner_text_len / 100), 3)
                # if elem not in candidates:
                #    candidates[elem] = self.score_node(elem)

                candidates[parent_node]["content_score"] += content_score
                if grand_parent_node is not None:
                    candidates[grand_parent_node]["content_score"] += content_score / 2.0

            # 根据链接密度得分,应该有一个较大的链接密度
            for elem in ordered:
                candidate = candidates[elem]
                ld = self.get_link_density(elem)
                candidate["content_score"] *= 1 + ld

        else:
            for elem in self.tags(self._html(), "p", "pre", "td"):
                parent_node = elem.getparent()
                if parent_node is None:
                    continue
                grand_parent_node = parent_node.getparent()

                inner_text = clean(elem.text_content() or "")
                inner_text_len = len(inner_text)

                # If this paragraph is less than 25 characters
                # don't even count it.
                if inner_text_len < MIN_LEN:
                    continue

                if parent_node not in candidates:
                    candidates[parent_node] = self.score_node(parent_node)
                    ordered.append(parent_node)

                if grand_parent_node is not None and grand_parent_node not in candidates:
                    candidates[grand_parent_node] = self.score_node(grand_parent_node)
                    ordered.append(grand_parent_node)

                content_score = 1
                content_score += len(inner_text.split(","))
                content_score += min((inner_text_len / 100), 3)
                # if elem not in candidates:
                #    candidates[elem] = self.score_node(elem)

                # WTF? candidates[elem]['content_score'] += content_score
                candidates[parent_node]["content_score"] += content_score
                if grand_parent_node is not None:
                    candidates[grand_parent_node]["content_score"] += content_score / 2.0

            for elem in ordered:
                candidate = candidates[elem]
                ld = self.get_link_density(elem)
                candidate["content_score"] *= 1 - ld

        return candidates

    def class_weight(self, e):
        weight = 0
        for feature in [e.get("class", None), e.get("id", None)]:
            if feature:
                if REGEXES["negativeRe"].search(feature):
                    weight -= 25

                if REGEXES["positiveRe"].search(feature):
                    weight += 25

                if self.positive_keywords and self.positive_keywords.search(feature):
                    weight += 25

                if self.negative_keywords and self.negative_keywords.search(feature):
                    weight -= 25

        if self.positive_keywords and self.positive_keywords.match("tag-" + e.tag):
            weight += 25

        if self.negative_keywords and self.negative_keywords.match("tag-" + e.tag):
            weight -= 25

        return weight

    def score_node(self, elem):
        content_score = self.class_weight(elem)
        name = elem.tag.lower()
        if name in ["div", "article"]:
            content_score += 5
        elif name in ["pre", "td", "blockquote"]:
            content_score += 3
        elif name in ["address", "ol", "ul", "dl", "dd", "dt", "li", "form", "aside"]:
            content_score -= 3
        elif name in [
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "th",
            "header",
            "footer",
            "nav",
        ]:
            content_score -= 5
        return {"content_score": content_score, "elem": elem}

    def remove_unlikely_candidates(self):
        for elem in self.html.findall(".//*"):
            s = "%s %s" % (elem.get("class", ""), elem.get("id", ""))
            if len(s) < 2:
                continue
            if (
                REGEXES["unlikelyCandidatesRe"].search(s)
                and (not REGEXES["okMaybeItsACandidateRe"].search(s))
                and elem.tag not in ["html", "body"]
            ):
                elem.drop_tree()

    def transform_misused_divs_into_paragraphs(self):
        for elem in self.tags(self.html, "div"):
            # transform <div>s that do not contain other block elements into
            # <p>s
            # FIXME: The current implementation ignores all descendants that
            # are not direct children of elem
            # This results in incorrect results in case there is an <img>
            # buried within an <a> for example
            if not REGEXES["divToPElementsRe"].search(
                str_(b"".join(map(tostring_, list(elem))))
            ):
                elem.tag = "a"

        for elem in self.tags(self.html, "div"):
            if elem.text and elem.text.strip():
                p = fragment_fromstring("<a/>")
                p.text = elem.text
                elem.text = None
                elem.insert(0, p)
                # print "Appended "+tounicode(p)+" to "+describe(elem)

            for pos, child in reversed(list(enumerate(elem))):
                if child.tail and child.tail.strip():
                    p = fragment_fromstring("<a/>")
                    p.text = child.tail
                    child.tail = None
                    elem.insert(pos + 1, p)
                    # print "Inserted "+tounicode(p)+" to "+describe(elem)
                if child.tag == "br":
                    # print 'Dropped <br> at '+describe(elem)
                    child.drop_tree()

    def tags(self, node, *tag_names):
        for tag_name in tag_names:
            for e in node.findall(".//%s" % tag_name):
                yield e

    def reverse_tags(self, node, *tag_names):
        for tag_name in tag_names:
            for e in reversed(node.findall(".//%s" % tag_name)):
                yield e

    def sanitize(self, node, candidates):
        MIN_LEN = self.min_text_length

        for elem in self.tags(node, "iframe"):
            if "src" in elem.attrib and REGEXES["videoRe"].search(elem.attrib["src"]):
                elem.text = "VIDEO"
            else:
                elem.drop_tree()

        allowed = {}
        for el in self.reverse_tags(
            node, "table", "ul", "div", "aside", "header", "footer", "section"
        ):
            if el in allowed:
                continue
            weight = self.class_weight(el)
            if el in candidates:
                content_score = candidates[el]["content_score"]
            else:
                content_score = 0
            tag = el.tag

            if weight + content_score < 0:
                el.drop_tree()

            elif el.text_content().count(",") > 2:
                counts = {}
                for kind in ["a","p", "img", "li", "a", "embed", "input"]:
                    counts[kind] = len(el.findall(".//%s" % kind))
                counts["li"] -= 100
                counts["input"] -= len(el.findall('.//input[@type="hidden"]'))

                # Count the text length excluding any surrounding whitespace
                content_length = text_length(el)
                link_density = self.get_link_density(el)
                parent_node = el.getparent()
                if parent_node is not None:
                    if parent_node in candidates:
                        content_score = candidates[parent_node]["content_score"]
                    else:
                        content_score = 0
                to_remove = False

                if counts["p"] and counts["img"] > 1 + counts["p"] * 1.3:
                    to_remove = True
                elif counts["li"] > counts["p"] and tag not in ("ol", "ul"):
                    to_remove = True
                elif counts["input"] > (counts["p"] / 3):
                    to_remove = True
                elif content_length < MIN_LEN and counts["img"] == 0:
                    to_remove = True
                elif content_length < MIN_LEN and counts["img"] > 2:
                    to_remove = True
                elif weight < 25 and link_density > 0.2:
                    to_remove = True
                elif weight >= 25 and link_density > 0.5:
                    to_remove = True
                elif (counts["embed"] == 1 and content_length < 75) or counts[
                    "embed"
                ] > 1:
                    to_remove = True
                elif not content_length:
                    to_remove = True
                    i, j = 0, 0
                    x = 1
                    siblings = []
                    for sib in el.itersiblings():
                        sib_content_length = text_length(sib)
                        if sib_content_length:
                            i = +1
                            siblings.append(sib_content_length)
                            if i == x:
                                break
                    for sib in el.itersiblings(preceding=True):
                        sib_content_length = text_length(sib)
                        if sib_content_length:
                            j = +1
                            siblings.append(sib_content_length)
                            if j == x:
                                break
                    if siblings and sum(siblings) > 1000:
                        to_remove = False
                        for desnode in self.tags(el, "table", "ul", "div", "section"):
                            allowed[desnode] = True

                if to_remove:
                    el.drop_tree()

        self.html = node
        return self.get_clean_html()