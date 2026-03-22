@echo off
chcp 65001 >nul
set OPENCLAW_CURSOR_MODE=1
set OPENCLAW_AUTO_EXECUTE=1
cd /d D:\OpenClaw\workspace
py 30-scripts-tools\copaw_entry.py 
