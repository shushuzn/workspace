@echo off
REM WORKFLOW-START.bat - One-click workflow start

echo ========================================
echo OpenClaw Workflow Starter
echo ========================================
echo.

echo [1/5] Checking tools...
py 30-scripts-tools\tool_namer_001.py --scan | findstr /C:"Total" >nul
if errorlevel 1 (
    echo   Warning: Some tools not in convention
)

echo [2/5] Discovering tools...
py 30-scripts-tools\auto_discover_001.py --scan >nul

echo [3/5] Running diagnostics...
py 30-scripts-tools\workflow_diagnosis_001.py > temp_diag.json
findstr /C:"bottlenecks" temp_diag.json >nul
del temp_diag.json

echo [4/5] Validating code...
py 30-scripts-tools\tool_validator_001.py --check 30-scripts-tools\workflow_master_001.py >nul
if errorlevel 1 (
    echo   Warning: Master has issues
)

echo [5/5] System check complete!
echo.
echo Run workflow:
echo   py 30-scripts-tools\workflow_master_001.py --run dev
echo   py 30-scripts-tools\workflow_master_001.py --run full
echo.
pause
