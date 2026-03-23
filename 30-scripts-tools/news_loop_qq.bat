@echo off
chcp 65001 >nul
cd /d D:\OpenClaw\workspace

:loop
py 30-scripts-tools\news_feishu.py update >nul 2>&1
py 30-scripts-tools\news_to_qq_napcat.py digest 3 >nul 2>&1
timeout /t 300 /nobreak >nul
goto loop
