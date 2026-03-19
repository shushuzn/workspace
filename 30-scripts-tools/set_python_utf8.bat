@echo off
REM 设置 Python UTF-8 编码（系统级）
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
chcp 65001 >nul 2>&1
