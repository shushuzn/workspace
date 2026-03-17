@echo off
chcp 65001 >nul
REM Dashboard v5.0 - Memory Integrated Startup Script
REM 仪表盘 v5.0 - 记忆系统集成版

echo.
echo ================================================================================
echo [OpenClaw] Dashboard v5.0 - Memory Integrated
echo 仪表盘 v5.0 - 记忆系统集成版
echo ================================================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

echo [INFO] Starting Dashboard API v5.0 - Memory Integrated...
echo.
echo [VERSION] 5.0-Memory
echo [FEATURES]
echo   - Asynchronous I/O (FastAPI + uvicorn)
echo   - 7-Persona Collaboration System
echo   - 🧠 Memory System Integration (NEW!)
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
echo [MEMORY SYSTEM]
echo   - MEMORY.md Read/Write
echo   - Daily Notes Management
echo   - Memory Search
echo   - Memory Statistics
echo.
echo [SERVER] http://0.0.0.0:8448
echo [API]  http://localhost:8448/api/personas
echo [FRONTEND] Open dashboard-v5-memory.html in browser
echo.
echo [INFO] Press Ctrl+C to stop
echo.

REM Start v5.0-Memory
python dashboard-api-v5-memory.py --workers 1

if errorlevel 1 (
    echo.
    echo [ERROR] Server stopped with error
    echo [INFO] Try falling back to v4.1-Persona...
    python dashboard-api-v4-persona.py --workers 1
)
