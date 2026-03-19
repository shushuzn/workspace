@echo off
chcp 65001 >nul
cd /d D:\OpenClaw\workspace
git add -A
git commit -m "docs: phase3 completion report and daily note - 100 percent complete"
git push origin master
echo Done!
