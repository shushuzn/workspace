@echo off
REM Feishu-UI Sync Launcher
REM 启动飞书 ↔ UI 消息同步服务

echo ========================================
echo 🚀 Feishu-UI Sync Service
echo ========================================
echo.
echo 启动参数:
echo - 同步间隔：30 秒
echo - 网关地址：http://127.0.0.1:18789
echo - 飞书用户：ou_72a847b95fc25870dcdd8ce56d929252
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

cd /d D:\OpenClaw\workspace
py 30-scripts\feishu-ui-sync.py --watch --interval 30

pause
