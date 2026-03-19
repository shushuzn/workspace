@echo off
chcp 65001 >nul
cd /d D:\OpenClaw\workspace
git add 13-memory/2026-03-19.md
git commit -m "docs: update daily note with missing file tool recovery"
git push origin master
echo Done!
