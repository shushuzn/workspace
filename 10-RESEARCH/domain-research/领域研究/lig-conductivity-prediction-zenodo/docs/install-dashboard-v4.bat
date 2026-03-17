@echo off
chcp 65001 >nul
echo.
echo 🚀 Dashboard API v4 依赖安装
echo ========================================
echo.

echo 正在安装 Python 依赖...
echo.

pip install fastapi uvicorn[standard] aiohttp redis psutil

echo.
echo ✅ 依赖安装完成!
echo.
echo 下一步:
echo   1. 启动服务器：python dashboard-api-v4.py
echo   2. 运行压力测试：python load_test_v4.py --requests 500 --concurrent 50
echo.
pause
