#!/usr/bin/env python3
# Copyright (c) 2015 Denis Kormalev <kormalev.denis@gmail.com>
# Copyright (c) 2016 Aliya Iskhakova <iskhakova.alija@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is furnished
# to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import requests
import re
import database_helper


def next_page_url(response):
    if response.status_code < 200 or response.status_code >= 300 or 'Link' not in response.headers:
        return None
    next_link = re.search('<([^>]*)>; rel="next"', response.headers['Link'])
    return next_link.group(1) if next_link is not None else None

def cache_response(response, uri=''):
    if len(uri) == 0:
        uri = response.url
    if 'ETag' not in response.headers:
        remove_response_from_cache(uri)
        return
    database_helper.cache_response(uri, response)

def caching_request_headers(uri):
    result = database_helper.fetch_cached_response(uri)
    return {'If-None-Match': result.headers['ETag']} if result is not None else {}

def fetch_cached_response(uri):
    return database_helper.fetch_cached_response(uri)

def remove_response_from_cache(uri):
        database_helper.remove_response(uri)
