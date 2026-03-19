@echo off
chcp 65001 >nul
cd /d D:\OpenClaw\workspace
git add -A
git commit -m "feat: Week 2 naming standard and category subdivision complete - general reduced 65 percent"
git push origin master
echo Done!
