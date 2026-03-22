@echo off
chcp 65001 >nul
title Stock PRO Dashboard

echo.
echo ================================================
echo            Stock PRO Dashboard Launcher
echo ================================================
echo.

:choice
echo Choose UI:
echo   [1] Simple UI (无需安装, 端口 8080)
echo   [2] Dash UI (需要安装 dash, 端口 8050)
echo   [3] 安装 Dash 后启动
echo   [0] 退出
echo.
set /p choice=请选择 (0-3):

if "%choice%"=="1" goto simple
if "%choice%"=="2" goto dash
if "%choice%"=="3" goto install_dash
if "%choice%"=="0" goto end

echo 无效选择，请重试
echo.
goto choice

:simple
echo.
echo 启动 Simple UI...
echo 打开浏览器访问: http://127.0.0.1:8080
echo 按 Ctrl+C 停止
echo.
cd /d "%~dp0"
python simple_ui.py
goto end

:dash
echo.
echo 检查 Dash 安装状态...
python -c "import dash; print(f'Dash {dash.__version__}')" 2>nul
if errorlevel 1 (
    echo.
    echo Dash 未安装，是否安装?
    set /p confirm=按 Y 安装，其他键跳过:
    if /i "%confirm%"=="Y" goto install_dash
)
echo.
echo 启动 Dash UI...
echo 打开浏览器访问: http://127.0.0.1:8050
echo 按 Ctrl+C 停止
echo.
cd /d "%~dp0"
python dash_app.py
goto end

:install_dash
echo.
echo 正在安装 Dash...
pip install dash plotly
echo.
echo 安装完成!
echo.
goto choice

:end
pause
