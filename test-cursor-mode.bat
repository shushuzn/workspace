@echo off
chcp 65001 >nul
title OpenClaw - Cursor Mode 测试

echo.
echo ========================================
echo   OpenClaw Cursor Mode 验证测试
echo ========================================
echo.

echo [1/6] 检查配置文件...
if exist "%USERPROFILE%\.copaw\config-cursor.json" (
    echo [✓] 主配置文件已创建
) else (
    echo [✗] 主配置文件缺失
)

if exist ".openclaw\config.json" (
    echo [✓] 工作区配置已创建
) else (
    echo [✗] 工作区配置缺失
)

echo.
echo [2/6] 检查工具脚本...
if exist "30-scripts-tools\cursor_code_executor.py" (
    echo [✓] cursor_code_executor.py 已创建
) else (
    echo [✗] cursor_code_executor.py 缺失
)

if exist "30-scripts-tools\tool_call_interceptor.py" (
    echo [✓] tool_call_interceptor.py 已创建
) else (
    echo [✗] tool_call_interceptor.py 缺失
)

echo.
echo [3/6] 检查启动脚本...
if exist "copaw.bat" (
    echo [✓] copaw.bat 已创建
) else (
    echo [✗] copaw.bat 缺失
)

if exist "cursor-mode.bat" (
    echo [✓] cursor-mode.bat 已创建
) else (
    echo [✗] cursor-mode.bat 缺失
)

echo.
echo [4/6] 检查环境变量...
echo OPENCLAW_CURSOR_MODE=%OPENCLAW_CURSOR_MODE%
echo OPENCLAW_AUTO_EXECUTE=%OPENCLAW_AUTO_EXECUTE%
echo OPENCLAW_WORKSPACE=%OPENCLAW_WORKSPACE%

echo.
echo [5/6] 测试代码执行器...
py 30-scripts-tools\cursor_code_executor.py structure 2>nul | findstr /C:"├──" /C:"└──" >nul
if errorlevel 1 (
    echo [⚠] 项目结构获取失败 (正常，首次运行)
) else (
    echo [✓] 项目结构获取成功
)

echo.
echo [6/6] 检查 MCP 服务器...
npx -y @modelcontextprotocol/server-filesystem --version >nul 2>&1
if errorlevel 1 (
    echo [⚠] MCP filesystem 未响应 (可能未安装)
) else (
    echo [✓] MCP filesystem 已安装
)

echo.
echo ========================================
echo   验证完成!
echo ========================================
echo.
echo 使用方法:
echo   copaw.bat "你的编程任务"
echo.
echo 示例:
echo   copaw.bat "读取 game.js 并分析代码结构"
echo   copaw.bat "搜索所有包含 totalClicks 的文件"
echo.
pause
