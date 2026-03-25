@echo off
chcp 65001 > nul
title Star Forge Web - Preview
color 0B

echo.
echo ====================================
echo     Star Forge Web - Preview Mode
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
echo Starting preview...
echo.

REM Launch preview server
start "" "http://localhost:4173"
npm run preview

pause
