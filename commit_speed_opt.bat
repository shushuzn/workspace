@echo off
chcp 65001 >nul
cd /d D:\OpenClaw\workspace
git add -A
git commit -m "feat: speed optimization phase3 complete - 12 tools total"
git push origin master
echo Done!
pause
