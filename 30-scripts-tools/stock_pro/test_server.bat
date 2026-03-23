@echo off
cd /d D:\OpenClaw\workspace\30-scripts-tools\stock_pro
start "RSS Server" python rss_server.py
echo Server starting...
timeout /t 3 /nobreak
echo Server should be running at http://localhost:8888
