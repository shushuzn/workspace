@echo off
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d D:\OpenClaw\workspace

echo ============================================================
echo 工具集成自动化脚本
echo ============================================================
echo.

echo [Step 1] 注册工具到 tools_registry.json...
py 30-scripts-tools\auto_register_tools.py

echo.
echo [Step 2] 集成到 tool_executor.py...
py 30-scripts-tools\integrate_tools.py

echo.
echo [Step 3] 验证集成结果...
py 30-scripts-tools\integration_validator.py --all

echo.
echo [Step 4] Git 提交...
git add -A
git commit -m "feat: integrate 7 new tools - registration + tool_executor integration"
git push origin master

echo.
echo ============================================================
echo 集成完成！
echo ============================================================
