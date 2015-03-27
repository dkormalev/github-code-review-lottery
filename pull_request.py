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

class PullRequest(object):
    def __init__(self, repository, number, author, assignee, labels):
        self._repository = repository
        self._number = number
        self._author = author
        self._assignee = assignee
        self._labels = labels

    @property
    def repository(self):
        return self._repository

    @property
    def number(self):
        return self._number

    @property
    def author(self):
        return self._author

    @property
    def assignee(self):
        return self._assignee

    @assignee.setter
    def assignee(self, assignee):
        self._assignee = assignee

    @property
    def labels(self):
        return self._labels

    def update_on_server(self):
        uri = GITHUB_API_URI + SINGLE_ISSUE_PATH.format(config.organization_name,
                                                    self.repository,
                                                    self.number)
        data_to_send = {}
        r = requests.patch(uri, auth = (config.api_token, 'x-oauth-basic'),
                           data = json.dumps({'assignee': self.assignee}))
        return r.status_code == 200

    def is_assigned(self):
        return self._assignee is not None
