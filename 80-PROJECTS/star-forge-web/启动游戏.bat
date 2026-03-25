@echo off
chcp 65001 > nul
title Star Forge Web - Quick Start
color 0A

echo.
echo  ====================================
echo     Star Forge Web - Quick Start
echo ====================================
echo.

cd /d "%~dp0"

REM Check dependencies
if not exist "node_modules" (
    echo First run, installing dependencies...
    echo.
    npm install
    if errorlevel 1 (
        echo.
        echo Installation failed! Check network connection.
        pause
        exit /b 1
    )
    cls
)

echo.
echo Starting game...
echo.

REM Launch dev server
start "" "http://localhost:5173"
npm run dev

pause
