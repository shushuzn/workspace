@echo off
chcp 65001 >nul
cd /d D:\OpenClaw\workspace
git add -A
git commit -m "feat: brainstorm agent autonomy 30 ideas"
git push origin master
echo Done!
pause
