@echo off
chcp 65001 >nul
title Workflow Commands

echo.
echo ============================================================
echo  🔧 工作流快捷命令
echo ============================================================
echo  status  - 查看当前状态
echo  stats   - 查看统计面板
echo  next    - 完成下一步
echo  complete- 完成指定步骤
echo  reset   - 重置状态
echo  start   - 启动新会话
echo ============================================================
echo.

set /p cmd=输入命令: 

if "%cmd%"=="status" (
    py -X utf8 30-scripts-tools\workflow_menu.py status
) else if "%cmd%"=="stats" (
    py -X utf8 30-scripts-tools\workflow_stats.py
) else if "%cmd%"=="next" (
    py -X utf8 30-scripts-tools\auto_step.py
) else if "%cmd%"=="complete" (
    set /p step=输入步骤号: 
    py -X utf8 30-scripts-tools\workflow_menu.py complete %step%
) else if "%cmd%"=="reset" (
    set /p confirm=确认重置? (y/n): 
    if "%confirm%"=="y" py -X utf8 30-scripts-tools\workflow_menu.py reset
) else if "%cmd%"=="start" (
    set /p task=输入任务名: 
    py -X utf8 30-scripts-tools\copaw_entry.py %task%
) else (
    echo 未知命令
)

echo.
pause