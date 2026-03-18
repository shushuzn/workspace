@echo off
chcp 65001 >nul
REM ============================================================
REM   批判者 v5.0 - 通用启动器
REM ============================================================
REM 
REM 功能:
REM   选择并运行批判者审查场景
REM 
REM 使用:
REM   critic.bat [scenario]
REM 
REM 场景:
REM   git_operation   - Git 操作审查
REM   file_organize   - 文件整理审查
REM   tool_optimize   - 工具优化审查
REM   data_cleanup    - 数据清理审查
REM   research_start  - 研究启动审查
REM   memory_operation - 记忆系统操作
REM   api_key         - API 密钥审查
REM   report_generate - 报告生成审查
REM 
REM ============================================================

if "%1"=="" (
    echo ============================================================
    echo   批判者 v5.0 - 选择审查场景
    echo ============================================================
    echo.
    echo 可用场景:
    echo   1. git_operation   - Git 操作审查
    echo   2. file_organize   - 文件整理审查
    echo   3. tool_optimize   - 工具优化审查
    echo   4. data_cleanup    - 数据清理审查
    echo   5. research_start  - 研究启动审查
    echo   6. memory_operation - 记忆系统操作
    echo   7. api_key         - API 密钥审查
    echo   8. report_generate - 报告生成审查
    echo.
    set /p choice="请选择场景 (1-8): "
    
    if "%choice%"=="1" set scenario=git_operation
    if "%choice%"=="2" set scenario=file_organize
    if "%choice%"=="3" set scenario=tool_optimize
    if "%choice%"=="4" set scenario=data_cleanup
    if "%choice%"=="5" set scenario=research_start
    if "%choice%"=="6" set scenario=memory_operation
    if "%choice%"=="7" set scenario=api_key
    if "%choice%"=="8" set scenario=report_generate
    
    if "%scenario%"=="" (
        echo [ERROR] 无效选择
        pause
        exit /b 1
    )
) else (
    set scenario=%1
)

echo.
echo ============================================================
echo   运行批判者 v5.0 - %scenario%
echo ============================================================
echo.

where py >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 未安装
    pause
    exit /b 1
)

py 30-scripts-tools\critic_v5_review.py --scenario %scenario%

if errorlevel 1 (
    echo.
    echo ============================================================
    echo   批判者审查未通过
    echo ============================================================
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   批判者审查通过
echo ============================================================
pause
