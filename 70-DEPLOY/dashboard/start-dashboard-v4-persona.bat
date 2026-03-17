@echo off
chcp 65001 >nul
REM Dashboard API v4.1 - 7-Persona Enhanced Startup Script
REM 多人格增强版启动脚本

echo.
echo ================================================================================
echo [OpenClaw] Dashboard API v4.1 - 7-Persona Enhanced
echo 多人格增强版 - 异步 API + 7 人格协作系统
echo ================================================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

echo [INFO] Starting Dashboard API v4.1 with 7-Persona System...
echo.
echo [PERSONAS]
echo   🔵 planner       - 规划者 (任务分解与规划)
echo   🟢 executor      - 执行者 (任务执行)
echo   🔴 critic        - 批判者 (质量审查)
echo   🟡 learner       - 学习者 (知识吸收)
echo   🟣 coordinator   - 协调者 (资源协调)
echo   🟠 innovator     - 创新者 (创意生成)
echo   ⚫ metacognition - 元认知 (全局监控)
echo.
echo [SERVER] http://0.0.0.0:8448
echo [INFO] Press Ctrl+C to stop
echo.

cd /d "%~dp0..\..\03-dashboard\api"
python dashboard-api-v4-persona.py --workers 1

if errorlevel 1 (
    echo.
    echo [ERROR] Server stopped with error
    pause
)
