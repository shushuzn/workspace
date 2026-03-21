@echo off
REM ========================================
REM WORKFLOW - Unified Workflow Entry Point
REM ========================================
REM Usage:
REM   workflow.bat              - Show help
REM   workflow.bat list         - List all workflows
REM   workflow.bat dev          - Run dev workflow
REM   workflow.bat run <name>   - Run specific workflow
REM   workflow.bat categories   - List by category

setlocal enabledelayedexpansion

set "CMD=%1"

if "%CMD%"=="" goto :help
if "%CMD%"=="help" goto :help
if "%CMD%"=="-h" goto :help
if "%CMD%"=="--help" goto :help

if "%CMD%"=="list" goto :list
if "%CMD%"=="categories" goto :categories

if "%CMD%"=="run" (
    set "WF=%2"
    if "!WF!"=="" (
        echo ERROR: Missing workflow name
        echo Usage: workflow.bat run ^<workflow-name^>
        exit /b 1
    )
    goto :run
)

REM Direct workflow run
set "WF=%CMD%"
goto :run

:run
echo.
echo ========================================
echo Running workflow: %WF%
echo ========================================
python 30-scripts-tools\workflow_master_001.py --run %WF%
exit /b %ERRORLEVEL%

:list
echo.
echo ========================================
echo Available Workflows
echo ========================================
python 30-scripts-tools\workflow_master_001.py --list
exit /b 0

:categories
echo.
echo ========================================
echo Workflow Categories
echo ========================================
python 30-scripts-tools\workflow_master_001.py --categories
exit /b 0

:help
echo.
echo ========================================
echo WORKFLOW - Unified Workflow Entry Point
echo ========================================
echo.
echo Usage:
echo   workflow.bat              - Show this help
echo   workflow.bat list         - List all workflows
echo   workflow.bat categories    - List by category
echo   workflow.bat dev          - Run dev workflow
echo   workflow.bat run ^<name^> - Run specific workflow
echo.
echo Categories:
echo   dev       - Development workflows
echo   plan      - Planning workflows
echo   qa        - Quality Assurance
echo   ops       - Operations
echo   research  - Research pipelines
echo.
echo Examples:
echo   workflow.bat dev
echo   workflow.bat plan
echo   workflow.bat full
echo   workflow.bat research
echo   workflow.bat run dev
exit /b 0
