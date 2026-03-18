@echo off
REM ========================================================================
REM  Flow ID 工作流快速启动脚本
REM ========================================================================
REM 
REM Usage:
REM   start-flow.bat {业务名} "{任务描述}"
REM 
REM Examples:
REM   start-flow.bat backend-crud "Backend CRUD API development"
REM   start-flow.bat frontend-ui "Frontend dashboard UI implementation"
REM   start-flow.bat db-migration "Database schema migration"
REM 
REM ========================================================================

setlocal enabledelayedexpansion

REM 检查参数
if "%~1"=="" (
    set BUSINESS_NAME=universal-workflow
) else (
    set BUSINESS_NAME=%1
)

REM 生成 Flow ID
REM 使用 PowerShell 获取标准日期格式
for /f "delims=" %%i in ('powershell -Command "Get-Date -Format 'yyyyMMdd'"') do set DATE=%%i
set FLOW_ID=%DATE%-%BUSINESS_NAME%-001

REM 任务描述 (可选)
set TASK_DESC=%~2
if not defined TASK_DESC set TASK_DESC=%BUSINESS_NAME% task

echo.
echo ============================================================
echo  Flow ID 工作流启动
echo ============================================================
echo.
echo Flow ID:     %FLOW_ID%
echo 业务名称：   %BUSINESS_NAME%
echo 任务描述：   %TASK_DESC%
echo 启动时间：   %date% %time%
echo.
echo ============================================================
echo.

REM 检查 flow-archive 目录
if not exist "flow-archive" (
    echo [INFO] Creating flow-archive directory...
    mkdir "flow-archive"
)

REM 创建 Flow ID 专属目录
set FLOW_DIR=flow-archive\%FLOW_ID%
if not exist "%FLOW_DIR%" (
    echo [INFO] Creating flow directory: %FLOW_DIR%
    mkdir "%FLOW_DIR%"
)

REM 更新 flow_registry.json (简化版)
echo [INFO] Registering flow in flow_registry.json...
py 30-scripts-tools\flow_register.py --flow_id %FLOW_ID% --business %BUSINESS_NAME%

echo.
echo ============================================================
echo  Flow ID 隔离规则
echo ============================================================
echo.
echo ✅ 所有文件读写 → %FLOW_DIR%/
echo ✅ 批判者审查 → %FLOW_DIR%/review.json
echo ✅ 执行日志 → %FLOW_DIR%/execution-log.json
echo ✅ Git 提交 → [FLOW ID: %FLOW_ID%]
echo.
echo ⚠️  禁止修改/引用其他工作流的任何内容
echo.
echo ============================================================
echo.

REM 提示用户
echo [READY] Flow %FLOW_ID% 已就绪
echo.
echo 下一步:
echo   1. 在工作目录中开始你的任务
echo   2. 完成后运行：py 30-scripts-tools\session_end.py "完成描述" --flow_id %FLOW_ID%
echo.
echo ============================================================
echo.

endlocal
