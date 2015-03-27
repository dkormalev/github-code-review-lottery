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
import random
import sched
import time

GITHUB_API_URI = 'https://api.github.com'
ISSUES_PATH = '/repos/{}/{}/issues'
SINGLE_ISSUE_PATH= '/repos/{}/{}/issues/{}'

organization_name = ''
repositories = []
reviewers = []
api_token = ''
interval_between_checks_in_seconds = 15

def fetch_opened_pull_requests(repository):
    uri = GITHUB_API_URI + ISSUES_PATH.format(organization_name, repository)
    r = requests.get(uri, auth = (api_token, 'x-oauth-basic'))
    if r.status_code != 200:
        print("Something went wrong", r.status_code)
        return []
    labels_filler = lambda label: label['name']
    issues_filler = lambda issue: {'repository': repository,
                                    'number': issue['number'],
                                    'author': issue['user']['login'],
                                    'labels': list(map(labels_filler, issue['labels'])),
                                    'assignee': issue['assignee']['login'] if issue['assignee'] else None}
    filtered_issues = filter(lambda issue: issue['state'] == 'open' and issue['pull_request'], json.loads(r.text))
    return map(issues_filler, filtered_issues)

def pull_requests_to_be_assigned(pull_requests):
    return filter(lambda pr: pr['assignee'] is None, pull_requests)

def assign_pull_request_to_reviewer(pull_request, reviewer):
    uri = GITHUB_API_URI + SINGLE_ISSUE_PATH.format(organization_name,
                                                    pull_request['repository'],
                                                    pull_request['number'])
    r = requests.patch(uri, auth = (api_token, 'x-oauth-basic'), data = json.dumps({'assignee': reviewer}))
    return r.status_code == 200

def reviewer_with_minimum_score(reviewers):
    min_score = -1
    min_reviewers = []
    print(reviewers)
    for reviewer, score in reviewers.items():
        if score < min_score or min_score == -1:
            min_score, min_reviewers = score, [reviewer]
        elif score == min_score:
            min_reviewers.append(reviewer)
    return random.choice(min_reviewers)

def main():
    scheduler = sched.scheduler(time.time, time.sleep)
    scores = {reviewer: 0 for reviewer in reviewers}
    def check_repositories():
        print("Checking for new pull requests at", time.ctime())
        for repository in repositories:
            for pull_request in pull_requests_to_be_assigned(fetch_opened_pull_requests(repository)):
                reviewer = reviewer_with_minimum_score(scores)
                scores[reviewer] += 1
                assign_result = assign_pull_request_to_reviewer(pull_request, reviewer)
                print(pull_request['repository'], pull_request['number'], reviewer, assign_result)
        scheduler.enter(interval_between_checks_in_seconds, 1, check_repositories)
    scheduler.enter(interval_between_checks_in_seconds, 1, check_repositories)
    scheduler.run()


if __name__ == '__main__':
    main()
