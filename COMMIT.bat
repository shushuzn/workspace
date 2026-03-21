@echo off
REM GUARDED-COMMIT.bat - Commit with mandatory checks
REM Usage: guarded_commit.bat <file1> [file2] ...

setlocal enabledelayedexpansion

echo ========================================
echo WORKFLOW GUARD - Mandatory Checks
echo ========================================

set FILES=
:loop
if "%~1"=="" goto done
    set FILES=!FILES! %1
    shift
    goto loop
:done

if "%FILES%"=="" (
    echo ERROR: No files specified
    echo Usage: guarded_commit.bat ^<file1^> [file2] ...
    exit /b 1
)

REM Run mandatory checks
python 30-scripts-tools\workflow_guard_001.py --commit %FILES%

if errorlevel 1 (
    echo.
    echo COMMIT BLOCKED - Fix errors above
    exit /b 1
)

echo.
echo COMMIT SUCCESSFUL
