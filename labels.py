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

def create_labels_if_needed(repository):
    labels_uri = GITHUB_API_URI + LABELS_PATH.format(repository)
    all_labels = []
    while labels_uri is not None:
        r = requests.get(labels_uri, auth = (config.api_token, 'x-oauth-basic'), headers = utils.caching_request_headers(labels_uri))

        if r.status_code == 200:
            utils.cache_response(r)
        elif r.status_code == 304:
            r = utils.fetch_cached_response(labels_uri)
        if r.status_code != 200:
            print('Something went wrong', r.status_code)
            return False

        all_labels += json.loads(r.text)
        labels_uri = utils.next_page_url(r)

    labels_uri = GITHUB_API_URI + LABELS_PATH.format(repository)

    in_review_label_found = False
    reviewed_label_found = False
    for label in all_labels:
        label_name = label['name']
        if label_name == IN_REVIEW_LABEL:
            in_review_label_found = True
        elif label_name == REVIEWED_LABEL:
            reviewed_label_found = True
        if in_review_label_found and reviewed_label_found:
            break

    if not in_review_label_found:
        label_data = {'name': IN_REVIEW_LABEL, 'color': 'eb6420'}
        r = requests.post(labels_uri, auth = (config.api_token, 'x-oauth-basic'),
                          data = json.dumps(label_data))
        if r.status_code != 201:
            print('Something went wrong with in review label', r.status_code)
            return False

    if not reviewed_label_found:
        label_data = {'name': REVIEWED_LABEL, 'color': '00aa00'}
        r = requests.post(labels_uri, auth = (config.api_token, 'x-oauth-basic'),
                          data = json.dumps(label_data))
        if r.status_code != 201:
            print('Something went wrong with reviewed label', r.status_code)
            return False

    return True
