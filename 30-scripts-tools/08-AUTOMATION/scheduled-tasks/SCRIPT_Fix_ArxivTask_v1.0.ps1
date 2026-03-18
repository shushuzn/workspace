# Fix Arxiv Collector Scheduled Task
# Run as Administrator

$TaskName = "OpenClaw-Arxiv-Collector"
$ScriptPath = "D:\OpenClaw\workspace\arxiv-workflow.ps1"
$TaskTime = "02:00"

Write-Host "Updating scheduled task: $TaskName" -ForegroundColor Cyan
Write-Host "New script path: $ScriptPath" -ForegroundColor Cyan
Write-Host "Task time: $TaskTime`n" -ForegroundColor Cyan

# Delete existing task
Write-Host "Removing old task..." -ForegroundColor Yellow
schtasks /Delete /TN $TaskName /F

# Create new task
Write-Host "Creating new task..." -ForegroundColor Yellow
$action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-ExecutionPolicy Bypass -File `"$ScriptPath`" -Mode all"
$trigger = New-ScheduledTaskTrigger -Daily -At $TaskTime
$principal = New-ScheduledTaskPrincipal -UserId "LAPTOP-229KNBOJ\huawei" -LogonType S4U -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Principal $principal `
    -Settings $settings `
    -Force `
    -Description "Daily arXiv paper collection workflow (fixed path)"

if ($?) {
    Write-Host "`n[SUCCESS] Task updated successfully!" -ForegroundColor Green
    Write-Host "Next run time: $(Get-ScheduledTaskInfo -TaskName $TaskName).NextRunTime" -ForegroundColor Green
} else {
    Write-Host "`n[FAILED] Task update failed!" -ForegroundColor Red
    Write-Host "Please run this script as Administrator" -ForegroundColor Red
}
