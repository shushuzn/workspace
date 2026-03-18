#!/usr/bin/env pwsh
# Setup Audit Tasks - 设置定时审计任务
# Usage: .\setup-audit-tasks.ps1

Write-Host "Setting up audit tasks..." -ForegroundColor Cyan
Write-Host ""

$scriptPath = "D:\OpenClaw\workspace\30-scripts\run-all-audit.ps1"

# Weekly audit - Every Sunday 6:00 AM
Write-Host "[1/2] Creating weekly audit task..." -ForegroundColor Yellow

$action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`""
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 6am
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Highest

try {
    Register-ScheduledTask -TaskName "OpenClaw-Weekly-Audit" `
        -Action $action `
        -Trigger $trigger `
        -Principal $principal `
        -Description "Weekly link network audit" `
        -ErrorAction Stop
    Write-Host "  Created: OpenClaw-Weekly-Audit (Every Sunday 6:00 AM)" -ForegroundColor Green
} catch {
    Write-Host "  Failed: $_" -ForegroundColor Red
    Write-Host "  Hint: Run as Administrator" -ForegroundColor Yellow
}

Write-Host ""

# Monthly heat analysis - 1st of each month 7:00 AM
Write-Host "[2/2] Creating monthly heat analysis task..." -ForegroundColor Yellow

$heatScript = "D:\OpenClaw\workspace\30-scripts\analyze-link-heat.ps1"
$action2 = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$heatScript`""
$trigger2 = New-ScheduledTaskTrigger -Monthly -DaysOfMonth 1 -At 7am

try {
    Register-ScheduledTask -TaskName "OpenClaw-Monthly-Heat-Analysis" `
        -Action $action2 `
        -Trigger $trigger2 `
        -Principal $principal `
        -Description "Monthly link heat analysis" `
        -ErrorAction Stop
    Write-Host "  Created: OpenClaw-Monthly-Heat-Analysis (1st of month 7:00 AM)" -ForegroundColor Green
} catch {
    Write-Host "  Failed: $_" -ForegroundColor Red
    Write-Host "  Hint: Run as Administrator" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete" -ForegroundColor Cyan
Write-Host "========================================"
Write-Host ""
Write-Host "Scheduled tasks:"
Write-Host "  1. Weekly Audit - Every Sunday 6:00 AM"
Write-Host "  2. Monthly Heat Analysis - 1st of month 7:00 AM"
Write-Host ""
Write-Host "To view tasks:"
Write-Host "  Get-ScheduledTask | Where-Object TaskName -like 'OpenClaw*'"
Write-Host ""
Write-Host "To remove tasks:"
Write-Host "  Unregister-ScheduledTask -TaskName 'OpenClaw-Weekly-Audit' -Confirm:`$false"
Write-Host "  Unregister-ScheduledTask -TaskName 'OpenClaw-Monthly-Heat-Analysis' -Confirm:`$false"
Write-Host ""
