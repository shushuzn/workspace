@echo off
REM ============================================
REM Find and Open Projects
REM Quick project access tool
REM ============================================

echo.
echo ============================================
echo   Project Finder - 项目查找器
echo ============================================
echo.

cd /d "%~dp0"

echo.
echo [1] TON Hackathon 2026 (HIGH PRIORITY)
echo [2] Knowledge Card Generator
echo [3] OpenClaw-RL
echo [4] Knowledge Card Package
echo [5] Knowledge Card Android
echo [6] View All Projects
echo [7] Create New Project
echo [0] Exit
echo.
set /p choice="Enter choice (0-7): "

if "%choice%"=="1" (
    echo.
    echo Opening TON Hackathon 2026...
    cd 50-projects\50-ton-hackathon-2026
    explorer .
    echo Done!
) else if "%choice%"=="2" (
    echo.
    echo Opening Knowledge Card Generator...
    cd knowledge-card-generator
    explorer .
    echo Done!
) else if "%choice%"=="3" (
    echo.
    echo Opening OpenClaw-RL...
    cd OpenClaw-RL
    explorer .
    echo Done!
) else if "%choice%"=="4" (
    echo.
    echo Opening Knowledge Card Package...
    cd knowledge-card-package
    explorer .
    echo Done!
) else if "%choice%"=="5" (
    echo.
    echo Opening Knowledge Card Android...
    cd knowledge-card-android
    explorer .
    echo Done!
) else if "%choice%"=="6" (
    echo.
    echo All Projects:
    echo.
    dir 50-projects /b
    echo.
    dir /b | findstr /i project
    echo.
) else if "%choice%"=="7" (
    echo.
    set /p name="Enter project name: "
    mkdir "50-projects\%name%"
    copy "projects\PROJECT_TEMPLATE.md" "50-projects\%name%\README.md"
    echo Created: 50-projects\%name%\
    echo Done!
) else if "%choice%"=="0" (
    echo.
    echo Exiting...
) else (
    echo.
    echo Invalid choice!
)

echo.
pause
