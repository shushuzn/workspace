@echo off
chcp 65001 >nul
REM ========================================
REM 会话结束自动化脚本 v2.0
REM 功能：压缩 + 蒸馏 + Git 提交
REM ========================================

echo.
echo ========================================
echo   会话结束自动化 v2.0
echo ========================================
echo.

REM 1. 会话压缩
echo [1/3] 会话压缩...
python 30-scripts-tools\post_session_compress.py --auto
if %ERRORLEVEL% NEQ 0 (
    echo [WARN] 会话压缩失败，继续执行...
)
echo.

REM 2. 实时蒸馏
echo [2/3] 实时蒸馏...
python 30-scripts-tools\real_time_distill_v3.py
if %ERRORLEVEL% NEQ 0 (
    echo [WARN] 实时蒸馏失败，继续执行...
)
echo.

REM 3. Git 提交
echo [3/3] Git 提交...
python 30-scripts-tools\memory_git_auto_commit.py
if %ERRORLEVEL% NEQ 0 (
    echo [WARN] Git 提交失败
)
echo.

echo ========================================
echo   会话结束完成！
echo ========================================
echo.

pause
