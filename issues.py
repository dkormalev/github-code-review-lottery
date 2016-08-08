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
import repositories
import utils

class Issue(object):
    def __init__(self, issue_json):
        self._issue_json = issue_json
        self._labels = set(map(lambda l: l['name'], issue_json['labels']))
        self._assignee = issue_json['assignee']['login'] if issue_json['assignee'] else None

    @property
    def repository(self):
        return self._issue_json['repository']['full_name']

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

    def contains_in_review_label(self):
        return IN_REVIEW_LABEL in self._labels

    def contains_reviewed_label(self):
        return REVIEWED_LABEL in self._labels

    def contains_review_related_labels(self):
        return self.contains_in_review_label() or self.contains_reviewed_label()

    def add_in_review_label(self):
        if self.contains_reviewed_label():
            self._labels.remove(REVIEWED_LABEL)
        self._labels.add(IN_REVIEW_LABEL)

    def add_reviewed_label(self):
        if self.contains_in_review_label():
            self._labels.remove(IN_REVIEW_LABEL)
        self._labels.add(REVIEWED_LABEL)

    def update_on_server(self):
        uri = GITHUB_API_URI + SINGLE_ISSUE_PATH.format(self.repository, self.number)
        r = requests.patch(uri, auth = (config.api_token, 'x-oauth-basic'),
                           data = json.dumps({'assignee': self.assignee,
                                             'labels': list(self.labels)}))
        return r.status_code == 200

    def is_assigned(self):
        return self.assignee is not None


def fetch_opened_pull_requests():
    uri = GITHUB_API_URI + (SUBSCRIBED_ISSUES_PATH if config.only_subscribed_issues else ALL_ISSUES_PATH)
    all_issues = []
    while uri is not None:
        try:
            r = requests.get(uri, auth = (config.api_token, 'x-oauth-basic'), headers = utils.caching_request_headers(uri))
        except requests.exceptions.RequestException:
            return []
        if r.status_code == 200:
            utils.cache_response(r)
        elif r.status_code == 304:
            r = utils.fetch_cached_response(uri)
        if r.status_code != 200:
            print('Could not fetch opened pull requests. Response code: ', r.status_code)
            return []
        all_issues += json.loads(r.text)
        uri = utils.next_page_url(r)

    issues_filler = lambda issue: Issue(issue)
    filtered_issues = filter(lambda issue: issue['state'] == 'open'
                                            and 'pull_request' in issue
                                            and not issue['repository']['fork'],
                             all_issues)
    return map(issues_filler, filtered_issues)

def filter_issues_for_team(issues, team):
    return filter(lambda i: team in repositories.repository_teams(i.repository), issues)

def filter_issues_to_be_assigned(issues):
    return filter(lambda i: not i.contains_review_related_labels(), issues)

def filter_issues_to_be_checked_for_completed_review(issues):
    return filter(lambda i: i.contains_in_review_label() and i.comments_count != 0, issues)
