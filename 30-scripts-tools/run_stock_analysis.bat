@echo off
REM STOCK-ANALYSIS.bat - Quick stock analysis runner

echo ========================================
echo Stock Analysis Workflow
echo ========================================
echo.

set WORKFLOW=%1
set SYMBOL=%2

if "%WORKFLOW%"=="" set WORKFLOW=quick
if "%SYMBOL%"=="" set SYMBOL=AAPL

echo Running: %WORKFLOW% for %SYMBOL%
echo.

py 30-scripts-tools\workflow_stock_001.py --run %WORKFLOW% %SYMBOL%

echo.
pause
