@echo off
chcp 65001 >nul
title OpenClaw - Cursor Mode

echo ========================================
echo   OpenClaw Cursor Mode
echo ========================================
echo.
echo 工作区：D:\OpenClaw\workspace
echo 模式：Cursor 编程模式
echo 自动执行：已启用
echo.
echo 可用命令:
echo   copaw "任务描述" - 执行任务
echo   copaw --cursor "代码任务" - 编程模式
echo   copaw --auto "自动化任务" - 自动模式
echo.
echo 快捷键:
echo   Ctrl+C - 中断当前任务
echo   Ctrl+Z - 撤销上次修改
echo.
pause
