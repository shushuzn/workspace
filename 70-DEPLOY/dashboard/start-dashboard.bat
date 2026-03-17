@echo off
chcp 65001 >nul
REM Default Dashboard Startup Script
REM 默认启动脚本 - 使用 v4.1-Persona 多人格增强版

echo.
echo ================================================================================
echo [OpenClaw] Dashboard - Default Startup
echo 默认启动 v4.1-Persona 多人格增强版
echo ================================================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

echo [INFO] Starting Dashboard API v4.1-Persona (Default)...
echo.
echo [VERSION] 4.1-Persona Enhanced
echo [FEATURES]
echo   - Asynchronous I/O (FastAPI + uvicorn)
echo   - 7-Persona Collaboration System
echo   - WebSocket Real-time Updates
echo   - Redis Task Queue (Optional)
echo   - Performance Monitoring
echo.
echo [PERSONAS]
echo   🔵 Planner       - Planning ^& Task Decomposition
echo   🟢 Executor      - Task Execution
echo   🔴 Critic        - Quality Review
echo   🟡 Learner       - Knowledge Absorption
echo   🟣 Coordinator   - Resource Coordination
echo   🟠 Innovator     - Creative Generation
echo   ⚫ Metacognition - Global Monitoring
echo.
echo [SERVER] http://0.0.0.0:8448
echo [API]  http://localhost:8448/api/personas
echo.
echo [INFO] Press Ctrl+C to stop
echo.

REM Start v4.1-Persona (Default)
cd /d "%~dp0..\..\03-dashboard\api"
python dashboard-api-v4-persona.py --workers 1

if errorlevel 1 (
    echo.
    echo [ERROR] Server stopped with error
    echo [INFO] Try falling back to v4.0...
    python dashboard-api-v4.py --workers 1
)
