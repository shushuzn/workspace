# Memory System Health Monitor - Windows Task Scheduler Setup
# Run this script as Administrator to create scheduled tasks

$taskName = "OpenClaw-MemoryHealth-Hourly"
$scriptPath = "D:\OpenClaw\workspace\30-scripts-tools\memory_health_monitor.py"
$pythonPath = "python"
$workingDir = "D:\OpenClaw\workspace"

# Create task trigger (hourly)
$trigger = New-ScheduledTaskTrigger -Hourly -At 0
$trigger.Repetition.Interval = "PT1H"

# Create task action
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "$scriptPath --check --report" -WorkingDirectory $workingDir

# Create task settings
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Register task
Register-ScheduledTask -TaskName $taskName -Trigger $trigger -Action $action -Settings $settings -Description "Memory system health check every hour"

Write-Host "Task created: $taskName"
Write-Host "Runs: Every hour"
Write-Host "Script: $scriptPath"
