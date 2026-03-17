@echo off
chcp 65001 >nul
echo ============================================================
echo [PM Agent v3.0] 产品管理 Agent
echo ============================================================
echo.

cd /d "%~dp0"

python agent-product-manager.py --run

echo.
echo ============================================================
echo 按任意键退出...
pause >nul
