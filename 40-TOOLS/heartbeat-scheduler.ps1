# Heartbeat Scheduler - Windows Task Scheduler Configuration
# Created: 2026-03-13 (Critic v5.0 fix-007)

param(
    [switch]$Install,
    [switch]$Remove,
    [switch]$Status,
    [switch]$Heartbeat,
    [switch]$Daily
)

$workspace = "D:\OpenClaw\workspace"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "OpenClaw Heartbeat Scheduler" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

function Install-HeartbeatTask {
    Write-Host "[1/2] Installing heartbeat task (every 30 min)" -ForegroundColor Cyan
    
    $taskName = "OpenClaw-Heartbeat"
    $scriptPath = "$workspace\30-scripts-脚本工具\heartbeat-trigger.ps1"
    
    $triggerScript = @'
$workspace = "D:\OpenClaw\workspace"
$logFile = "$workspace\91-logs-日志\heartbeat-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

try {
    "$(Get-Date -Format 'o') - Heartbeat triggered" | Out-File $logFile -Append
    $heartbeatState = Get-Content "$workspace\13-memory-记忆系统\heartbeat-state.json" -Raw | ConvertFrom-Json
    $pendingCount = ($heartbeatState.todo | Where-Object { $_.status -eq 'pending' }).Count
    "$(Get-Date -Format 'o') - Pending tasks: $pendingCount" | Out-File $logFile -Append
    Write-Host "Heartbeat check completed - $pendingCount pending tasks" -ForegroundColor Green
}
catch {
    "$(Get-Date -Format 'o') - ERROR: $_" | Out-File $logFile -Append
    Write-Host "Heartbeat check failed: $_" -ForegroundColor Red
}
'@
    
    $triggerScript | Out-File -FilePath $scriptPath -Encoding UTF8
    Write-Host "  + Trigger script created" -ForegroundColor Green
    
    $action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
        -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`""
    $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 30)
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
    
    try {
        Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Force | Out-Null
        Write-Host "  + Task registered: $taskName" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "  - Registration failed (admin required): $_" -ForegroundColor Red
        return $false
    }
}

function Install-DailyTasks {
    Write-Host ""
    Write-Host "[2/2] Installing daily tasks" -ForegroundColor Cyan
    
    # Domain Ranking (Daily 9AM)
    $taskName = "OpenClaw-Domain-Ranking"
    $scriptPath = "$workspace\30-scripts-脚本工具\10-DOMAIN-RANKING\core\domain_ranker_v2.py"
    
    $action = New-ScheduledTaskAction -Execute "py.exe" `
        -Argument "`"$scriptPath`" --compare"
    $trigger = New-ScheduledTaskTrigger -Daily -At 9am
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
    
    try {
        Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Force | Out-Null
        Write-Host "  + Domain Ranking: $taskName (Daily 9:00 AM)" -ForegroundColor Green
    }
    catch {
        Write-Host "  - Domain Ranking failed: $_" -ForegroundColor Red
    }
    
    # Daily Log (Daily 12AM)
    $taskName = "OpenClaw-Daily-Log"
    $scriptPath = "$workspace\30-scripts-脚本工具\daily-log-creator.ps1"
    
    $logCreatorScript = @'
$workspace = "D:\OpenClaw\workspace"
$today = Get-Date -Format 'yyyy-MM-dd'
$logFile = "$workspace\13-memory-记忆系统\$today.md"

if (-not (Test-Path $logFile)) {
    @"
# $today Work Log

## Plan
- [ ] To be filled

## Execution Record
- [ ] To be recorded
"@ | Out-File -FilePath $logFile -Encoding UTF8
    Write-Host "Daily log created: $logFile"
}
'@
    
    $logCreatorScript | Out-File -FilePath $scriptPath -Encoding UTF8
    
    $action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
        -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`""
    $trigger = New-ScheduledTaskTrigger -Daily -At 12am
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
    
    try {
        Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Force | Out-Null
        Write-Host "  + Daily Log: $taskName (Daily 12:00 AM)" -ForegroundColor Green
    }
    catch {
        Write-Host "  - Daily Log failed: $_" -ForegroundColor Red
    }
    
    # LIG Risk Monitor (Daily 7AM)
    $taskName = "LIG-Risk-Monitor"
    $scriptPath = "$workspace\40-arxiv-论文收集\lig\risk\lig-risk-monitor.py"
    
    if (Test-Path $scriptPath) {
        $action = New-ScheduledTaskAction -Execute "py.exe" -Argument "`"$scriptPath`""
        $trigger = New-ScheduledTaskTrigger -Daily -At 7am
        $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
        
        try {
            Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Force | Out-Null
            Write-Host "  + LIG Risk Monitor: $taskName (Daily 7:00 AM)" -ForegroundColor Green
        }
        catch {
            Write-Host "  - LIG Risk Monitor failed: $_" -ForegroundColor Red
        }
    }
    else {
        Write-Host "  ! LIG Risk Monitor script not found, skipping" -ForegroundColor Yellow
    }
}

function Get-TaskStatus {
    $taskNames = @("OpenClaw-Heartbeat", "OpenClaw-Domain-Ranking", "OpenClaw-Daily-Log", "LIG-Risk-Monitor")
    
    foreach ($taskName in $taskNames) {
        try {
            $task = Get-ScheduledTask -TaskName $taskName -ErrorAction Stop
            $state = $task.State
            $lastRun = $task.LastRunTime
            $nextRun = $task.NextRunTime
            
            $statusColor = if ($state -eq "Ready") { "Green" } else { "Yellow" }
            Write-Host "[$state] $taskName" -ForegroundColor $statusColor
            Write-Host "  Last Run: $lastRun" -ForegroundColor Gray
            Write-Host "  Next Run: $nextRun" -ForegroundColor Gray
            Write-Host ""
        }
        catch {
            Write-Host "[Not Installed] $taskName" -ForegroundColor Red
            Write-Host ""
        }
    }
}

function Remove-AllTasks {
    Write-Host "Removing all OpenClaw scheduled tasks..." -ForegroundColor Red
    
    $taskNames = @("OpenClaw-Heartbeat", "OpenClaw-Domain-Ranking", "OpenClaw-Daily-Log", "LIG-Risk-Monitor")
    
    foreach ($taskName in $taskNames) {
        try {
            Unregister-ScheduledTask -TaskName $taskName -Confirm:$false | Out-Null
            Write-Host "  - Removed: $taskName" -ForegroundColor Green
        }
        catch {
            Write-Host "  ! Not found: $taskName" -ForegroundColor Yellow
        }
    }
}

# Main logic
if ($Install) {
    Install-HeartbeatTask
    Install-DailyTasks
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Installation Complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
}
elseif ($Remove) {
    Remove-AllTasks
}
elseif ($Status) {
    Get-TaskStatus
}
elseif ($Heartbeat) {
    Install-HeartbeatTask
}
elseif ($Daily) {
    Install-DailyTasks
}
else {
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\heartbeat-scheduler.ps1 -Install   # Install all tasks"
    Write-Host "  .\heartbeat-scheduler.ps1 -Remove    # Remove all tasks"
    Write-Host "  .\heartbeat-scheduler.ps1 -Status    # Check task status"
    Write-Host "  .\heartbeat-scheduler.ps1 -Heartbeat # Install heartbeat only"
    Write-Host "  .\heartbeat-scheduler.ps1 -Daily     # Install daily tasks only"
    Write-Host ""
    Write-Host "Note: Administrator privileges required" -ForegroundColor Red
}
