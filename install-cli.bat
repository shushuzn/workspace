@echo off
REM OpenClaw CLI Installation Script for Windows
REM Adds openclaw command to system PATH

echo ============================================================
echo [OpenClaw] CLI Installation
echo ============================================================
echo.

REM Get script directory
set SCRIPT_DIR=%~dp0
set CLI_SCRIPT=%SCRIPT_DIR%openclaw-cli.py
set BATCH_FILE=%SCRIPT_DIR%openclaw.bat

REM Create batch wrapper
echo Creating batch wrapper...
echo @echo off > "%BATCH_FILE%"
echo python "%CLI_SCRIPT%" %%* >> "%BATCH_FILE%"
echo. >> "%BATCH_FILE%"

REM Add to PATH (user level)
echo.
echo Adding to user PATH...
setx OPENCLAW_CLI "%SCRIPT_DIR%" >nul 2>&1

echo.
echo ============================================================
echo Installation Complete!
echo ============================================================
echo.
echo Usage:
echo   openclaw --help
echo   openclaw cache stats
echo   openclaw memory maintain --daily
echo   openclaw collect github --language python
echo.
echo Note: You may need to restart your terminal for PATH changes to take effect.
echo.
echo ============================================================

pause
