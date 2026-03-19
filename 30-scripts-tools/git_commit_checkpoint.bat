@echo off
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d D:\OpenClaw\workspace
git add flow-archive/20260318-universal-workflow-001/checkpoint.json
git add 13-memory/2026-03-19.md
git commit -m "Update checkpoint and memory after visual progress implementation"
git push origin master
pause
