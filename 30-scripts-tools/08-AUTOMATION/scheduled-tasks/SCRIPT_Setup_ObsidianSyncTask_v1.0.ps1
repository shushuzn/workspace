# Obsidian Auto Sync - Task Scheduler Setup
# Run as Administrator

$taskName = "Obsidian-Auto-Sync"
$scriptPath = "D:\OpenClaw\workspace\scripts\obsidian-auto-sync.ps1"
$taskUser = "huawei"
$syncInterval = 30

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Obsidian Auto Sync Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $scriptPath)) {
    Write-Host "ERROR: Script not found: $scriptPath" -ForegroundColor Red
    exit 1
}

Write-Host "Task: $taskName" -ForegroundColor Green
Write-Host "Script: $scriptPath" -ForegroundColor Green
Write-Host "Interval: Every $syncInterval minutes" -ForegroundColor Green
Write-Host ""

$action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`""

$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) `
    -RepetitionInterval (New-TimeSpan -Minutes $syncInterval) `
    -RepetitionDuration (New-TimeSpan -Days 3650)

$principal = New-ScheduledTaskPrincipal -UserId $taskUser -LogonType Interactive -RunLevel Highest

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 10)

Write-Host "Creating task..." -ForegroundColor Yellow

try {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    
    Register-ScheduledTask `
        -TaskName $taskName `
        -Action $action `
        -Trigger $trigger `
        -Principal $principal `
        -Settings $settings `
        -Force `
        -ErrorAction Stop
    
    Write-Host ""
    Write-Host "[OK] Task created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Verify: Get-ScheduledTask -TaskName `"$taskName`""
    Write-Host "Test: Start-ScheduledTask -TaskName `"$taskName`""
    Write-Host ""
}
catch {
    Write-Host ""
    Write-Host "[ERROR] Failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Run this script as Administrator" -ForegroundColor Yellow
    exit 1
}
