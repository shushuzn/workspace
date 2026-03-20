@echo off
chcp 65001 >nul
REM Protected PY - 强制防护的 Python 执行器
REM 所有 py 命令都通过此包装器

REM 检查是否有参数
if "%~1"=="" (
    echo ===============================================
    echo [FATAL] 必须提供脚本路径
    echo [FATAL] 用法：protected_py.bat ^<script.py^> [args...]
    echo ===============================================
    exit /b 1
)

REM 执行防护包装器
py "%~dp0protected_py.py" %*
