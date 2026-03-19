@echo off
REM 完全自动化工作流执行脚本
REM 设置 UTF-8 编码环境变量

set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
chcp 65001 >nul 2>&1

echo [INFO] UTF-8 编码已设置
echo [INFO] 开始执行工作流...
echo.

REM 启动工作流并执行
py 30-scripts-tools\workflow_enforcer.py --start
py 30-scripts-tools\auto_execute_workflow.py

echo.
echo [INFO] 执行完成
