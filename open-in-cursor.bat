@echo off
chcp 65001 >nul
:: Open file in Cursor IDE
:: Usage: open-in-cursor.bat filename

if "%1"=="" (
    "D:\cursor\resources\cursor.exe" "D:\OpenClaw\workspace"
) else (
    "D:\cursor\resources\cursor.exe" "%~f1"
)
