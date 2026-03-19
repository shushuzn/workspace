@echo off
chcp 65001 >nul
cd /d D:\OpenClaw\workspace
git add -A
git commit -m "feat: tool governance layer 4 phase 2 complete - 7 tools automated, total 23 tools, 31 triggers added"
git push origin master
echo Done!
