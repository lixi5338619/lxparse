# -*- coding: utf-8 -*-

from .parse_title import TitleExtractor
from .parse_loc import parse_loc
from .parse_date import DateExtractor
from .parse_author import AuthorExtractor,SourceExtractor
from .parse_content import ContentExtractor
from .parse_list import ListExtractor

list_parse = ListExtractor()
title_parse = TitleExtractor()
date_parse = DateExtractor()
author_parse = AuthorExtractor()
source_parse = SourceExtractor()
content_parse = ContentExtractor()