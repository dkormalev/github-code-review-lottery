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
import labels
import time
import utils

repositories = {}
denied_repositories = {}

class Repository(object):
    def __init__(self, name):
        self._name = name
        self._teams = []

    @property
    def name(self):
        return self._name

    @property
    def teams(self):
        return self._teams

    def update_teams(self):
        uri = GITHUB_API_URI + REPO_TEAMS_PATH.format(self._name)
        r = requests.get(uri, auth = (config.api_token, 'x-oauth-basic'),
                         headers = utils.caching_request_headers(uri))

        if r.status_code == 200:
            utils.cache_response(r)
        elif r.status_code == 304:
            r = utils.fetch_cached_response(uri)
        if r.status_code != 200:
            denied_repositories[self._name] = time.time()
            utils.remove_response_from_cache(uri)
            self._teams = []
            return

        self._teams = list(map(lambda r: r['name'], json.loads(r.text)))

def init_repository(repository):
    try:
        repositories[repository] = Repository(repository)
        repositories[repository].update_teams()
        if len(config.teams.intersection(repositories[repository].teams)) > 0:
            if not labels.create_labels_if_needed(repository):
                return False
        return True
    except:
        del repositories[repository]
        raise

def repository_teams(repository):
    if repository in repositories:
        #If repository access was denied once - let's not ask about it for an hour
        if repository not in denied_repositories or time.time() - denied_repositories[repository] > 60 * 60:
            repositories[repository].update_teams()
    else:
        init_repository(repository)
    return repositories[repository].teams
