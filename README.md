GitHub Code Review Lottery
--------------------------
Utility that loops endlessly in waiting for new pull requests in given repositories and adds assignees (who supposed to review these PRs).

Prereqs
=======
* Python3 (I'm using 3.4)
* requests

ToDo
====
* labels usage
* configparser instead of .py file
* sqlite db to store reviewers scores between runs
* teams usage to determine what repos and reviewers lists
* git statistics usage to select proper reviewer

Disclaimer
==========
I'm not a pythonista but a C++/Qt guy mostly. If you found that my code is not really good from Python perspective - feel free to ping me and say about it.
