@echo off
REM Stock PRO v12.0 - Quick Launcher
cd /d "%~dp0.."
set PYTHONPATH=%CD%\30-scripts-tools
python -m stock_pro.main %*
