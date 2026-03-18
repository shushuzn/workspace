@echo off
chcp 65001 >nul
echo ============================================================
echo   批判者 v5.0 集成测试
echo ============================================================
echo.

echo [测试 1] 批判者审查工具
echo ------------------------------------------------------------
py 30-scripts-tools\critic_v5_review.py --list
echo.

echo [测试 2] file-organizer.py 集成检查
echo ------------------------------------------------------------
py 30-scripts-tools\file-organizer.py --help 2>&1 | findstr /c:"--no-critic"
if errorlevel 1 (
    echo [FAIL] 未找到--no-critic 参数
) else (
    echo [OK] file-organizer.py 集成成功
)
echo.

echo [测试 3] 检查工具集成
echo ------------------------------------------------------------
findstr /c:"critic_v5_review" 30-scripts-tools\file-organizer.py >nul
if errorlevel 1 (
    echo [FAIL] file-organizer.py 未集成
) else (
    echo [OK] file-organizer.py 已集成
)

findstr /c:"critic_v5_review" 30-scripts-tools\optimize-tools-quick.py >nul
if errorlevel 1 (
    echo [FAIL] optimize-tools-quick.py 未集成
) else (
    echo [OK] optimize-tools-quick.py 已集成
)

findstr /c:"critic_v5_review" 30-scripts-tools\cleanup-60data-sensitive.py >nul
if errorlevel 1 (
    echo [FAIL] cleanup-60data-sensitive.py 未集成
) else (
    echo [OK] cleanup-60data-sensitive.py 已集成
)
echo.

echo ============================================================
echo   测试完成!
echo ============================================================
pause
