@echo off
chcp 65001 >nul
title Cursor IDE

:: 启动 Cursor，打开指定文件或工作区
if "%1"=="" (
    "D:\cursor\resources\cursor.exe" "D:\OpenClaw\workspace"
) else (
    "D:\cursor\resources\cursor.exe" %*
)
