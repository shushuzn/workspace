@echo off
chcp 65001 >nul
REM Safe Shell - 唯一允许的 shell 命令执行入口
REM 所有 shell 命令都通过此包装器

if "%~1"=="" (
    echo ===============================================
    echo [FATAL] 必须提供命令
    echo [FATAL] 用法：safe_shell.bat ^<command^> [description]
    echo ===============================================
    exit /b 1
)

py "%~dp0safe_shell_executor.py" %*
