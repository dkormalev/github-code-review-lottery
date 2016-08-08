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

import config
import teams
import repositories
import lottery_modes
import database_helper

class Lottery(object):
    def __init__(self):
        self._reviewers_by_teams = {}
        self._ubers_by_teams = {}
        self._reviewer_selector = None

    def select_assignee(self, issue, team_name):
        selected = self._reviewer_selector(dict(map(lambda x: (x, database_helper.fetch_user_rating(x)),
                                                    self._reviewers_by_teams[team_name])),
                                           self._ubers_by_teams[team_name], issue)
        if selected is None:
            selected = issue.author
        issue.assignee = selected
        self.increase_reviewer_score(selected)


    def increase_reviewer_score(self, reviewer):
        for key in self._reviewers_by_teams:
            if reviewer in self._reviewers_by_teams[key]:
                database_helper.increment_user_rating(reviewer)
                break



    def read_config(self):
        if config.lottery_mode == 'random':
            self._reviewer_selector = lottery_modes.select_reviewer_by_random
        elif config.lottery_mode == 'repo':
            self._reviewer_selector = lottery_modes.select_reviewer_by_repo_stats
        else:
            return False

        uber_team_id = teams.find_team_by_name(config.uber_team)
        if uber_team_id is None:
            return False
        full_uber_team = list(teams.team_members(uber_team_id))

        repositories_list = []

        for team_name in config.teams:
            team_id = teams.find_team_by_name(team_name)
            if team_id is None:
                return False
            self._reviewers_by_teams[team_name] = list(teams.team_members(team_id))
            self._ubers_by_teams[team_name] = list(filter(lambda u: u in self._reviewers_by_teams[team_name], full_uber_team))
            repositories_list.extend(list(teams.team_repositories(team_id)))

        print('Repositories found:', repositories_list)
        for repository in repositories_list:
            if not repositories.init_repository(repository):
                return False

        print('Reviewers:', self._reviewers_by_teams)
        print('Ubers:', self._ubers_by_teams)
        return True

