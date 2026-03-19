@echo off
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d D:\OpenClaw\workspace
git add -A
git commit -m "docs: session end - anomaly detection completed"
git push origin master
pause
