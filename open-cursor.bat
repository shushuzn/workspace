@echo off
chcp 65001 >nul
title Cursor IDE - OpenClaw Workspace

echo.
echo ========================================
echo   Cursor IDE - OpenClaw Workspace
echo ========================================
echo.
echo Starting Cursor with OpenClaw workspace...
echo Workspace: D:\OpenClaw\workspace
echo.
echo Keyboard shortcuts:
echo   Ctrl+K - AI Command
echo   Ctrl+L - AI Chat
echo   Ctrl+S - Save
echo.
echo "D:\cursor\resources\app\bin\cursor.cmd" "D:\OpenClaw\workspace"
start "" "D:\cursor\resources\app\bin\cursor.cmd" "D:\OpenClaw\workspace"
