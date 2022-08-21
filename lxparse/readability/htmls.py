from lxml.html import tostring
import lxml.html
from .encoding import get_encoding

utf8_parser = lxml.html.HTMLParser(encoding="utf-8")


def build_doc(page):
    if isinstance(page, str):
        encoding = None
        decoded_page = page
    else:
        encoding = get_encoding(page) or "utf-8"
        decoded_page = page.decode(encoding, "replace")

    # XXX: we have to do .decode and .encode even for utf-8 pages to remove bad characters
    doc = lxml.html.document_fromstring(
        decoded_page.encode("utf-8", "replace"), parser=utf8_parser
    )
    return doc, encoding

