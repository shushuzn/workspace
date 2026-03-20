@echo off
chcp 65001 >nul
REM Git Wrapper - 防止绕过防护
REM 用法：git_wrapper.bat commit -m "message"

REM 检查禁止的参数
echo %* | findstr /i /c:"--no-verify" /c:"--no-hooks" /c:"-n " >nul
if %errorlevel% equ 0 (
    echo ========================================
    echo [BLOCK] Git 命令被拒绝
    echo [BLOCK] 禁止的参数：--no-verify / --no-hooks / -n
    echo [BLOCK] 不允许绕过 pre-commit hook
    echo ========================================
    exit /b 1
)

REM 检查 session
if not exist "flow-archive\20260318-universal-workflow-001\execution-state.json" (
    echo ========================================
    echo [BLOCK] Git 命令被拒绝
    echo [BLOCK] 原因：execution-state.json 不存在
    echo [BLOCK] 请先运行：py 30-scripts-tools\copaw_entry.py ^<task^>
    echo ========================================
    exit /b 1
)

REM 执行 git 命令
git %*
