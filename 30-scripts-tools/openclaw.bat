@echo off
REM OpenClaw Workspace Launcher
REM 自动设置环境并启动 Python

set OPENCLAW_WORKSPACE=D:\OpenClaw\workspace
set OPENCLAW_CONFIG=C:\Users\华为\.copaw
set PYTHONSTARTUP=D:\OpenClaw\workspace\python_startup.py

cd /d D:\OpenClaw\workspace

echo ========================================
echo [OpenClaw] Workspace Launcher
echo ========================================
echo Workspace: %OPENCLAW_WORKSPACE%
echo Config: %OPENCLAW_CONFIG%
echo Python Startup: %PYTHONSTARTUP%
echo ========================================
echo.

%*
