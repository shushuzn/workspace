@echo off
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d D:\OpenClaw\workspace
git add flow-archive/20260318-universal-workflow-001/COMPLETION-TEMPLATE-LIBRARY.md
git add flow-archive/20260318-universal-workflow-001/checkpoint.json
git commit -m "Add completion report for template library implementation"
git push origin master
pause
