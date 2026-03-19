@echo off
chcp 65001 >nul
cd /d D:\OpenClaw\workspace
git add -A
git commit -m "feat: tool governance solution - 5 layer framework for 424 tools"
git push origin master
echo Done!
