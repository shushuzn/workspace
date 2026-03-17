@echo off
chcp 65001 >nul
title Dashboard API v4 Server

echo.
echo 🚀 Innovator Dashboard API v4.0
echo ========================================
echo 高性能异步 API 服务器
echo.
echo 正在启动服务器...
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 未安装或未添加到 PATH
    pause
    exit /b 1
)

REM 检查依赖
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  依赖未安装，正在安装...
    call install-dashboard-v4.bat
)

echo.
echo 📁 工作目录：%~dp0
echo.
echo 服务器地址：http://0.0.0.0:8447
echo API 文档：http://localhost:8447/docs
echo.
echo 按 Ctrl+C 停止服务器
echo.

REM 启动服务器
python dashboard-api-v4.py

pause
