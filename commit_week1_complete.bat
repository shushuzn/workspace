@echo off
chcp 65001 >nul
cd /d D:\OpenClaw\workspace
git add -A
git commit -m "feat: tool usage tracking and deprecated marking complete - Week 1 100 percent"
git push origin master
echo Done!
