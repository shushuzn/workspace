@echo off
chcp 65001 >nul
cd /d D:\OpenClaw\workspace
git add -A
git commit -m "feat: research-driven brainstorm 20 ideas from GitHub arXiv"
git push origin master
echo Done!
