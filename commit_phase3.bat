@echo off
chcp 65001 >nul
cd /d D:\OpenClaw\workspace
git add -A
git commit -m "feat: tool quality improvement phase 3 complete - 12 tools improved, total 32 tools, score 51.3"
git push origin master
echo Done!
