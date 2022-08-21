# -*- coding: utf-8 -*-

from urllib import parse

def parse_loc(detail_url,response_url):
    if detail_url.startswith('../../'):
        detail_url = detail_url[6:]
    elif detail_url.startswith('..'):
        detail_url = detail_url[2:]
    elif detail_url.startswith('.'):
        detail_url = detail_url[1:]

    if detail_url.startswith('http'):
        return detail_url
    elif detail_url.startswith('//www'):
        return response_url.split('://')[0]+':'+detail_url
    elif detail_url.startswith('//'):
        return response_url.split('//')[0]+detail_url
    else:
        parts = parse.urlparse(response_url)
        base_url = parts.scheme + '://' + parts.netloc
        if not base_url.endswith('/') and not detail_url.startswith('/'):
            base_url = base_url+'/'

        if '?' in response_url:
            if '?' in detail_url:
                return base_url+detail_url
            loc = response_url.split('?')[0]
            return loc+detail_url
        else:
            if '?' in detail_url:
                return base_url+detail_url
            elif detail_url.startswith('/'):
                return base_url+detail_url
            else:
                if not base_url.endswith('/') and not detail_url.startswith('/'):
                    return base_url + '/' + detail_url
                else:
                    return base_url + detail_url
