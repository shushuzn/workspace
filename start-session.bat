@echo off
chcp 65001 >nul
cd /d D:\OpenClaw\workspace

echo ========================================
echo 启动新会话 (强制工作流检查)
echo ========================================
echo.

REM 步骤 1: 运行工作流强制执行检查
echo [Step 1] 检查工作流合规性...
py 30-scripts-tools\workflow_enforcer.py

if errorlevel 1 (
    echo.
    echo [FAIL] 工作流检查失败！
    echo 请先按主工作流执行必需步骤
    echo.
    echo 主工作流步骤:
    echo   Step 1: 上下文加载验证
    echo   Step 2: Flow ID 绑定
    echo   Step 3: 任务解析
    echo   ...
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] 工作流检查通过
echo.

REM 步骤 2: 显示今日笔记状态
echo [Step 2] 检查当日笔记...
if exist "13-memory\2026-03-20.md" (
    for %%A in ("13-memory\2026-03-20.md") do set SIZE=%%~zA
    if %SIZE% GTR 5120 (
        echo [WARN] 当日笔记过大
    ) else (
        echo [OK] 当日笔记大小正常
    )
) else (
    echo [INFO] 今日笔记尚未创建
)

echo.
echo ========================================
echo [OK] 会话启动准备完成
echo ========================================
echo.
echo 请开始执行主工作流:
echo   Step 1: 上下文加载验证
echo   Step 2: Flow ID 绑定
echo   Step 3: 任务解析
echo   ...
echo.
echo 会话结束后记得:
echo   Step 11: 会话压缩保存
echo   Step 12: Git 提交推送
echo.
pause
