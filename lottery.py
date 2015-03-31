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

import config
import teams
import repositories
import lottery_modes

class Lottery(object):
    def __init__(self):
        self._reviewers = {}
        self._ubers = []
        self._reviewer_selector = None

    @property
    def reviewers(self):
        return self._reviewers

    @property
    def ubers(self):
        return self._ubers

    def select_assignee(self, issue):
        selected = self._reviewer_selector(self._reviewers, self._ubers, issue)
        if selected is None:
            selected = issue.author
        issue.assignee = selected
        self._reviewers[issue.assignee] += 1

    def increase_reviewer_score(self, reviewer):
        if reviewer not in self._reviewers:
            return
        self._reviewers[reviewer] += 1

    def read_config(self):
        if config.lottery_mode == 'random':
            self._reviewer_selector = lottery_modes.select_reviewer_by_random
        elif config.lottery_mode == 'repo':
            self._reviewer_selector = lottery_modes.select_reviewer_by_repo_stats
        else:
            return False

        team_id = teams.find_team_by_name(config.team)
        if team_id is None:
            return False
        self._reviewers = {reviewer: 0 for reviewer in teams.team_members(team_id)}

        uber_team_id = teams.find_team_by_name(config.uber_team)
        if uber_team_id is None:
            return False
        self._ubers = list(filter(lambda u: u in self._reviewers, teams.team_members(uber_team_id)))

        repositories_list = list(teams.team_repositories(team_id))

        print(self._reviewers, self._ubers)
        print(repositories_list)

        for repository in repositories_list:
            if not repositories.init_repository(repository):
                return False
        return True
