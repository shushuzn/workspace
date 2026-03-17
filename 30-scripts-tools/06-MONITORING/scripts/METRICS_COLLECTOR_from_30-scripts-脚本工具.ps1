#!/usr/bin/env pwsh
# Metrics Collector - Auto collect metrics from tuning report
# Usage: .\METRICS_COLLECTOR.ps1 [-ReportPath "output/tuning_report.json"]

param(
    [string]$ReportPath = "output/tuning_report.json",
    [string]$OutputPath = "30-scripts/metrics_history.csv",
    [string]$LogPath = "30-scripts/metrics_collector.log",
    [switch]$Force,
    [int]$MaxRecords = 1000,
    [int]$MinFreeMB = 50,
    [switch]$NoCleanup,
    [switch]$ValidateOnly,
    [switch]$NoBackup,
    [int]$BackupRetention = 7,
    [int]$MaxRetries = 3,
    [long]$MaxLogSizeMB = 10,
    [int]$LogRetention = 5
)

$ErrorRecovery = @{
    BackupCreated = $false
    BackupFile = ""
    OriginalData = ""
    LockAcquired = $false
}

function Invoke-LogRotation {
    param(
        [string]$LogPath,
        [long]$MaxSizeMB,
        [int]$Retention
    )
    
    if (-not (Test-Path $LogPath)) {
        return
    }
    
    $LogFile = Get-Item $LogPath
    $MaxSizeBytes = $MaxSizeMB * 1MB
    $CurrentSize = $LogFile.Length
    
    Write-Log "Checking log rotation: ${CurrentSize} bytes / ${MaxSizeBytes} bytes" "INFO"
    
    if ($CurrentSize -gt $MaxSizeBytes) {
        Write-Log "Log file exceeds ${MaxSizeMB}MB, rotating..." "INFO"
        
        $Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $RotatedLog = Join-Path (Split-Path $LogPath -Parent) "metrics_collector_$Timestamp.log"
        
        try {
            # Move current log to rotated
            Move-Item $LogPath -Destination $RotatedLog -Force
            Write-Log "Log rotated to: $RotatedLog" "SUCCESS"
            
            # Create new empty log
            "" | Out-File -FilePath $LogPath -Encoding UTF8
            Write-Log "New log file created" "INFO"
            
            # Cleanup old logs
            $LogDir = Split-Path $LogPath -Parent
            $OldLogs = Get-ChildItem $LogDir -Filter "metrics_collector_*.log" | Sort-Object LastWriteTime -Descending
            
            if ($OldLogs.Count -gt $Retention) {
                $ToDelete = $OldLogs | Select-Object -Skip $Retention
                foreach ($OldLog in $ToDelete) {
                    Remove-Item $OldLog.FullName -Force
                    Write-Log "Old log removed: $($OldLog.Name)" "INFO"
                }
            }
        } catch {
            Write-Log "Log rotation failed: $($_.Exception.Message)" "ERROR"
        }
    } else {
        Write-Log "Log file size OK, no rotation needed" "INFO"
    }
}

$StartTime = Get-Date
$ScriptDir = Split-Path $MyInvocation.MyCommand.Path -Parent
$LogFile = Join-Path $ScriptDir (Split-Path $LogPath -Leaf)

# Performance & Memory tracking
$PerfMetrics = @{
    StartTime = $StartTime
    Steps = @{}
    StartMemory = [System.GC]::GetTotalMemory($false) / 1MB
}

function Start-PerfStep {
    param([string]$Name)
    $PerfMetrics.Steps[$Name] = @{
        Start = Get-Date
    }
}

function Stop-PerfStep {
    param([string]$Name)
    if ($PerfMetrics.Steps[$Name]) {
        $End = Get-Date
        $Duration = [math]::Round(($End - $PerfMetrics.Steps[$Name].Start).TotalMilliseconds, 2)
        $PerfMetrics.Steps[$Name].Duration = $Duration
        Write-Log "Step '$Name' completed in ${Duration}ms" "INFO"
    }
}

function Show-PerfSummary {
    $EndTime = Get-Date
    $EndMemory = [System.GC]::GetTotalMemory($false) / 1MB
    $TotalDuration = [math]::Round(($EndTime - $PerfMetrics.StartTime).TotalMilliseconds, 2)
    $MemoryUsed = [math]::Round($EndMemory - $PerfMetrics.StartMemory, 2)
    $PeakMemory = [math]::Round($EndMemory, 2)
    
    Write-Log "`n=== Performance Summary ===" "INFO"
    Write-Log "Total Duration: ${TotalDuration}ms" "INFO"
    Write-Log "Memory Used: ${MemoryUsed}MB" "INFO"
    Write-Log "Peak Memory: ${PeakMemory}MB" "INFO"
    
    foreach ($Step in $PerfMetrics.Steps.GetEnumerator()) {
        $Duration = $Step.Value.Duration
        Write-Log "  $($Step.Key): ${Duration}ms" "INFO"
    }
}

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"
    
    # Write to console
    switch ($Level) {
        "ERROR" { Write-Host $LogEntry -ForegroundColor Red }
        "WARNING" { Write-Host $LogEntry -ForegroundColor Yellow }
        "INFO" { Write-Host $LogEntry -ForegroundColor Gray }
        "SUCCESS" { Write-Host $LogEntry -ForegroundColor Green }
        default { Write-Host $LogEntry }
    }
    
    # Write to file
    $LogEntry | Out-File -FilePath $LogFile -Append -Encoding UTF8
}

function Test-Configuration {
    param(
        [string]$ReportPath,
        [string]$OutputPath,
        [int]$MaxRecords,
        [int]$MinFreeMB
    )
    
    $Valid = $true
    
    # Validate ReportPath
    if ([string]::IsNullOrWhiteSpace($ReportPath)) {
        Write-Host "ERROR: ReportPath cannot be empty" -ForegroundColor Red
        $Valid = $false
    } elseif (-not $ReportPath.EndsWith('.json')) {
        Write-Host "WARNING: ReportPath should end with .json" -ForegroundColor Yellow
    }
    
    # Validate OutputPath
    if ([string]::IsNullOrWhiteSpace($OutputPath)) {
        Write-Host "ERROR: OutputPath cannot be empty" -ForegroundColor Red
        $Valid = $false
    } elseif (-not $OutputPath.EndsWith('.csv')) {
        Write-Host "WARNING: OutputPath should end with .csv" -ForegroundColor Yellow
    }
    
    # Validate MaxRecords
    if ($MaxRecords -lt 10) {
        Write-Host "ERROR: MaxRecords must be >= 10" -ForegroundColor Red
        $Valid = $false
    } elseif ($MaxRecords -gt 100000) {
        Write-Host "WARNING: MaxRecords is very large ($MaxRecords)" -ForegroundColor Yellow
    }
    
    # Validate MinFreeMB
    if ($MinFreeMB -lt 10) {
        Write-Host "ERROR: MinFreeMB must be >= 10" -ForegroundColor Red
        $Valid = $false
    }
    
    return $Valid
}

$LockFile = "30-scripts/.metrics_collector.lock"
$LockTimeout = 300  # 5 minutes

function Test-Lock {
    param([string]$LockPath)
    
    if (Test-Path $LockPath) {
        $LockAge = (Get-Date) - (Get-Item $LockPath).LastWriteTime
        if ($LockAge.TotalSeconds -lt $LockTimeout) {
            return $false  # Lock is active
        } else {
            Remove-Item $LockPath -Force  # Lock expired
        }
    }
    return $true  # Can acquire lock
}

function Acquire-Lock {
    param([string]$LockPath)
    
    try {
        "Locked at $(Get-Date)" | Out-File -FilePath $LockPath -Encoding UTF8
        return $true
    } catch {
        return $false
    }
}

function Release-Lock {
    param([string]$LockPath)
    
    if (Test-Path $LockPath) {
        Remove-Item $LockPath -Force
        Write-Log "Lock released: $LockPath" "INFO"
    }
}

function Invoke-WithRetry {
    param(
        [scriptblock]$ScriptBlock,
        [string]$Operation,
        [int]$MaxRetries = 3
    )
    
    $Attempts = 0
    while ($Attempts -lt $MaxRetries) {
        try {
            & $ScriptBlock
            return $true
        } catch {
            $Attempts++
            Write-Log "Retry $Attempts/$MaxRetries for '$Operation': $($_.Exception.Message)" "WARNING"
            if ($Attempts -ge $MaxRetries) {
                Write-Log "Operation '$Operation' failed after $MaxRetries attempts" "ERROR"
                return $false
            }
            Start-Sleep -Milliseconds (100 * $Attempts)
        }
    }
}

function Invoke-Rollback {
    Write-Log "`n=== Invoking Rollback ===" "WARNING"
    
    # Restore backup if exists
    if ($ErrorRecovery.BackupCreated -and $ErrorRecovery.BackupFile -and (Test-Path $ErrorRecovery.BackupFile)) {
        try {
            Copy-Item $ErrorRecovery.BackupFile -Destination $OutputPath -Force
            Write-Log "Restored from backup: $ErrorRecovery.BackupFile" "SUCCESS"
        } catch {
            Write-Log "Failed to restore backup: $($_.Exception.Message)" "ERROR"
        }
    }
    
    # Release lock if held
    if ($ErrorRecovery.LockAcquired) {
        Release-Lock $LockFile
    }
    
    Write-Log "Rollback completed" "INFO"
}

# Log rotation check
Invoke-LogRotation -LogPath $LogFile -MaxSizeMB $MaxLogSizeMB -LogRetention $LogRetention

# Main execution with error recovery
try {
    Write-Log "=== Metrics Collector Started ===" "INFO"
    Write-Log "ReportPath: $ReportPath" "INFO"
    Write-Log "OutputPath: $OutputPath" "INFO"
    Write-Log "MaxRecords: $MaxRecords" "INFO"
    Write-Log "MaxLogSize: ${MaxLogSizeMB}MB" "INFO"
    Write-Log "LogRetention: $LogRetention files" "INFO"

# Validate configuration
Start-PerfStep "Validation"
Write-Log "Validating configuration..." "INFO"
if (-not (Test-Configuration -ReportPath $ReportPath -OutputPath $OutputPath -MaxRecords $MaxRecords -MinFreeMB $MinFreeMB)) {
    Write-Log "Configuration validation FAILED" "ERROR"
    Show-PerfSummary
    exit 1
}
Write-Log "Configuration OK" "SUCCESS"
Stop-PerfStep "Validation"

# ValidateOnly mode
if ($ValidateOnly) {
    Write-Host "Validation only mode - exiting" -ForegroundColor Green
    exit 0
}

# Acquire lock
Start-PerfStep "LockAcquisition"
if (-not $Force) {
    if (-not (Test-Lock $LockFile)) {
        Write-Log "ERROR: Another instance is running" "ERROR"
        Show-PerfSummary
        exit 1
    }
    
    $LockResult = Invoke-WithRetry -ScriptBlock { Acquire-Lock $LockFile } -Operation "LockAcquisition" -MaxRetries $MaxRetries
    if (-not $LockResult) {
        Write-Log "ERROR: Cannot acquire lock after $MaxRetries retries" "ERROR"
        Show-PerfSummary
        exit 1
    }
    $ErrorRecovery.LockAcquired = $true
}
Write-Log "Lock acquired: $LockFile" "SUCCESS"
Stop-PerfStep "LockAcquisition"

# Auto-create directories with permission check
$ReportDir = Split-Path $ReportPath -Parent
$OutputDir = Split-Path $OutputPath -Parent

function Test-DirectoryPermission {
    param([string]$Path)
    try {
        $TestFile = Join-Path $Path "test_permission_$([System.Guid]::NewGuid()).tmp"
        "" | Out-File -FilePath $TestFile -Force -ErrorAction Stop
        Remove-Item $TestFile -Force
        return $true
    } catch {
        return $false
    }
}

function Test-DiskSpace {
    param([string]$Path, [long]$MinFreeMB = 100)
    try {
        # Get full path
        if ([System.IO.Path]::IsPathRooted($Path)) {
            $FullPath = $Path
        } else {
            $FullPath = Join-Path (Get-Location) $Path
        }
        
        # Get drive letter
        $DriveLetter = $FullPath[0]
        $Drive = Get-PSDrive -Name $DriveLetter -PSProvider FileSystem -ErrorAction Stop
        $FreeMB = [math]::Round($Drive.Free / 1MB, 2)
        
        if ($FreeMB -lt $MinFreeMB) {
            Write-Host "WARNING: Low disk space on ${DriveLetter}: - Free: ${FreeMB}MB" -ForegroundColor Yellow
            return $false
        }
        
        Write-Host "Disk OK: ${DriveLetter}: - Free: ${FreeMB}MB" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "Disk check skipped" -ForegroundColor Gray
        return $true
    }
}

if ($ReportDir) {
    if (-not (Test-Path $ReportDir)) {
        try {
            New-Item -ItemType Directory -Path $ReportDir -Force | Out-Null
            Write-Log "Created directory: $ReportDir" "SUCCESS"
        } catch {
            Write-Host "FAIL: Cannot create directory: $ReportDir" -ForegroundColor Red
            Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
            exit 1
        }
    }
    
    if (-not (Test-DirectoryPermission $ReportDir)) {
        Write-Host "FAIL: No write permission: $ReportDir" -ForegroundColor Red
        exit 1
    }
    
    # Check disk space
    if (-not (Test-DiskSpace $ReportDir -MinFreeMB 50)) {
        Write-Host "WARNING: Insufficient disk space for report directory" -ForegroundColor Yellow
    }
}

if ($OutputDir) {
    if (-not (Test-Path $OutputDir)) {
        try {
            New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
            Write-Log "Created directory: $OutputDir" "SUCCESS"
        } catch {
            Write-Host "FAIL: Cannot create directory: $OutputDir" -ForegroundColor Red
            Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
            exit 1
        }
    }
    
    if (-not (Test-DirectoryPermission $OutputDir)) {
        Write-Host "FAIL: No write permission: $OutputDir" -ForegroundColor Red
        exit 1
    }
    
    # Check disk space
    if (-not (Test-DiskSpace $OutputDir -MinFreeMB 50)) {
        Write-Host "WARNING: Insufficient disk space for output directory" -ForegroundColor Yellow
    }
}

# Check report file
if (-not (Test-Path $ReportPath)) {
    Write-Host "Report not found, creating mock data..." -ForegroundColor Yellow
    
    $MockData = @{
        top1 = @{
            score = @{
                V_total = 0.65
                components = @{
                    growth_momentum = 0.6
                    return_quality = 0.7
                    upgrade_satisfaction = 0.65
                    progress_clarity = 0.6
                    stability_score = 0.7
                }
                fail_rate = 0.02
                bottleneck = @{
                    longest_stall_median_seconds = 300
                }
                constraint_failed = 0
            }
        }
    }
    
    $MockData | ConvertTo-Json -Depth 10 | Out-File -FilePath $ReportPath -Encoding UTF8
    Write-Log "Mock data created: $ReportPath" "SUCCESS"
}

# Read report
Start-PerfStep "ReadReport"
$Report = Get-Content $ReportPath -Raw | ConvertFrom-Json
Stop-PerfStep "ReadReport"

# Extract metrics
$NorthStar = [math]::Round($Report.top1.score.V_total * 100, 1)
$GrowthMomentum = [math]::Round($Report.top1.score.components.growth_momentum * 100, 1)
$ReturnQuality = [math]::Round($Report.top1.score.components.return_quality * 100, 1)
$UpgradeSatisfaction = [math]::Round($Report.top1.score.components.upgrade_satisfaction * 100, 1)
$ProgressClarity = [math]::Round($Report.top1.score.components.progress_clarity * 100, 1)
$StabilityScore = [math]::Round($Report.top1.score.components.stability_score * 100, 1)
$FailRate = [math]::Round($Report.top1.score.fail_rate * 100, 2)
$StallSeconds = $Report.top1.score.bottleneck.longest_stall_median_seconds
$ConstraintFailed = $Report.top1.score.constraint_failed

# Calculate risk level
$RiskLevel = "Low"
if ($FailRate -gt 1 -or $StallSeconds -gt 1200) { $RiskLevel = "Medium" }
if ($NorthStar -lt 50 -or $ConstraintFailed -gt 0) { $RiskLevel = "High" }

# Determine mode
$Mode = "Optimization"
if ($NorthStar -lt 50) { $Mode = "Acceleration" }
elseif ($NorthStar -ge 85 -or $RiskLevel -eq "High") { $Mode = "Hardening" }

# Display results
Write-Log "North Star: $NorthStar%" "INFO"
Write-Log "Risk Level: $RiskLevel" "INFO"
Write-Log "Current Mode: $Mode" "INFO"

# Save to CSV
$Metrics = [PSCustomObject]@{
    Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    NorthStar = $NorthStar
    GrowthMomentum = $GrowthMomentum
    ReturnQuality = $ReturnQuality
    UpgradeSatisfaction = $UpgradeSatisfaction
    ProgressClarity = $ProgressClarity
    StabilityScore = $StabilityScore
    FailRate = $FailRate
    StallSeconds = $StallSeconds
    ConstraintFailed = $ConstraintFailed
    RiskLevel = $RiskLevel
    Mode = $Mode
}

if (Test-Path $OutputPath) {
    $Metrics | Export-Csv -Path $OutputPath -Append -NoTypeInformation -Encoding UTF8
} else {
    $Metrics | Export-Csv -Path $OutputPath -NoTypeInformation -Encoding UTF8
}

Write-Log "Saved to: $OutputPath" "SUCCESS"

# Backup before cleanup
if (-not $NoCleanup -and -not $NoBackup) {
    Start-PerfStep "Backup"
    $BackupDir = Join-Path $ScriptDir "backups"
    if (-not (Test-Path $BackupDir)) {
        New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
    }
    
    if (Test-Path $OutputPath) {
        $Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $BackupFile = Join-Path $BackupDir "metrics_history_$Timestamp.csv"
        
        $BackupResult = Invoke-WithRetry -ScriptBlock {
            Copy-Item $OutputPath -Destination $BackupFile -Force
        } -Operation "Backup" -MaxRetries $MaxRetries
        
        if ($BackupResult) {
            $ErrorRecovery.BackupCreated = $true
            $ErrorRecovery.BackupFile = $BackupFile
            Write-Log "Backup created: $BackupFile" "SUCCESS"
        } else {
            Write-Log "WARNING: Backup failed, continuing without backup" "WARNING"
        }
        
        # Cleanup old backups
        $Backups = Get-ChildItem $BackupDir -Filter "metrics_history_*.csv" | Sort-Object LastWriteTime -Descending
        if ($Backups.Count -gt $BackupRetention) {
            $OldBackups = $Backups | Select-Object -Skip $BackupRetention
            foreach ($OldBackup in $OldBackups) {
                Remove-Item $OldBackup.FullName -Force
                Write-Log "Old backup removed: $($OldBackup.Name)" "INFO"
            }
        }
    }
    Stop-PerfStep "Backup"
}

# Cleanup old records
if (-not $NoCleanup) {
    Start-PerfStep "Cleanup"
    Write-Log "Cleaning up old records (Max: $MaxRecords)..." "INFO"
    
    if (Test-Path $OutputPath) {
        $AllRecords = Import-Csv $OutputPath
        $RecordCount = $AllRecords.Count
        
        if ($RecordCount -gt $MaxRecords) {
            $KeepRecords = $AllRecords | Select-Object -Last $MaxRecords
            $KeepRecords | Export-Csv $OutputPath -NoTypeInformation -Encoding UTF8
            $RemovedCount = $RecordCount - $MaxRecords
            Write-Log "Cleaned up $RemovedCount old records" "SUCCESS"
Stop-PerfStep "Cleanup"
        } else {
            Write-Log "No cleanup needed ($RecordCount records)" "INFO"
Stop-PerfStep "Cleanup"
        }
    }
}

Show-PerfSummary
Write-Log "=== Metrics Collector Completed ===" "SUCCESS"

} catch {
    Write-Log "`n=== ERROR DETECTED ===" "ERROR"
    Write-Log "Error: $($_.Exception.Message)" "ERROR"
    Write-Log "StackTrace: $($_.Exception.StackTrace)" "ERROR"
    
    Invoke-Rollback
    
    Show-PerfSummary
    exit 1
} finally {
    # Always release lock
    if ($ErrorRecovery.LockAcquired) {
        Release-Lock $LockFile
    }
}

return $Metrics
