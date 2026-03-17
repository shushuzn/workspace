#!/usr/bin/env pwsh
<#
.SYNOPSIS
    配置 arXiv Research Orchestrator 定时任务
    每日 3am 自动执行

.DESCRIPTION
    创建 Windows 定时任务，每日 3am 自动运行编排脚本
#>

$TaskName = "arxiv-research-orchestrator"
$TaskPath = "\OpenClaw\"
$ScriptPath = "D:\OpenClaw\workspace\30-scripts\arxiv-research-orchestrator.ps1"
$TriggerTime = "3:00 AM"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Setup arXiv Orchestrator Task" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# 检查脚本是否存在
if (-not (Test-Path $ScriptPath)) {
    Write-Host "ERROR: Script not found: $ScriptPath" -ForegroundColor Red
    exit 1
}

# 创建任务路径
try {
    $folder = schtasks /Query /TN $TaskPath 2>$null
    if (-not $folder) {
        Write-Host "Creating task folder: $TaskPath" -ForegroundColor Yellow
        schtasks /Create /TN $TaskPath /TR "echo Creating folder" /SC ONCE /ST "00:00" /F 2>$null | Out-Null
    }
} catch {
    Write-Host "WARNING: Could not check folder: $_" -ForegroundColor Yellow
}

# 删除旧任务 (如果存在)
Write-Host "Removing old task (if exists)..." -ForegroundColor Yellow
schtasks /Delete /TN "$TaskPath\$TaskName" /F 2>$null | Out-Null

# 创建新任务
Write-Host "`nCreating scheduled task..." -ForegroundColor Yellow
Write-Host "  Task Name: $TaskName" -ForegroundColor Gray
Write-Host "  Schedule: Daily at $TriggerTime" -ForegroundColor Gray
Write-Host "  Script: $ScriptPath" -ForegroundColor Gray

$action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`""

$trigger = New-ScheduledTaskTrigger -Daily -At (Get-Date -Hour 3 -Minute 0 -Second 0)

$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Highest

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -WakeToRun

Register-ScheduledTask `
    -TaskName $TaskName `
    -TaskPath $TaskPath `
    -Action $action `
    -Trigger $trigger `
    -Principal $principal `
    -Settings $settings `
    -Description "Daily arXiv paper collection and AI Research OS analysis" `
    -ErrorAction Stop

Write-Host "`nTask created successfully!" -ForegroundColor Green

# 验证任务
Write-Host "`nVerifying task..." -ForegroundColor Yellow
$task = Get-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath -ErrorAction SilentlyContinue

if ($task) {
    Write-Host "  Task Name: $($task.TaskName)" -ForegroundColor Green
    Write-Host "  State: $($task.State)" -ForegroundColor Green
    Write-Host "  Next Run: $((Get-ScheduledTaskInfo -TaskName $TaskName -TaskPath $TaskPath).NextRunTime)" -ForegroundColor Green
} else {
    Write-Host "  WARNING: Task verification failed" -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Manual Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nRun manually with:" -ForegroundColor White
Write-Host "  powershell -File `"$ScriptPath`"" -ForegroundColor Gray
Write-Host "`nOr run now to test:" -ForegroundColor White

$runNow = Read-Host "Run now? (y/n)"
if ($runNow -eq 'y' -or $runNow -eq 'Y') {
    Write-Host "`nRunning orchestrator..." -ForegroundColor Yellow
    & $ScriptPath
}

Write-Host "`nDone!`n" -ForegroundColor Green
