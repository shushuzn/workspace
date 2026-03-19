@echo off
chcp 65001 >nul
cd /d D:\OpenClaw\workspace

REM Git Commit Helper - Python version with retry
REM 用法：git_commit "提交消息"

py 30-scripts-tools\git_commit_helper.py %*
