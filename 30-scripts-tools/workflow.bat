@echo off
chcp 65001 >nul
title Workflow Quick Commands

echo.
echo ============================================================
echo  🔧 工作流快捷命令
echo ============================================================
echo  1. 查看状态          (status)
echo  2. 完成当前步骤      (next)
echo  3. 查看待办          (todo)
echo  4. 启动新会话        (start)
echo  0. 退出
echo ============================================================
echo.

set /p choice=选择操作 [0-4]: 

if "%choice%"=="1" (
    py -X utf8 30-scripts-tools\workflow_menu.py status
) else if "%choice%"=="2" (
    py -X utf8 30-scripts-tools\workflow_menu.py status
    echo.
    set /p step=输入步骤号 (直接回车自动完成当前): 
    if "%step%"=="" (
        py -X utf8 30-scripts-tools\workflow_menu.py complete
    ) else (
        py -X utf8 30-scripts-tools\workflow_menu.py complete %step%
    )
) else if "%choice%"=="3" (
    if exist "TODO.md" (type TODO.md) else (echo 无 TODO.md)
) else if "%choice%"=="4" (
    echo 启动新会话...
    py -X utf8 30-scripts-tools\copaw_entry.py "New Task"
) else if "%choice%"=="0" (
    exit
)

echo.
pause