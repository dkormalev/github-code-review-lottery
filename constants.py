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

GITHUB_API_URI = 'https://api.github.com'
SUBSCRIBED_ISSUES_PATH = '/issues?filter=subscribed&per_page=100'
ALL_ISSUES_PATH = '/issues?filter=all&per_page=100'
SINGLE_ISSUE_PATH= '/repos/{}/issues/{}'
LABELS_PATH = '/repos/{}/labels?per_page=100'
COMMENTS_PATH = '/repos/{}/issues/{}/comments?per_page=100'

USER_PATH = '/user'
USER_TEAMS_PATH = '/user/teams?per_page=100'
TEAM_MEMBERS_PATH = '/teams/{}/members?per_page=100'
TEAM_REPOS_PATH = '/teams/{}/repos?per_page=100'

REPO_TEAMS_PATH = '/repos/{}/teams?per_page=100'

REPO_CONTRIBUTORS_PATH = '/repos/{}/contributors?per_page=100'

IN_REVIEW_LABEL = 'In Review'
REVIEWED_LABEL = 'Reviewed'
REVIEW_DONE_COMMENT = '+1'
