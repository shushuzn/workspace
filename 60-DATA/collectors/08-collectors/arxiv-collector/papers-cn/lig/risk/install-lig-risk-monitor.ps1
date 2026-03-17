# Install LIG Risk Monitor Scheduled Task
# Function: Install LIG risk warning scheduled task (Daily 7AM)
# Created: 2026-03-13 (Critic v5.0 Task #4)
# Usage: Run as Administrator

$taskName = "LIG-Risk-Monitor"
$scriptPath = "D:\OpenClaw\workspace\40-arxiv-论文收集\lig\risk\lig-risk-monitor.py"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Install LIG Risk Monitor Task" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if script exists
if (-not (Test-Path $scriptPath)) {
    Write-Host "ERROR: Script not found at $scriptPath" -ForegroundColor Red
    Write-Host "Please verify the script path." -ForegroundColor Yellow
    exit 1
}

Write-Host "[1/3] Script found: $scriptPath" -ForegroundColor Green

# Create scheduled task
$action = New-ScheduledTaskAction -Execute "py.exe" -Argument "`"$scriptPath`""
$trigger = New-ScheduledTaskTrigger -Daily -At 7am
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Write-Host "[2/3] Creating scheduled task..." -ForegroundColor Yellow

try {
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Force | Out-Null
    Write-Host "[3/3] Task registered successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Task Details:" -ForegroundColor Cyan
    Write-Host "  Name: $taskName" -ForegroundColor White
    Write-Host "  Schedule: Daily at 7:00 AM" -ForegroundColor White
    Write-Host "  Script: $scriptPath" -ForegroundColor White
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Installation Complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
}
catch {
    Write-Host "ERROR: Failed to register task" -ForegroundColor Red
    Write-Host "Details: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please run this script as Administrator." -ForegroundColor Yellow
    exit 1
}
