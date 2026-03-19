@echo off
chcp 65001 >nul
cd /d D:\OpenClaw\workspace
git add -A
git commit -m "feat: 5-layer protection system + quality scorer - prevent hasty deletion"
git push origin master
echo Done!
