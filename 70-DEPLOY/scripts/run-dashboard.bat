@echo off
chcp 65001 >nul
cd /d %~dp0
set PYTHONIOENCODING=utf-8
python 03-dashboard\api\dashboard-api-v4-persona.py --host 0.0.0.0 --port 8448
