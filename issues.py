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

class Issue(object):
    def __init__(self, repository, issue_json):
        self._repository = repository
        self._issue_json = issue_json
        self._labels = filter(lambda l: l['name'], issue_json['labels'])
        self._assignee = issue_json['assignee']['login'] if issue_json['assignee'] else None

    @property
    def repository(self):
        return self._repository

    @property
    def number(self):
        return self._issue_json['number']

    @property
    def author(self):
        return self._issue_json['user']['login']

    @property
    def assignee(self):
        return self._assignee

    @assignee.setter
    def assignee(self, assignee):
        self._assignee = assignee

    @property
    def labels(self):
        return self._labels

    @property
    def comments_count(self):
        return self._issue_json['comments']

    def update_on_server(self):
        uri = GITHUB_API_URI + SINGLE_ISSUE_PATH.format(config.organization_name,
                                                    self.repository,
                                                    self.number)
        data_to_send = {}
        r = requests.patch(uri, auth = (config.api_token, 'x-oauth-basic'),
                           data = json.dumps({'assignee': self.assignee}))
        return r.status_code == 200

    def is_assigned(self):
        return self.assignee is not None


def fetch_opened_pull_requests(repository):
    uri = GITHUB_API_URI + ISSUES_PATH.format(config.organization_name, repository)
    r = requests.get(uri, auth = (config.api_token, 'x-oauth-basic'))
    if r.status_code != 200:
        print("Something went wrong", r.status_code)
        return []
    labels_filler = lambda label: label['name']
    issues_filler = lambda issue: Issue(repository = repository, issue_json = issue)
    filtered_issues = filter(lambda issue: issue['state'] == 'open' and issue['pull_request'], json.loads(r.text))
    return map(issues_filler, filtered_issues)

def issues_to_be_assigned(issues):
    return filter(lambda i: not i.is_assigned(), issues)
