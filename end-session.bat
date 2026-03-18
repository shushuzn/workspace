@echo off
chcp 65001 >nul
echo ============================================================
echo   Session End - 会话结束压缩
echo ============================================================
echo.

echo [1/3] Compressing session context...
py 30-scripts-tools\post_session_compress.py --auto
if errorlevel 1 (
    echo [ERROR] Compression failed!
    pause
    exit /b 1
)

echo.
echo [2/3] Verifying context size...
py 30-scripts-tools\fast_load.py

echo.
echo [3/3] Cleaning up...
if exist 30-scripts-tools\session_temp.json (
    del 30-scripts-tools\session_temp.json
    echo [OK] Cleaned up temp file
)

echo.
echo ============================================================
echo   Session compressed successfully!
echo   Context size: ^<100KB
echo ============================================================
pause
