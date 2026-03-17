@echo off
REM ============================================
REM 7-Persona System Quick Access
REM Interactive menu for persona system
REM ============================================

echo.
echo ============================================
echo   7-Persona System - 七人格系统
echo ============================================
echo.
echo Location: 00-persona-system\
echo.

echo [1] Open Persona System Folder
echo [2] View System Architecture
echo [3] View Interaction Guide
echo [4] View Launch Guide
echo [5] View All Persona Files
echo.
echo [6] Open Planner Persona
echo [7] Open Executor Persona
echo [8] Open Critic Persona (批判者)
echo [9] Open Learner Persona
echo [10] Open Coordinator Persona
echo [11] Open Innovator Persona
echo [12] Open Metacognitive Persona
echo.
echo [13] View Test Summary
echo [14] View Performance Benchmarks
echo [15] View File Standards
echo.
echo [0] Exit
echo.
set /p choice="Enter choice (0-15): "

if "%choice%"=="1" (
    echo.
    echo Opening 00-persona-system\...
    explorer 00-persona-system
    echo Done!
) else if "%choice%"=="2" (
    echo.
    echo Opening System Architecture...
    start 00-persona-system\PERSONA-ARCHITECTURE-v1.md
    echo Done!
) else if "%choice%"=="3" (
    echo.
    echo Opening Interaction Guide...
    start 00-persona-system\PERSONA-INTERACTION-GUIDE.md
    echo Done!
) else if "%choice%"=="4" (
    echo.
    echo Opening Launch Guide...
    start 00-persona-system\5-PERSONA-SYSTEM-LAUNCH.md
    echo Done!
) else if "%choice%"=="5" (
    echo.
    echo All Persona Files:
    dir 00-persona-system\*PERSONA*.md /b
    echo.
) else if "%choice%"=="6" (
    echo.
    if exist "00-persona-system\PLANNER-PERSONA-v1.md" (
        start 00-persona-system\PLANNER-PERSONA-v1.md
    ) else (
        echo PLANNER-PERSONA-v1.md not found!
        echo Creating from template...
        echo Creating Planner Persona... > 00-persona-system\PLANNER-PERSONA-v1.md
        echo File created. Please edit manually.
    )
    echo Done!
) else if "%choice%"=="7" (
    echo.
    if exist "00-persona-system\EXECUTOR-PERSONA-v1.md" (
        start 00-persona-system\EXECUTOR-PERSONA-v1.md
    ) else (
        echo EXECUTOR-PERSONA-v1.md not found!
        echo Creating from template...
        echo Creating Executor Persona... > 00-persona-system\EXECUTOR-PERSONA-v1.md
        echo File created. Please edit manually.
    )
    echo Done!
) else if "%choice%"=="8" (
    echo.
    if exist "00-persona-system\SOUL-批判者 v5.0-终极批判机器.md" (
        start 00-persona-system\SOUL-批判者 v5.0-终极批判机器.md
    ) else if exist "00-persona-system\CRITIC-PERSONA-v1.md" (
        start 00-persona-system\CRITIC-PERSONA-v1.md
    ) else (
        echo Critic persona not found!
    )
    echo Done!
) else if "%choice%"=="9" (
    echo.
    start 00-persona-system\LEARNER-PERSONA-v1.md
    echo Done!
) else if "%choice%"=="10" (
    echo.
    start 00-persona-system\COORDINATOR-PERSONA-v1.md
    echo Done!
) else if "%choice%"=="11" (
    echo.
    start 00-persona-system\INNOVATOR-PERSONA-v1.md
    echo Done!
) else if "%choice%"=="12" (
    echo.
    start 00-persona-system\METACOGNITIVE-PERSONA-v1.md
    echo Done!
) else if "%choice%"=="13" (
    echo.
    start 00-persona-system\TEST-SUMMARY-20260313.md
    echo Done!
) else if "%choice%"=="14" (
    echo.
    start 00-persona-system\PERFORMANCE-BENCHMARK-20260313.md
    echo Done!
) else if "%choice%"=="15" (
    echo.
    start 00-persona-system\FILE-NAMING-STANDARD-20260313.md
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
