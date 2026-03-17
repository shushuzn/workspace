@echo off
REM ============================================
REM arXiv Collector - Daily Scheduled Task Setup
REM Auto-runs every day at 8:00 AM
REM ============================================

echo.
echo ============================================
echo   arXiv Collector - Scheduled Task Setup
echo ============================================
echo.

REM Get current directory
set SCRIPT_DIR=%~dp0
set PYTHON_SCRIPT=%SCRIPT_DIR%arxiv-collector-v2.py

echo [INFO] Script location: %PYTHON_SCRIPT%
echo.

REM Find Python executable
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found in PATH
    echo Please install Python or add it to PATH
    exit /b 1
)

for /f "delims=" %%i in ('where python') do set PYTHON_EXE=%%i
echo [INFO] Python: %PYTHON_EXE%
echo.

REM Create scheduled task
echo [ACTION] Creating scheduled task...
echo.
echo Task Details:
echo   Name: arXiv-Daily-Collector
echo   Trigger: Daily at 8:00 AM
echo   Action: python arxiv-collector-v2.py
echo   Working Directory: %SCRIPT_DIR%
echo.

schtasks /Create /TN "arXiv-Daily-Collector" /TR "\"%PYTHON_EXE%\" \"%PYTHON_SCRIPT%\"" /SC DAILY /ST 08:00 /RL HIGHEST /F

if %errorlevel% equ 0 (
    echo.
    echo [SUCCESS] Scheduled task created!
    echo.
    echo To verify:
    echo   schtasks /Query /TN "arXiv-Daily-Collector"
    echo.
    echo To run manually:
    echo   schtasks /Run /TN "arXiv-Daily-Collector"
    echo.
    echo To delete:
    echo   schtasks /Delete /TN "arXiv-Daily-Collector" /F
    echo.
) else (
    echo.
    echo [ERROR] Failed to create scheduled task
    echo Please run as Administrator
    echo.
)

pause
