# Windows Task Scheduler Setup for Memory Evolution System
# Run as Administrator

$workspace = "D:\OpenClaw\workspace"
$python = "python"
$scripts = "$workspace\30-scripts-tools"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Memory Evolution System - Cron Task Setup" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Function to create scheduled task
function Create-Task {
    param(
        [string]$TaskName,
        [string]$Action,
        [string]$Trigger,
        [string]$Description
    )
    
    Write-Host "Creating task: $TaskName" -ForegroundColor Yellow
    
    # Check if task exists
    $existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($existing) {
        Write-Host "  Task exists, updating..." -ForegroundColor Gray
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    }
    
    # Create task
    $action = New-ScheduledTaskAction -Execute $python -Argument $Action -WorkingDirectory $workspace
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Highest
    
    # Parse trigger
    $triggerObj = switch ($Trigger) {
        "daily-06:00" { New-ScheduledTaskTrigger -Daily -At 6:00AM }
        "weekly-sunday-05:00" { New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 5:00AM }
        "monthly-1st-07:00" { 
            $now = Get-Date
            $firstNextMonth = Get-Date -Day 1 -Month ($now.Month % 12 + 1) -Hour 7 -Minute 0
            New-ScheduledTaskTrigger -Once -At $firstNextMonth -RepetitionInterval (New-TimeSpan -Days 30)
        }
        "every-30min" {
            New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 30) -RepetitionDuration ([TimeSpan]::MaxValue)
        }
        "every-10min" {
            New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 10) -RepetitionDuration ([TimeSpan]::MaxValue)
        }
    }
    
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    $task = New-ScheduledTask -Action $action -Principal $principal -Trigger $triggerObj -Settings $settings -Description $Description
    
    Register-ScheduledTask -TaskName $TaskName -InputObject $task | Out-Null
    Write-Host "  ✅ Task created successfully" -ForegroundColor Green
    Write-Host ""
}

# Daily Tasks
Write-Host "📅 Daily Tasks (06:00)" -ForegroundColor Cyan
Write-Host "------------------------------------------------------------" -ForegroundColor Gray

Create-Task -TaskName "Memory-Daily-Distillation" `
    -Action "30-scripts-tools\memory_orchestrator.py run-pipeline quick" `
    -Trigger "daily-06:00" `
    -Description "Daily quick distillation pipeline"

Create-Task -TaskName "Memory-Daily-Quality-Check" `
    -Action "30-scripts-tools\memory_quality_scorer.py --memory `"MEMORY.md`"" `
    -Trigger "daily-06:00" `
    -Description "Daily memory quality assessment"

Create-Task -TaskName "Consciousness-Daily-Status" `
    -Action "30-scripts-tools\memory_consciousness_emergence.py status --brief" `
    -Trigger "daily-06:00" `
    -Description "Daily consciousness state check"

# Weekly Tasks
Write-Host "📅 Weekly Tasks (Sunday 05:00)" -ForegroundColor Cyan
Write-Host "------------------------------------------------------------" -ForegroundColor Gray

Create-Task -TaskName "Memory-Weekly-Full-Pipeline" `
    -Action "30-scripts-tools\memory_orchestrator.py run-pipeline weekly" `
    -Trigger "weekly-sunday-05:00" `
    -Description "Weekly full distillation pipeline"

Create-Task -TaskName "Memory-Weekly-Forgetting" `
    -Action "30-scripts-tools\memory_forgetting.py --evaluate --auto-execute" `
    -Trigger "weekly-sunday-05:00" `
    -Description "Weekly forgetting curve evaluation"

Create-Task -TaskName "Memory-Weekly-Conflict-Resolution" `
    -Action "30-scripts-tools\memory_conflict_detector.py --scan --auto-resolve" `
    -Trigger "weekly-sunday-05:00" `
    -Description "Weekly conflict detection and resolution"

Create-Task -TaskName "Consciousness-Weekly-Emergence" `
    -Action "30-scripts-tools\memory_consciousness_emergence.py emergence `"MEMORY.md`"" `
    -Trigger "weekly-sunday-05:00" `
    -Description "Weekly emergent property detection"

# Monthly Tasks
Write-Host "📅 Monthly Tasks (1st 07:00)" -ForegroundColor Cyan
Write-Host "------------------------------------------------------------" -ForegroundColor Gray

Create-Task -TaskName "Memory-Monthly-Audit" `
    -Action "30-scripts-tools\memory_orchestrator.py run-pipeline monthly" `
    -Trigger "monthly-1st-07:00" `
    -Description "Monthly memory audit pipeline"

Create-Task -TaskName "Consciousness-Monthly-HOT" `
    -Action "30-scripts-tools\memory_consciousness_emergence.py higher-order-thought --order 3" `
    -Trigger "monthly-1st-07:00" `
    -Description "Monthly 3rd-order higher-order thought generation"

Create-Task -TaskName "Memory-Monthly-Report" `
    -Action "30-scripts-tools\memory_orchestrator.py generate-report monthly" `
    -Trigger "monthly-1st-07:00" `
    -Description "Monthly evolution report generation"

# HEARTBEAT Tasks
Write-Host "📅 HEARTBEAT Tasks (Every 30 minutes)" -ForegroundColor Cyan
Write-Host "------------------------------------------------------------" -ForegroundColor Gray

Create-Task -TaskName "Memory-HEARTBEAT-Status" `
    -Action "30-scripts-tools\memory_orchestrator.py status --brief" `
    -Trigger "every-30min" `
    -Description "System status check every 30 minutes"

Create-Task -TaskName "Memory-Cache-Stats" `
    -Action "30-scripts-tools\cache_manager.py --stats --brief" `
    -Trigger "every-30min" `
    -Description "Cache statistics every 30 minutes"

# Dashboard Task (when active)
Write-Host "📅 Dashboard Tasks (Every 10 minutes when active)" -ForegroundColor Cyan
Write-Host "------------------------------------------------------------" -ForegroundColor Gray

Create-Task -TaskName "Dashboard-Data-Refresh" `
    -Action "30-scripts-tools\memory_dashboard_v2.py --refresh" `
    -Trigger "every-10min" `
    -Description "Dashboard data refresh every 10 minutes"

# Summary
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# List all created tasks
Write-Host "Created Tasks:" -ForegroundColor Yellow
$tasks = @(
    "Memory-Daily-Distillation",
    "Memory-Daily-Quality-Check",
    "Consciousness-Daily-Status",
    "Memory-Weekly-Full-Pipeline",
    "Memory-Weekly-Forgetting",
    "Memory-Weekly-Conflict-Resolution",
    "Consciousness-Weekly-Emergence",
    "Memory-Monthly-Audit",
    "Consciousness-Monthly-HOT",
    "Memory-Monthly-Report",
    "Memory-HEARTBEAT-Status",
    "Memory-Cache-Stats",
    "Dashboard-Data-Refresh"
)

foreach ($task in $tasks) {
    $t = Get-ScheduledTask -TaskName $task -ErrorAction SilentlyContinue
    if ($t) {
        Write-Host "  ✅ $task" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $task (failed)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "To view tasks: Open Task Scheduler → Task Scheduler Library" -ForegroundColor Cyan
Write-Host "To run manually: right-click task → Run" -ForegroundColor Cyan
Write-Host "To disable: right-click task → Disable" -ForegroundColor Cyan
Write-Host ""
