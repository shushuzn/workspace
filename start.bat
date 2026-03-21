@echo off
chcp 65001 >nul
echo ========================================
echo OpenClaw - New Session
echo ========================================
echo.
echo Starting dashboard...

REM Run pre-session workflow
py 30-scripts-tools\workflow_master_001.py --run dev

echo.
echo Dashboard: http://localhost:8448
echo.
echo Type your commands below...
echo.
