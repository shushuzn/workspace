@echo off
REM Unified Dashboard v1.0 Launcher
REM Starts the consolidated workspace monitoring dashboard

echo Starting Unified Dashboard v1.0...
echo.

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

REM Install psutil if not present
python -c "import psutil" >nul 2>&1
if errorlevel 1 (
    echo Installing psutil...
    pip install psutil
)

echo.
echo ========================================
echo   Unified Dashboard v1.0
echo   Consolidated Workspace Monitoring
echo ========================================
echo.
echo Access URL: http://localhost:8500
echo API: http://localhost:8500/api/data
echo Health: http://localhost:8500/api/health
echo.
echo Press Ctrl+C to stop
echo.

REM Start dashboard
python 30-scripts-tools\unified_dashboard.py

pause
