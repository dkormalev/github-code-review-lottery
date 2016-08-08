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
import issues
import random
import utils

def _random_selector(reviewers, issue):
    print('_random_selector:', reviewers, issue.author)
    if len(reviewers) == 0:
        return None
    min_score = -1
    min_reviewers = []
    for reviewer, score in reviewers.items():
        if reviewer == issue.author:
            continue
        if score < min_score or min_score == -1:
            min_score, min_reviewers = score, [reviewer]
        elif score == min_score:
            min_reviewers.append(reviewer)
    print('_random_selector 2:', min_reviewers)
    if len(min_reviewers) == 0:
        return None
    return random.choice(min_reviewers)


def select_reviewer_by_random(reviewers, ubers, issue):
    result = _random_selector(reviewers, issue)
    print('select_reviewer_by_random:\r\n', reviewers, 'Uber team: ', ubers, "The issue author:", issue.author, result)
    if result is None:
        result = _random_selector({u: reviewers[u] for u in ubers}, issue)
    if result is None:
        result = issue.author
    return result

def select_reviewer_by_repo_stats(reviewers, ubers, issue):
    print('select_reviewer_by_repo_stats:\r\n', reviewers, 'Uber team: ', ubers, "The issue author:", issue.author)
    uri = GITHUB_API_URI + REPO_CONTRIBUTORS_PATH.format(issue.repository)
    r = requests.get(uri, auth = (config.api_token, 'x-oauth-basic'), headers = utils.caching_request_headers(uri))

    if r.status_code == 200:
        utils.cache_response(r)
    elif r.status_code == 304:
        r = utils.fetch_cached_response(uri)
    if r.status_code != 200:
        return select_reviewer_by_random(reviewers, ubers, issue)

    contributions = 0
    contributors = {}
    for contributor in json.loads(r.text):
        contributions += contributor['contributions']
        contributors[contributor['login']] = contributor['contributions']
    if len(contributors) == 0:
        return select_reviewer_by_random(reviewers, ubers, issue)
    threshold = contributions / len(contributors) * config.repo_lottery_factor

    eligible_reviewers = {}
    for reviewer, score in reviewers.items():
        if reviewer not in contributors or reviewer == issue.author:
            continue
        if contributors[reviewer] >= threshold:
            eligible_reviewers[reviewer] = score

    print("Eligible reviewers: ", eligible_reviewers)
    if len(eligible_reviewers) == 0:
        eligible_reviewers = {u: reviewers[u] for u in ubers}
        ubers = {}
    return select_reviewer_by_random(eligible_reviewers, ubers, issue)

