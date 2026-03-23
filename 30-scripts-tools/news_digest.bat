@echo off
chcp 65001 >nul
cd /d D:\OpenClaw\workspace

echo [%date% %time%] Sending digest...

:: 发送摘要
py 30-scripts-tools\news_manager.py digest

echo [%date% %time%] Done.
