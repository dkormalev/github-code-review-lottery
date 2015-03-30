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
import sched
import time
import daemon

import issues
import config
import labels
import comments
import teams
import repositories
import lottery_modes

reviewers = []
ubers = []
reviewer_selector = None

def init_stuff():
    global reviewers
    global ubers
    global reviewer_selector

    if config.lottery_mode == 'random':
        reviewer_selector = lottery_modes.reviewer_random_selector
    elif config.lottery_mode == 'repo':
        reviewer_selector = lottery_modes.reviewer_repo_selector
    else:
        return False

    team_id = teams.find_team_by_name(config.team)
    if team_id is None:
        return False
    reviewers = list(teams.team_members(team_id))
    repositories_list = list(teams.team_repositories(team_id))

    uber_team_id = teams.find_team_by_name(config.uber_team)
    if uber_team_id is None:
        return False
    ubers = list(filter(lambda u: u in reviewers, teams.team_members(uber_team_id)))

    print(reviewers, ubers)
    print(repositories_list)

    for repository in repositories_list:
        if not repositories.init_repository(repository):
            return False
    return True

def main():
    if not init_stuff():
        print("Can't init script, exiting now")
        return
    print("Init done, starting lottery")

    scheduler = sched.scheduler(time.time, time.sleep)
    scores = {reviewer: 0 for reviewer in reviewers}

    def check_for_new_issues():
        print("Checking for new pull requests at", time.ctime())
        all_issues = issues.fetch_opened_pull_requests()
        all_issues = list(issues.filter_issues_for_team(all_issues, config.team))
        print (list(map(lambda i: (i.repository, i.number) , all_issues)))

        for issue in issues.filter_issues_to_be_assigned(all_issues):
            if issue.assignee is None:
                issue.assignee = reviewer_selector(scores, ubers, issue)
                scores[issue.assignee] += 1
            issue.add_in_review_label()
            update_result = issue.update_on_server()
            print("Added for review:", issue.repository, issue.number, issue.assignee)#, update_result)

        for issue in issues.filter_issues_to_be_checked_for_completed_review(all_issues):
            if comments.issue_contains_review_done_comment(issue):
                issue.add_reviewed_label()
                update_result = issue.update_on_server()
                print("Review completed:", issue.repository, issue.number, issue.assignee, update_result)

        if not config.single_shot:
            scheduler.enter(config.interval_between_checks_in_seconds, 1, check_for_new_issues)

    check_for_new_issues()
    if not config.single_shot:
        scheduler.run()

if __name__ == '__main__':
    if config.daemonize and not config.single_shot:
        with daemon.DaemonContext():
            main()
    else:
        main()
