@echo off
chcp 65001 >nul
cd /d D:\OpenClaw\workspace

echo [%date% %time%] Starting news auto push...

:: 抓取新闻
py 30-scripts-tools\news_manager.py fetch

:: 推送未发送的新闻
py 30-scripts-tools\news_manager.py push

echo [%date% %time%] Done.
