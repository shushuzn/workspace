@echo off
chcp 65001 >nul
cd /d D:\OpenClaw\workspace
git add -A
git commit -m "feat: tool quality improvement phase 1-2 complete - 20 tools improved, poor tools -45 percent, critic 80/100"
git push origin master
echo Done!
