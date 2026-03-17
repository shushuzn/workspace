@echo off
echo ================================================
echo   Fix Arxiv Collector Scheduled Task
echo ================================================
echo.
echo This script requires Administrator privileges.
echo.
pause
powershell -ExecutionPolicy Bypass -Command "Start-Process powershell -ArgumentList '-ExecutionPolicy Bypass -File D:\OpenClaw\workspace\fix-arxiv-task.ps1' -Verb RunAs"
echo.
echo Administrator PowerShell launched.
echo Please wait for the task update to complete.
echo.
pause
