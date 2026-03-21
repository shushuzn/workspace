@echo off
cd /d D:\OpenClaw\workspace
git add -A
git commit --file=commit_msg.txt
git push origin master
del commit_msg.txt
del run_commit.bat
