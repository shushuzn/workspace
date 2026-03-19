@echo off
chcp 65001 >nul
cd /d D:\OpenClaw\workspace
git add -A
git commit -m "feat: Week 3 complete - tool directory created and 86 deprecated tools deleted - 20 percent reduction"
git push origin master
echo Done!
