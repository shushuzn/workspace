@echo off
chcp 65001 >nul
cd /d D:\OpenClaw\workspace
git add -A
git commit -m "feat: tool governance layer 4 phase 1 - 16 tools automated, 21 triggers added, automation rate 10.8 percent"
git push origin master
echo Done!
