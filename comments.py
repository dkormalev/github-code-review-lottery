#!/usr/bin/env python3
# Copyright (c) 2015 Denis Kormalev <kormalev.denis@gmail.com>
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
import json
from constants import *
import config
import utils

def issue_contains_review_done_comment(issue):
    if issue.comments_count == 0:
        return False

    uri = GITHUB_API_URI + COMMENTS_PATH.format(issue.repository, issue.number)
    try:
        r = requests.get(uri, auth = (config.api_token, 'x-oauth-basic'), headers = utils.caching_request_headers(uri))
    except requests.exceptions.RequestException:
        return False

    if r.status_code == 200:
        utils.cache_response(r)
    elif r.status_code == 304:
        r = utils.fetch_cached_response(uri)
    if r.status_code != 200:
        print('Something went wrong', r.status_code)
        return False

    for comment in json.loads(r.text):
        if comment['user']['login'] == issue.assignee and comment['body'].strip() == REVIEW_DONE_COMMENT:
            return True

    return False

