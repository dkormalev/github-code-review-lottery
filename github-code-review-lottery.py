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
import daemon

import issues
import config
import labels

def init_stuff():
    for repository in config.repositories:
        if not labels.create_labels_if_needed(repository):
            return False
    return True

def reviewer_with_minimum_score(reviewers):
    min_score = -1
    min_reviewers = []
    for reviewer, score in reviewers.items():
        if score < min_score or min_score == -1:
            min_score, min_reviewers = score, [reviewer]
        elif score == min_score:
            min_reviewers.append(reviewer)
    return random.choice(min_reviewers)

def main():
    if not init_stuff():
        print("Can't init script, exiting now")
        return

    scheduler = sched.scheduler(time.time, time.sleep)
    scores = {reviewer: 0 for reviewer in config.reviewers}
    def check_repositories():
        print("Checking for new pull requests at", time.ctime())
        for repository in config.repositories:
            for issue in issues.issues_to_be_assigned(issues.fetch_opened_pull_requests(repository)):
                if issue.assignee is None:
                    issue.assignee = reviewer_with_minimum_score(scores)
                    scores[issue.assignee] += 1
                issue.add_in_review_label()
                assign_result = issue.update_on_server()
                print(issue.repository, issue.number, issue.assignee, assign_result)
        scheduler.enter(config.interval_between_checks_in_seconds, 1, check_repositories)
    scheduler.enter(config.interval_between_checks_in_seconds, 1, check_repositories)
    scheduler.run()

if __name__ == '__main__':
    if config.daemonize:
        with daemon.DaemonContext():
            main()
    else:
        main()
