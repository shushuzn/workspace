@echo off
REM Obsidian Auto Sync - Startup Script
REM Place in Windows Startup folder or run manually

echo ========================================
echo Obsidian Auto Sync
echo ========================================
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "D:\OpenClaw\workspace\scripts\obsidian-auto-sync.ps1"

echo.
echo Sync complete!
pause
