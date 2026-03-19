@echo off
chcp 65001 >nul
cd /d D:\OpenClaw\workspace
git add -A
git commit -m "fix: restore 29 deleted tools - quality over quantity principle"
git push origin master
echo Done!
