# OpenClaw Scheduled Tasks Setup Script
# Created: 2026-03-04 14:00
# Purpose: Configure all scheduled tasks

$ErrorActionPreference = "Stop"
$Workspace = "D:\OpenClaw\workspace"
$ScriptsDir = "$Workspace\scripts"

Write-Host "OpenClaw Scheduled Tasks Setup" -ForegroundColor Cyan
Write-Host "Workspace: $Workspace"
Write-Host ""

# Task 1: Arxiv Collector (Daily 2AM)
Write-Host "Creating: OpenClaw-Arxiv-Collector" -ForegroundColor Yellow
try {
    $action = New-ScheduledTaskAction -Execute "python" -Argument "scripts/arxiv-daily.py --categories cs.AI,cs.LG,cs.CL --output Medium/Raw/" -WorkingDirectory $Workspace
    $trigger = New-ScheduledTaskTrigger -Daily -At 2am
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Highest
    Register-ScheduledTask -TaskName "OpenClaw-Arxiv-Collector" -Action $action -Trigger $trigger -Principal $principal -Description "Daily arXiv paper collection" -ErrorAction SilentlyContinue
    Write-Host "  OK: Daily 2:00 AM" -ForegroundColor Green
} catch {
    Write-Host "  Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Task 2: Medium Watcher (Daily 4AM)
Write-Host "Creating: OpenClaw-Medium-Watcher" -ForegroundColor Yellow
try {
    $action = New-ScheduledTaskAction -Execute "python" -Argument "scripts/medium-watcher.py --tags ai,llm,ml --output Medium/Raw/" -WorkingDirectory $Workspace
    $trigger = New-ScheduledTaskTrigger -Daily -At 4am
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Highest
    Register-ScheduledTask -TaskName "OpenClaw-Medium-Watcher" -Action $action -Trigger $trigger -Principal $principal -Description "Daily Medium article collection" -ErrorAction SilentlyContinue
    Write-Host "  OK: Daily 4:00 AM" -ForegroundColor Green
} catch {
    Write-Host "  Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Task 3: Nightly Security Audit (Daily 3AM)
Write-Host "Creating: OpenClaw-Nightly-Security-Audit" -ForegroundColor Yellow
try {
    $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File $Workspace\nightly-security-audit.ps1" -WorkingDirectory $Workspace
    $trigger = New-ScheduledTaskTrigger -Daily -At 3am
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Highest
    Register-ScheduledTask -TaskName "OpenClaw-Nightly-Security-Audit" -Action $action -Trigger $trigger -Principal $principal -Description "Daily security audit" -ErrorAction SilentlyContinue
    Write-Host "  OK: Daily 3:00 AM" -ForegroundColor Green
} catch {
    Write-Host "  Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Task 4: Memory Distiller (Weekly Sunday 5AM)
Write-Host "Creating: OpenClaw-Memory-Distiller" -ForegroundColor Yellow
try {
    $action = New-ScheduledTaskAction -Execute "python" -Argument "scripts/memory-distiller.py --input memory/ --output MEMORY.md --period weekly" -WorkingDirectory $Workspace
    $trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 5am
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Highest
    Register-ScheduledTask -TaskName "OpenClaw-Memory-Distiller" -Action $action -Trigger $trigger -Principal $principal -Description "Weekly memory distillation" -ErrorAction SilentlyContinue
    Write-Host "  OK: Weekly Sunday 5:00 AM" -ForegroundColor Green
} catch {
    Write-Host "  Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Task 5: Daily Collect (Daily 9AM)
Write-Host "Creating: OpenClaw-Daily-Collect" -ForegroundColor Yellow
try {
    $action = New-ScheduledTaskAction -Execute "python" -Argument "scripts/collect-all.ps1" -WorkingDirectory $ScriptsDir
    $trigger = New-ScheduledTaskTrigger -Daily -At 9am
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Highest
    Register-ScheduledTask -TaskName "OpenClaw-Daily-Collect" -Action $action -Trigger $trigger -Principal $principal -Description "Daily collection from all sources" -ErrorAction SilentlyContinue
    Write-Host "  OK: Daily 9:00 AM" -ForegroundColor Green
} catch {
    Write-Host "  Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Task 6: Weekly Report (Weekly Monday 10AM)
Write-Host "Creating: OpenClaw-Weekly-Report" -ForegroundColor Yellow
try {
    $action = New-ScheduledTaskAction -Execute "python" -Argument "scripts/report-generator.py weekly" -WorkingDirectory $ScriptsDir
    $trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 10am
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Highest
    Register-ScheduledTask -TaskName "OpenClaw-Weekly-Report" -Action $action -Trigger $trigger -Principal $principal -Description "Weekly report generation" -ErrorAction SilentlyContinue
    Write-Host "  OK: Weekly Monday 10:00 AM" -ForegroundColor Green
} catch {
    Write-Host "  Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "Task Status:" -ForegroundColor Cyan
Get-ScheduledTask -TaskName "OpenClaw-*" | Select-Object TaskName, State, LastRunTime, NextRunTime | Format-Table -AutoSize

Write-Host ""
Write-Host "Tips:" -ForegroundColor Cyan
Write-Host "  - Run task manually: Start-ScheduledTask -TaskName 'TaskName'"
Write-Host "  - View logs: Event Viewer -> Task Scheduler -> Application Logs"
Write-Host "  - Disable task: Disable-ScheduledTask -TaskName 'TaskName'"
Write-Host ""
