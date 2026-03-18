@echo off
chcp 65001 >nul
echo ============================================================
echo   Alibaba Cloud ECS Integration Setup
echo   阿里云 ECS 接入配置工具
echo ============================================================
echo.

py 30-scripts-tools\01-SETUP\setup-aliyun-ecs.py

pause
