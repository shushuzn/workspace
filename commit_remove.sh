#!/bin/bash
cd /d D:\OpenClaw\workspace
git reset HEAD 30-scripts-tools/bad_test_001.py
git add .gitignore
git rm --cached 30-scripts-tools/bad_test_001.py
del 30-scripts-tools\bad_test_001.py
git add -A
git commit --file=commit_msg.txt
git push origin master
