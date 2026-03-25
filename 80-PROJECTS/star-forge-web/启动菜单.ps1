# Star Forge Web Launch Menu
# PowerShell Interactive Startup Script
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Clear-Host
Write-Host ""
Write-Host "  ====================================" -ForegroundColor Cyan
Write-Host "      Star Forge Web Launcher     " -ForegroundColor Cyan
Write-Host "  ====================================" -ForegroundColor Cyan
Write-Host ""

Set-Location -Path $PSScriptRoot

# Check dependencies
if (-not (Test-Path "node_modules")) {
    Write-Host "First run, installing dependencies..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Installation failed!" -ForegroundColor Red
        Read-Host "Press Enter to exit..."
        exit 1
    }
    Write-Host "Dependencies installed!" -ForegroundColor Green
    Clear-Host
}

Write-Host "Select startup mode:" -ForegroundColor White
Write-Host ""
Write-Host "  [1] Development Mode (dev)" -ForegroundColor Green
Write-Host "      Hot reload enabled" -ForegroundColor Gray
Write-Host "      Best for development" -ForegroundColor Gray
Write-Host ""
Write-Host "  [2] Preview Mode" -ForegroundColor Cyan
Write-Host "      Production build" -ForegroundColor Gray
Write-Host "      Best for testing" -ForegroundColor Gray
Write-Host ""
Write-Host "  [3] Build for Production" -ForegroundColor Yellow
Write-Host "      Optimize code" -ForegroundColor Gray
Write-Host "      Generate dist folder" -ForegroundColor Gray
Write-Host ""
Write-Host "  [4] Clean Cache" -ForegroundColor Magenta
Write-Host "      Remove node_modules and dist" -ForegroundColor Gray
Write-Host "      Reinstall dependencies" -ForegroundColor Gray
Write-Host ""
Write-Host "  [5] View Guide" -ForegroundColor Blue
Write-Host "      Display detailed guide" -ForegroundColor Gray
Write-Host ""
Write-Host "  [0] Exit" -ForegroundColor Red
Write-Host ""

$choice = Read-Host "Enter option [1-5, 0]"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Starting development server..." -ForegroundColor Green
        Write-Host "   Press Ctrl+C to stop server" -ForegroundColor Gray
        Write-Host ""
        npm run dev
    }
    "2" {
        Write-Host ""
        Write-Host "Starting preview server..." -ForegroundColor Cyan
        Write-Host "   Press Ctrl+C to stop server" -ForegroundColor Gray
        Write-Host ""
        npm run preview
    }
    "3" {
        Write-Host ""
        Write-Host "Building for production..." -ForegroundColor Yellow
        npm run build
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "Build complete! Check dist folder" -ForegroundColor Green
        } else {
            Write-Host ""
            Write-Host "Build failed!" -ForegroundColor Red
        }
        Read-Host "Press Enter to return to menu..."
        & $PSCommandPath
    }
    "4" {
        Write-Host ""
        Write-Host "Cleaning cache..." -ForegroundColor Magenta
        
        if (Test-Path "node_modules") {
            Write-Host "   Removing node_modules..." -ForegroundColor Gray
            Remove-Item -Path "node_modules" -Recurse -Force
        }
        
        if (Test-Path "dist") {
            Write-Host "   Removing dist..." -ForegroundColor Gray
            Remove-Item -Path "dist" -Recurse -Force
        }
        
        if (Test-Path "package-lock.json") {
            Write-Host "   Removing package-lock.json..." -ForegroundColor Gray
            Remove-Item -Path "package-lock.json" -Force
        }
        
        Write-Host ""
        Write-Host "Installing dependencies..." -ForegroundColor Cyan
        npm install
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "Clean and install complete!" -ForegroundColor Green
        } else {
            Write-Host ""
            Write-Host "Installation failed!" -ForegroundColor Red
        }
        
        Read-Host "Press Enter to return to menu..."
        & $PSCommandPath
    }
    "5" {
        Clear-Host
        Write-Host ""
        Write-Host "  ====================================" -ForegroundColor Cyan
        Write-Host "       Star Forge Web Guide           " -ForegroundColor Cyan
        Write-Host "  ====================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "[Introduction]" -ForegroundColor Yellow
        Write-Host "  Star Forge Web is a farm-building game." -ForegroundColor White
        Write-Host "  Collect energy, build structures, buy upgrades, unlock achievements." -ForegroundColor White
        Write-Host ""
        Write-Host "[Startup Methods]" -ForegroundColor Yellow
        Write-Host "  Method 1: Double-click 启动菜单.ps1 (Recommended)" -ForegroundColor White
        Write-Host "  Method 2: Double-click 启动游戏.bat" -ForegroundColor White
        Write-Host "  Method 3: Run npm run dev in terminal" -ForegroundColor White
        Write-Host ""
        Write-Host "[Game Features]" -ForegroundColor Yellow
        Write-Host "  - Energy collection" -ForegroundColor White
        Write-Host "  - Building system" -ForegroundColor White
        Write-Host "  - Upgrade system" -ForegroundColor White
        Write-Host "  - Achievement system" -ForegroundColor White
        Write-Host "  - Prestige system" -ForegroundColor White
        Write-Host "  - Auto-save system" -ForegroundColor White
        Write-Host ""
        Write-Host "[Shortcut Operations]" -ForegroundColor Yellow
        Write-Host "  - Click 🌐 button to switch language" -ForegroundColor White
        Write-Host "  - Click ☀️/🌙 button to switch theme" -ForegroundColor White
        Write-Host "  - Click ⚙️ button to open settings" -ForegroundColor White
        Write-Host "  - Use tabs to switch panels" -ForegroundColor White
        Write-Host "  - Choose quality level (Low/Medium/High)" -ForegroundColor White
        Write-Host ""
        Write-Host "[File Locations]" -ForegroundColor Yellow
        Write-Host "  - Save location: localStorage" -ForegroundColor White
        Write-Host "  - Theme settings: localStorage" -ForegroundColor White
        Write-Host "  - Language settings: localStorage" -ForegroundColor White
        Write-Host "  - Quality settings: localStorage" -ForegroundColor White
        Write-Host ""
        Read-Host "Press Enter to return to menu..."
        & $PSCommandPath
    }
    "0" {
        Write-Host ""
        Write-Host "Thanks for using Star Forge Web!" -ForegroundColor Cyan
        Start-Sleep -Seconds 1
        exit 0
    }
    default {
        Write-Host ""
        Write-Host "Invalid option, please select again!" -ForegroundColor Red
        Start-Sleep -Seconds 1
        & $PSCommandPath
    }
}
