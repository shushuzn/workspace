@echo off
REM ============================================
REM Workspace Root Cleanup Script
REM Keeps root directory clean and organized
REM ============================================

echo.
echo ============================================
echo   Workspace Root Cleanup
echo ============================================
echo.

cd /d "%~dp0"

echo [INFO] Current directory: %CD%
echo.

REM Create archive folder if not exists
if not exist "00-root-docs" mkdir 00-root-docs
if not exist "21-reports" mkdir 21-reports
if not exist "15-docs" mkdir 15-docs
if not exist "02-openclaw-system" mkdir 02-openclaw-system

echo [1/4] Moving reports to 21-reports/...
move 00-*.md 21-reports\ >nul 2>&1
move AUTONOMOUS-*.md 21-reports\ >nul 2>&1
move WORKSPACE-STANDARDIZATION-*.md 21-reports\ >nul 2>&1
echo [OK]   Reports moved

echo.
echo [2/4] Moving identity files to 02-openclaw-system/...
move AGENTS.md 02-openclaw-system\ >nul 2>&1
move SOUL.md 02-openclaw-system\ >nul 2>&1
move IDENTITY.md 02-openclaw-system\ >nul 2>&1
move USER.md 02-openclaw-system\ >nul 2>&1
move TOOLS.md 02-openclaw-system\ >nul 2>&1
move HEARTBEAT.md 02-openclaw-system\ >nul 2>&1
echo [OK]   Identity files moved

echo.
echo [3/4] Moving documentation to 15-docs/...
move WORKSPACE-*.md 15-docs\ >nul 2>&1
move BIG-FILES-*.md 15-docs\ >nul 2>&1
move OPTIMIZATION-*.md 15-docs\ >nul 2>&1
move API-SETUP-*.md 15-docs\ >nul 2>&1
echo [OK]   Documentation moved

echo.
echo [4/4] Moving temporary files to 00-root-docs/...
move *.md 00-root-docs\ >nul 2>&1
move *.json 00-root-docs\ >nul 2>&1
move .env* 00-root-docs\ >nul 2>&1
move *.zip 00-root-docs\ >nul 2>&1
echo [OK]   Temporary files moved

echo.
echo ============================================
echo   Cleanup Complete!
echo ============================================
echo.
echo Root directory should now contain:
echo   - Essential config (.gitignore, .env.example)
echo   - Main entry points (README.md, package.json)
echo   - System directories (.git/, .obsidian/)
echo.
echo Everything else is organized in folders!
echo.

dir /b

echo.
pause
