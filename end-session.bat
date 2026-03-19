@echo off
chcp 65001 >nul
cd /d D:\OpenClaw\workspace

echo ========================================
echo 结束会话 (强制压缩 + 检查)
echo ========================================
echo.

REM 步骤 1: 检查当日笔记
echo [Step 1] 检查当日笔记...
if not exist "13-memory\2026-03-20.md" (
    echo [FAIL] 当日笔记不存在！
    echo 请先创建当日笔记
    pause
    exit /b 1
)

for %%A in ("13-memory\2026-03-20.md") do set SIZE=%%~zA

if %SIZE% GTR 5120 (
    echo [FAIL] 当日笔记过大：%SIZE% bytes (>5KB)
    echo.
    echo 请先压缩当日笔记！
    echo 目标：<5KB
    echo 当前：%SIZE% bytes
    echo.
    pause
    exit /b 1
) else (
    echo [OK] 当日笔记大小正常
)

echo.

REM 步骤 2: 运行 Git 提交前检查
echo [Step 2] Git 提交前合规检查...
py 30-scripts-tools\pre_commit_checker.py

if errorlevel 1 (
    echo.
    echo [FAIL] 合规性检查失败！
    echo 请修复问题后再提交
    pause
    exit /b 1
)

echo.

REM 步骤 3: Git 提交
echo [Step 3] Git 提交...
set /p MSG="输入提交消息: "
if "%MSG%"=="" (
    echo [FAIL] 提交消息不能为空
    pause
    exit /b 1
)

call 30-scripts-tools\git_commit.bat "%MSG%"

if errorlevel 1 (
    echo.
    echo [FAIL] Git 提交失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo [OK] 会话结束完成
echo ========================================
echo.
echo 完成项:
echo   [OK] 当日笔记已压缩
echo   [OK] 合规性检查通过
echo   [OK] Git 提交成功
echo.
echo 下次会话请运行: start-session.bat
echo.
pause
