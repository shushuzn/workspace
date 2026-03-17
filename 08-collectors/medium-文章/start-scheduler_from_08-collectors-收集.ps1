# Medium Watcher 定时任务调度器 v2.9
# 单进程 + 等待时段资料整理蒸馏

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$collectorScript = "D:\obsidian\Vault\Medium\medium-watcher-auto.py"
$roadmapScript = "D:\obsidian\Vault\Medium\update-roadmap.py"
$organizeScript = "D:\obsidian\Vault\Medium\organize-notes.py"
$logPath = "D:\obsidian\Vault\Medium\scheduler-log.md"
$perfLogPath = "D:\obsidian\Vault\Medium\performance-log.md"

# 搜集间隔配置（分钟）
$INTERVALS = @{
    medium = 120     # Medium: 每 2 小时
    arxiv = 120      # arXiv: 每 2 小时
    github = 120     # GitHub: 每 2 小时
    roadmap = 1440   # 路线图：每 24 小时
}

# 性能保护配置
$PERF_CONFIG = @{
    max_cpu_percent = 30
    max_memory_mb = 500
    min_battery_percent = 20
    pause_hours = @(2,3,4,5)
    max_daily_runs = 15
}

# 追踪
$lastRuns = @{
    medium = $null
    arxiv = $null
    github = $null
    roadmap = $null
    organize = $null   # 整理任务
}
$todayRuns = 0
$today = (Get-Date).Date

function Write-SchedulerLog {
    param($msg, $level = "info")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $icon = switch ($level) {
        "error" { "[!]" }
        "success" { "[OK]" }
        "info" { "[i]" }
        "perf" { "[PERF]" }
        "pause" { "[PAUSE]" }
        "organize" { "[ORG]" }
        default { "[-]" }
    }
    $entry = "- [$timestamp] $icon $msg`n"
    
    if (-not (Test-Path $logPath)) {
        $header = @"
# Medium Watcher 调度器日志 v2.9 (单进程 + 资料整理)

## 运行状态

- 状态：运行中
- 启动时间：$(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
- 执行模式：**单进程顺序执行 + 等待时段整理**
- Medium 间隔：2 小时
- arXiv 间隔：2 小时
- GitHub 间隔：2 小时
- 路线图更新：24 小时
- 资料整理：等待时段自动执行

## 性能配置

- 最大 CPU: $($PERF_CONFIG.max_cpu_percent)%
- 最大内存：$($PERF_CONFIG.max_memory_mb)MB
- 最低电池：$($PERF_CONFIG.min_battery_percent)%
- 暂停时段：$($PERF_CONFIG.pause_hours -join ",") 点
- 每日最多：$($PERF_CONFIG.max_daily_runs) 次

---

## 运行记录

"@
        Set-Content -Path $logPath -Value $header -Encoding UTF8
    }
    
    Add-Content -Path $logPath -Value $entry -Encoding UTF8
}

function Get-SystemPerf {
    $cpu = Get-Counter '\Processor(_Total)\% Processor Time' -ErrorAction SilentlyContinue
    $cpuPercent = [math]::Round($cpu.CounterSamples.CookedValue, 1)
    
    $os = Get-CimInstance Win32_OperatingSystem
    $memoryUsed = [math]::Round(($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / 1MB, 1)
    
    $battery = Get-CimInstance Win32_Battery -ErrorAction SilentlyContinue
    $batteryPercent = if ($battery) { $battery.EstimatedChargeRemaining } else { 100 }
    $onBattery = if ($battery) { -not $battery.PowerOnline } else { $false }
    
    return @{
        cpu = $cpuPercent
        memory = $memoryUsed
        battery = $batteryPercent
        onBattery = $onBattery
    }
}

function Test-ShouldRun {
    if ((Get-Date).Date -gt $today) {
        $script:today = (Get-Date).Date
        $script:todayRuns = 0
    }
    
    if ($todayRuns -ge $PERF_CONFIG.max_daily_runs) {
        Write-SchedulerLog "已达每日运行上限 ($todayRuns/$($PERF_CONFIG.max_daily_runs))" "pause"
        return $false
    }
    
    $hour = (Get-Date).Hour
    if ($PERF_CONFIG.pause_hours -contains $hour) {
        Write-SchedulerLog "暂停时段 ($hour:00)，跳过运行" "pause"
        return $false
    }
    
    $perf = Get-SystemPerf
    
    if ($perf.cpu -gt $PERF_CONFIG.max_cpu_percent) {
        Write-SchedulerLog "CPU 使用率高 ($($perf.cpu)%)，暂停运行" "perf"
        return $false
    }
    
    if ($perf.memory -gt $PERF_CONFIG.max_memory_mb) {
        Write-SchedulerLog "内存使用高 ($($perf.memory)MB)，暂停运行" "perf"
        return $false
    }
    
    if ($perf.onBattery -and $perf.battery -lt $PERF_CONFIG.min_battery_percent) {
        Write-SchedulerLog "电池电量低 ($($perf.battery)%)，暂停运行" "perf"
        return $false
    }
    
    return $true
}

function Run-All-Sources {
    if (-not (Test-ShouldRun)) {
        return
    }
    
    $sourcesToRun = @()
    
    if ($null -eq $lastRuns["medium"] -or ((Get-Date) - $lastRuns["medium"]).TotalMinutes -ge $INTERVALS["medium"]) {
        $sourcesToRun += "medium"
    }
    if ($null -eq $lastRuns["arxiv"] -or ((Get-Date) - $lastRuns["arxiv"]).TotalMinutes -ge $INTERVALS["arxiv"]) {
        $sourcesToRun += "arxiv"
    }
    if ($null -eq $lastRuns["github"] -or ((Get-Date) - $lastRuns["github"]).TotalMinutes -ge $INTERVALS["github"]) {
        $sourcesToRun += "github"
    }
    
    if ($sourcesToRun.Count -eq 0) {
        return
    }
    
    Write-SchedulerLog "开始执行搜集任务 (源：$($sourcesToRun -join ', '))" "info"
    $startTime = Get-Date
    
    foreach ($source in $sourcesToRun) {
        Write-SchedulerLog "执行 $source 搜集" $source
        
        try {
            $env:MW_SOURCE = $source
            $psi = New-Object System.Diagnostics.ProcessStartInfo
            $psi.FileName = "python"
            $psi.Arguments = $collectorScript
            $psi.WorkingDirectory = "D:\obsidian\Vault\Medium"
            $psi.RedirectStandardOutput = $true
            $psi.RedirectStandardError = $true
            $psi.UseShellExecute = $false
            $psi.StandardOutputEncoding = [System.Text.Encoding]::UTF8
            $psi.StandardErrorEncoding = [System.Text.Encoding]::UTF8
            
            $process = [System.Diagnostics.Process]::Start($psi)
            $output = $process.StandardOutput.ReadToEnd()
            $error = $process.StandardError.ReadToEnd()
            $process.WaitForExit()
            
            if ($output) {
                Write-SchedulerLog "$source : $output" "success"
            }
            if ($error) {
                Write-SchedulerLog "$source 错误：$error" "error"
            }
        } catch {
            Write-SchedulerLog "$source 异常：$_" "error"
        }
    }
    
    $duration = [math]::Round(((Get-Date) - $startTime).TotalSeconds, 1)
    $script:todayRuns++
    
    foreach ($source in $sourcesToRun) {
        $lastRuns[$source] = Get-Date
    }
    
    $perf = Get-SystemPerf
    $perfEntry = "- [$([Get-Date]::Now.ToString("yyyy-MM-dd HH:mm:ss"))] 批量执行 ($($sourcesToRun.Count)源) : CPU $($perf.cpu)% | Mem $($perf.memory)MB | ${duration}s`n"
    Add-Content -Path $perfLogPath -Value $perfEntry -Encoding UTF8 -ErrorAction SilentlyContinue
    
    Write-SchedulerLog "搜集任务完成 (总耗时：${duration}s, 今日运行：$todayRuns/$($PERF_CONFIG.max_daily_runs))" "success"
}

function Run-Organize {
    """在等待时段执行资料整理蒸馏"""
    
    $perf = Get-SystemPerf
    
    # 检查系统负载，负载高时跳过
    if ($perf.cpu -gt 20 -or $perf.memory -gt 400) {
        return
    }
    
    Write-SchedulerLog "执行资料整理蒸馏" "organize"
    $startTime = Get-Date
    
    try {
        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName = "python"
        $psi.Arguments = $organizeScript
        $psi.WorkingDirectory = "D:\obsidian\Vault\Medium"
        $psi.RedirectStandardOutput = $true
        $psi.RedirectStandardError = $true
        $psi.UseShellExecute = $false
        $psi.StandardOutputEncoding = [System.Text.Encoding]::UTF8
        $psi.StandardErrorEncoding = [System.Text.Encoding]::UTF8
        
        $process = [System.Diagnostics.Process]::Start($psi)
        $output = $process.StandardOutput.ReadToEnd()
        $error = $process.StandardError.ReadToEnd()
        $process.WaitForExit()
        
        if ($output) {
            Write-SchedulerLog "整理：$output" "success"
        }
        if ($error) {
            Write-SchedulerLog "整理错误：$error" "error"
        }
        
        $duration = [math]::Round(((Get-Date) - $startTime).TotalSeconds, 1)
        $lastRuns["organize"] = Get-Date
        
        $perf = Get-SystemPerf
        $perfEntry = "- [$([Get-Date]::Now.ToString("yyyy-MM-dd HH:mm:ss"))] 资料整理 : CPU $($perf.cpu)% | Mem $($perf.memory)MB | ${duration}s`n"
        Add-Content -Path $perfLogPath -Value $perfEntry -Encoding UTF8 -ErrorAction SilentlyContinue
    } catch {
        Write-SchedulerLog "整理异常：$_" "error"
    }
}

# 初始化性能日志
if (-not (Test-Path $perfLogPath)) {
    @"
# Medium Watcher 性能日志 v2.9

## 配置

- 执行模式：单进程顺序执行 + 等待时段整理
- 最大 CPU: $($PERF_CONFIG.max_cpu_percent)%
- 最大内存：$($PERF_CONFIG.max_memory_mb)MB
- 最低电池：$($PERF_CONFIG.min_battery_percent)%
- 每日最多：$($PERF_CONFIG.max_daily_runs) 次

---

## 运行记录

格式：时间 | 执行类型 | CPU% | 内存 MB | 耗时 s

"@ | Out-File -FilePath $perfLogPath -Encoding UTF8
}

Write-SchedulerLog "调度器 v2.9 启动 (单进程 + 资料整理)" "success"
Write-SchedulerLog "Medium: 每 $($INTERVALS.medium/60) 小时" "info"
Write-SchedulerLog "arXiv: 每 $($INTERVALS.arxiv/60) 小时" "info"
Write-SchedulerLog "GitHub: 每 $($INTERVALS.github/60) 小时" "info"
Write-SchedulerLog "路线图：每 $($INTERVALS.roadmap/1440) 天" "info"
Write-SchedulerLog "资料整理：等待时段自动执行" "organize"
Write-SchedulerLog "性能保护：启用" "perf"

# 初始等待
Start-Sleep -Seconds 30

$loopCount = 0
while ($true) {
    $loopCount++
    
    # 每 24 小时执行路线图更新
    if ($null -eq $lastRuns["roadmap"] -or ((Get-Date) - $lastRuns["roadmap"]).TotalMinutes -ge $INTERVALS["roadmap"]) {
        Write-SchedulerLog "执行路线图更新 (24 小时)" "info"
        try {
            $psi = New-Object System.Diagnostics.ProcessStartInfo
            $psi.FileName = "python"
            $psi.Arguments = $roadmapScript
            $psi.WorkingDirectory = "D:\obsidian\Vault\Medium"
            $psi.RedirectStandardOutput = $true
            $psi.UseShellExecute = $false
            $psi.StandardOutputEncoding = [System.Text.Encoding]::UTF8
            
            $process = [System.Diagnostics.Process]::Start($psi)
            $output = $process.StandardOutput.ReadToEnd()
            $process.WaitForExit()
            
            if ($output) {
                Write-SchedulerLog "路线图：$output" "success"
            }
            $lastRuns["roadmap"] = Get-Date
        } catch {
            Write-SchedulerLog "路线图异常：$_" "error"
        }
    }
    
    # 单进程顺序执行所有到期的源
    Run-All-Sources
    
    # 在等待时段执行资料整理 (每 30 分钟检查一次)
    if ($null -eq $lastRuns["organize"] -or ((Get-Date) - $lastRuns["organize"]).TotalMinutes -ge 30) {
        Run-Organize
    }
    
    # 每 10 分钟检查一次
    Write-SchedulerLog "等待 10 分钟... (Loop $loopCount)" "info"
    Start-Sleep -Minutes 10
}
