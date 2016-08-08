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
import users
import utils

def find_team_by_name(team_name):
    uri = GITHUB_API_URI + USER_TEAMS_PATH
    while uri is not None:
        r = requests.get(uri, auth = (config.api_token, 'x-oauth-basic'), headers = utils.caching_request_headers(uri))

        if r.status_code == 200:
            utils.cache_response(r)
        elif r.status_code == 304:
            r = utils.fetch_cached_response(uri)
        if r.status_code != 200:
            print('Unable to find team by name. API response code: ', r.status_code)
            return None

        for team in json.loads(r.text):
            if team_name == team['name']:
                return team['id']
        uri = utils.next_page_url(r)

    return None

def team_members(team_id):
    uri = GITHUB_API_URI + TEAM_MEMBERS_PATH.format(team_id)
    all_users = []
    while uri is not None:
        r = requests.get(uri, auth = (config.api_token, 'x-oauth-basic'), headers = utils.caching_request_headers(uri))

        if r.status_code == 200:
            utils.cache_response(r)
        elif r.status_code == 304:
            r = utils.fetch_cached_response(uri)
        if r.status_code != 200:
            print('Unable to find team members by team ID. API response code: ', r.status_code)
            return None

        all_users += json.loads(r.text)
        uri = utils.next_page_url(r)

    current_user = users.current_user_name()
    return map(lambda u: u['login'], filter(lambda u: u['login'] != current_user, all_users))

def team_repositories(team_id):
    uri = GITHUB_API_URI + TEAM_REPOS_PATH.format(team_id)
    all_repos = []
    while uri is not None:
        r = requests.get(uri, auth = (config.api_token, 'x-oauth-basic'), headers = utils.caching_request_headers(uri))

        if r.status_code == 200:
            utils.cache_response(r)
        elif r.status_code == 304:
            r = utils.fetch_cached_response(uri)
        if r.status_code != 200:
            print('Unable to find team repositories by name. API response code: ', r.status_code)
            return None

        all_repos += json.loads(r.text)
        uri = utils.next_page_url(r)

    return map(lambda r: r['full_name'], filter(lambda r: not r['fork'], all_repos))


