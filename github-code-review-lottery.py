#!/usr/bin/env python3
# Copyright (c) 2015 Denis Kormalev <kormalev.denis@gmail.com>
# Copyright (c) 2016 Aliya Iskhakova <iskhakova.alija@gmail.com>
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

import sched
import time
import daemon
import requests

import issues
import config
import comments
import database_helper

from lottery import Lottery

def main():
    database_helper.init_database()
    lottery = Lottery()
    if not lottery.read_config():
        print("Can't init script, exiting now")
        return
    print('Init done, starting lottery')

    scheduler = sched.scheduler(time.time, time.sleep)

    def check_for_new_issues():
        print('Checking for new pull requests at', time.ctime())
        all_issues = list(issues.fetch_opened_pull_requests())
        issues_by_teams = {}

        for team_name in config.teams:
            try:
                team_issues = list(issues.filter_issues_for_team(all_issues, team_name))
                issues_by_teams[team_name] = team_issues
                all_issues = list(filter(lambda i: i not in team_issues, all_issues))
            except requests.exceptions.RequestException:
                pass

        for team_name in issues_by_teams:
            team_issues = issues_by_teams[team_name]
            print ('Team', team_name, 'has:', list(map(lambda i: (i.repository, i.number) , team_issues)))
            for issue in issues.filter_issues_to_be_assigned(team_issues):
                try:
                    if issue.assignee is None:
                        lottery.select_assignee(issue, team_name)
                    else:
                        lottery.increase_reviewer_score(issue.assignee)
                    issue.add_in_review_label()
                    update_result = issue.update_on_server()
                    print('Added for review:', issue.repository, issue.number, issue.assignee, update_result)
                except requests.exceptions.RequestException:
                    pass

            for issue in issues.filter_issues_to_be_checked_for_completed_review(team_issues):
                if comments.issue_contains_review_done_comment(issue):
                    issue.add_reviewed_label()
                    try:
                        update_result = issue.update_on_server()
                        print('Review completed:', issue.repository, issue.number, issue.assignee, update_result)
                    except requests.exceptions.RequestException:
                        pass

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
