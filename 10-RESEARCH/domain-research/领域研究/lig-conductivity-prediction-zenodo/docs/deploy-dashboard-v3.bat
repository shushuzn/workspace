@echo off
REM Innovator Dashboard v3.0 - Windows Batch Deployment Script
REM Uses SSH/SCP commands for deployment

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║     🚀 Innovator Dashboard v3.0 - Auto Deploy Script     ║
echo ║              Target: 8.208.30.28 (UK London)             ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

set SERVER=root@8.208.30.28
set REMOTE_DIR=/root/dashboard-v3
set PORT=8446

echo Step 1: Creating remote directory...
ssh %SERVER% "mkdir -p %REMOTE_DIR%"
if errorlevel 1 (
    echo Failed to create remote directory
    exit /b 1
)
echo ✓ Remote directory created

echo.
echo Step 2: Uploading files...
scp dashboard-api-v3.py %SERVER%:%REMOTE_DIR%/
scp innovator-dashboard-v3.html %SERVER%:%REMOTE_DIR%/
scp -r dashboard-data %SERVER%:%REMOTE_DIR%/
if errorlevel 1 (
    echo Failed to upload files
    exit /b 1
)
echo ✓ Files uploaded

echo.
echo Step 3: Installing dependencies...
ssh %SERVER% "pip3 install psutil -q"
echo ✓ Dependencies installed

echo.
echo Step 4: Stopping existing server...
ssh %SERVER% "pkill -f 'dashboard-api-v3.py' 2^>^/dev/null || true"
echo ✓ Existing server stopped

echo.
echo Step 5: Starting new server...
ssh %SERVER% "cd %REMOTE_DIR% && nohup python3 dashboard-api-v3.py ^> dashboard.log 2^>^&1 ^&"
echo ✓ Server started

echo.
echo Step 6: Configuring firewall...
ssh %SERVER% "ufw allow %PORT%/tcp 2^>^/dev/null || true"
echo ✓ Firewall configured

echo.
echo Step 7: Verifying deployment...
timeout /t 3 /nobreak >nul
ssh %SERVER% "curl -s http://localhost:%PORT%/api/health | findstr local"
if errorlevel 1 (
    echo ⚠ Warning: Health check may have failed
) else (
    echo ✓ Health check passed
)

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║           🎭 Innovator Dashboard v3.0 LIVE!              ║
echo ╠══════════════════════════════════════════════════════════╣
echo ║                                                          ║
echo ║  🌐 Access URLs:                                         ║
echo ║  • Dashboard:   http://8.208.30.28:%PORT%/                      ║
echo ║  • API:         http://8.208.30.28:%PORT%/api/dashboard         ║
echo ║                                                          ║
echo ║  📁 Remote Location: %REMOTE_DIR%                   ║
echo ║  🔄 Auto-refresh: Every 5 minutes                        ║
echo ║                                                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo Deployment complete!
pause
