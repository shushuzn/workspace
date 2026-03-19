@echo off
chcp 65001 >nul
cd /d D:\OpenClaw\workspace
git add -A
git commit -m "docs: integration fix report - lesson learned"
git push origin master
