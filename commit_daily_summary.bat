@echo off
chcp 65001 >nul
cd /d D:\OpenClaw\workspace
git add 13-memory/2026-03-20.md
git commit -m "docs: daily summary 2026-03-20 complete - speed opt + quality improvement + protection system"
git push origin master
echo Done!
