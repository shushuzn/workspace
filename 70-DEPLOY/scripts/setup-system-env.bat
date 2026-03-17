@echo off
REM OpenClaw 系统环境变量永久设置
REM 管理员权限运行此脚本

echo ========================================
echo [OpenClaw] System Environment Setup
echo ========================================
echo.

REM 设置系统环境变量
echo [1/3] Setting OPENCLAW_WORKSPACE...
setx /M OPENCLAW_WORKSPACE "D:\OpenClaw\workspace"
if %errorlevel% equ 0 (
    echo   [OK] OPENCLAW_WORKSPACE = D:\OpenClaw\workspace
) else (
    echo   [ERR] Failed to set OPENCLAW_WORKSPACE
)

echo.
echo [2/3] Setting OPENCLAW_CONFIG...
setx /M OPENCLAW_CONFIG "C:\Users\华为\.copaw"
if %errorlevel% equ 0 (
    echo   [OK] OPENCLAW_CONFIG = C:\Users\华为\.copaw
) else (
    echo   [ERR] Failed to set OPENCLAW_CONFIG
)

echo.
echo [3/3] Setting PYTHONSTARTUP...
setx /M PYTHONSTARTUP "D:\OpenClaw\workspace\python_startup.py"
if %errorlevel% equ 0 (
    echo   [OK] PYTHONSTARTUP = D:\OpenClaw\workspace\python_startup.py
) else (
    echo   [ERR] Failed to set PYTHONSTARTUP
)

echo.
echo ========================================
echo [OK] System environment variables set!
echo.
echo IMPORTANT: Restart terminal/IDE to apply
echo ========================================

pause
