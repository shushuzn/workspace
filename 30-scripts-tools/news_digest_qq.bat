@echo off
chcp 65001 >nul
cd /d D:\OpenClaw\workspace

py 30-scripts-tools\news_to_qq_napcat.py digest 5
py 30-scripts-tools\feishu_assistant.py daily
