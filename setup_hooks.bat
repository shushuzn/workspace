@echo off
REM Install Git Hooks
echo Installing Git hooks...

REM Copy pre-commit hook
copy /Y ".git\hooks\pre-commit.bat" ".git\hooks\pre-commit" >nul
if errorlevel 1 (
    echo Failed to install hooks
    exit /b 1
)

REM Make sure pre-commit is executable on Unix systems
REM (Not needed on Windows but keeps compatibility)

echo ✅ Git hooks installed
echo.
echo Hooks will automatically run before each commit:
echo   1. Validate Python files in 30-scripts-tools/
echo   2. Check naming conventions
echo.
echo If checks fail, commit is BLOCKED
