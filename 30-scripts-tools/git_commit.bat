@echo off
chcp 65001 >nul
cd /d D:\OpenClaw\workspace

REM Git Commit Helper - 使用变量避免空格问题
REM 用法：git_commit "提交消息"

set "MSG=%~1"

git add -u
git commit -m "%MSG%"
git push origin master

if %errorlevel% equ 0 (
    echo [OK] Git 推送成功
) else (
    echo [WARN] Git 推送失败，但本地提交已完成
)
