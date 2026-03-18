@echo off
chcp 65001 >nul
REM ============================================================
REM   批判者 v5.0 - Git 操作审查
REM ============================================================
REM 
REM 功能:
REM   在 git commit 前自动运行批判者审查
REM   检查提交质量、代码质量、安全性等
REM 
REM 使用:
REM   critic-git.bat
REM 
REM ============================================================

echo ============================================================
echo   批判者 v5.0 - Git 操作审查
echo ============================================================
echo.

REM 检查 Python
where py >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 未安装或未添加到 PATH
    echo 请先安装 Python 3.x
    pause
    exit /b 1
)

REM 运行批判者审查
py 30-scripts-tools\critic_v5_review.py --scenario git_operation

if errorlevel 1 (
    echo.
    echo ============================================================
    echo   批判者审查未通过
    echo ============================================================
    echo.
    echo 建议:
    echo   1. 根据审查结果修复问题
    echo   2. 或创建 skip_critic.txt 跳过审查
    echo   3. 或使用 git commit --no-verify 强制提交
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   批判者审查通过 - 可以继续提交
echo ============================================================
echo.
pause
