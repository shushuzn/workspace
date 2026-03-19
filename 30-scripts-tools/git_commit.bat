@echo off
chcp 65001 >nul
cd /d D:\OpenClaw\workspace

REM Git Commit Helper - 带重试机制
REM 用法：git_commit "提交消息"

set "MSG=%~1"

echo ========================================
echo Git Commit + Push (with retry)
echo ========================================
echo.

REM 本地提交
git add -u
git commit -m "%MSG%"
if %errorlevel% neq 0 (
    echo [WARN] 本地提交失败，可能没有更改
    goto :check_push
)
echo [OK] 本地提交成功

:check_push
REM 推送前检查 - 测试网络连接
echo.
echo [CHECK] Testing network connection...
git ls-remote --heads origin >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARN] 无法连接到远程仓库，等待 5 秒...
    timeout /t 5 /nobreak >nul
)

REM 推送重试逻辑 (最多 3 次)
set "MAX_RETRIES=3"
set "RETRY_COUNT=0"
set "PUSH_SUCCESS=0"

:push_loop
if %RETRY_COUNT% geq %MAX_RETRIES% goto :push_failed

set /a RETRY_COUNT+=1

if %RETRY_COUNT% equ 1 (
    echo.
    echo [PUSH] Attempt %RETRY_COUNT%/%MAX_RETRIES%...
) else (
    echo.
    echo [RETRY] Attempt %RETRY_COUNT%/%MAX_RETRIES% (waiting 3s)...
    timeout /t 3 /nobreak >nul
    echo [PUSH] Retry attempt %RETRY_COUNT%/%MAX_RETRIES%...
)

git push origin master
if %errorlevel% equ 0 (
    set "PUSH_SUCCESS=1"
    goto :push_success
)

echo [WARN] Push attempt %RETRY_COUNT% failed
goto :push_loop

:push_success
echo.
echo [OK] Git push successful on attempt %RETRY_COUNT%
goto :end

:push_failed
echo.
echo [FAIL] Git push failed after %MAX_RETRIES% attempts
echo [INFO] Local commit is saved, you can push manually later
echo [HINT] Check network connection or run: git push origin master

:end
echo ========================================
if %PUSH_SUCCESS% equ 1 (
    echo [RESULT] SUCCESS
) else (
    echo [RESULT] PARTIAL (local commit OK, push failed)
)
echo ========================================
