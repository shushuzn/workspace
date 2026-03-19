@echo off
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d D:\OpenClaw\workspace
git add flow-archive/20260318-universal-workflow-001/FINAL-PROTECTION-REPORT.md
git commit -m "Add final protection report"
git push origin master
pause
