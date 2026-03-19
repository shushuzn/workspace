@echo off
chcp 65001 >nul
cd /d D:\OpenClaw\workspace
git commit -m "docs: tool categorization complete - 100 percent coverage"
git push origin master
echo Done!
