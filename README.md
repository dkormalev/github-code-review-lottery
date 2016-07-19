GitHub Code Review Lottery
==========================
Utility that loops endlessly in waiting for new pull requests in given repositories and adds assignees (who supposed to review these PRs).

Prereqs
-------
* Python3 (I'm using 3.4)
* requests
* python-daemon

ToDo
----
* sqlite db to store reviewers scores between runs
* git statistics usage to select proper reviewer
* consider configparser instead of .py file
* Refactor to hide github pagination in single fetch method
* Think about teams members re-fetch

Disclaimer
----------
I'm not a pythonista but a C++/Qt guy mostly. If you found that my code is not really good from Python perspective - feel free to ping me and say about it.
