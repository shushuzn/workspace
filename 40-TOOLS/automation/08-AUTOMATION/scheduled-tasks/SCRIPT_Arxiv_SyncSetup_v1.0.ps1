# arxiv-sync-setup.ps1
# Obsidian Sync 目录自动化脚本
# 功能：创建标准化的论文同步目录结构

param(
    [string]$VaultPath = "D:\obsidian\Vault",
    [string]$SyncRoot = "arxiv",
    [switch]$Init,           # 初始化完整结构
    [switch]$CreateDaily,    # 创建今日目录
    [string]$Date,           # 指定日期 (YYYY-MM-DD)，默认为今天
    [switch]$CreateWeekly,   # 创建周汇总
    [switch]$CreateMonthly,  # 创建月汇总
    [switch]$DryRun          # 预览不执行
)

$ErrorActionPreference = "Stop"

# ==================== 配置 ====================

$Domains = @(
    "csAI",      # 人工智能
    "csLG",      # 机器学习
    "csCV",      # 计算机视觉
    "csCL",      # 计算语言学
    "csIR",      # 信息检索
    "csSE",      # 软件工程
    "csDC",      # 分布式计算
    "csAR",      # 架构/硬件
    "csCR",      # 密码学
    "csGT",      # 博弈论
    "csMM",      # 多媒体
    "csNI",      # 网络
    "csOS",      # 操作系统
    "csPL",      # 编程语言
    "csRO",      # 机器人
    "csSY",      # 系统
    "cross"      # 交叉领域
)

$LogTypes = @(
    "cron",      # 定时任务日志
    "status",    # 同步状态
    "update",    # 更新日志
    "errors"     # 错误日志
)

# ==================== 工具函数 ====================

function Get-ISODate {
    param([string]$InputDate)
    if ($InputDate) {
        return $InputDate
    }
    return Get-Date -Format "yyyy-MM-dd"
}

function Get-WeekNumber {
    param([string]$InputDate)
    $date = if ($InputDate) { [datetime]$InputDate } else { Get-Date }
    $culture = [cultureinfo]::InvariantCulture
    return $culture.Calendar.GetWeekOfYear($date, [System.Globalization.CalendarWeekRule]::FirstDay, [DayOfWeek]::Monday)
}

function Get-MonthYear {
    param([string]$InputDate)
    $date = if ($InputDate) { [datetime]$InputDate } else { Get-Date }
    return $date.ToString("yyyy-MM")
}

function New-DirectorySafe {
    param([string]$Path)
    if ($DryRun) {
        Write-Host "[DRY RUN] Would create: $Path" -ForegroundColor Yellow
        return
    }
    if (!(Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
        Write-Host "✓ Created: $Path" -ForegroundColor Green
    } else {
        Write-Host "○ Exists: $Path" -ForegroundColor Gray
    }
}

function New-TemplateFile {
    param(
        [string]$Path,
        [string]$Title,
        [string]$Content
    )
    if ($DryRun) {
        Write-Host "[DRY RUN] Would create: $Path" -ForegroundColor Yellow
        return
    }
    if (!(Test-Path $Path)) {
        $fullContent = "---`ncreated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`ntags: [arxiv, template]`n---`n`n# $Title`n`n$Content"
        Set-Content -Path $Path -Value $fullContent -Encoding UTF8
        Write-Host "✓ Created: $Path" -ForegroundColor Green
    } else {
        Write-Host "○ Exists: $Path" -ForegroundColor Gray
    }
}

# ==================== 核心功能 ====================

function Initialize-FullStructure {
    Write-Host "`n=== 初始化完整目录结构 ===" -ForegroundColor Cyan
    
    $basePath = Join-Path $VaultPath $SyncRoot
    
    # 创建基础目录
    New-DirectorySafe -Path $basePath
    New-DirectorySafe -Path (Join-Path $basePath "daily")
    New-DirectorySafe -Path (Join-Path $basePath "weekly")
    New-DirectorySafe -Path (Join-Path $basePath "monthly")
    New-DirectorySafe -Path (Join-Path $basePath "archive")
    
    # 创建领域模板目录
    $domainsPath = Join-Path $basePath "domains"
    New-DirectorySafe -Path $domainsPath
    foreach ($domain in $Domains) {
        New-DirectorySafe -Path (Join-Path $domainsPath $domain)
    }
    
    Write-Host "`n✓ 完整结构初始化完成" -ForegroundColor Green
}

function Create-DailyStructure {
    param([string]$InputDate)
    
    $date = Get-ISODate -InputDate $InputDate
    Write-Host "`n=== 创建 $date 每日目录 ===" -ForegroundColor Cyan
    
    $datePath = Join-Path $VaultPath $SyncRoot "daily" $date.Substring(0,4) $date.Substring(5,2) $date
    
    # 创建日期目录
    New-DirectorySafe -Path $datePath
    
    # 创建领域子目录
    foreach ($domain in $Domains) {
        New-DirectorySafe -Path (Join-Path $datePath $domain)
    }
    
    # 创建日志目录
    $logsPath = Join-Path $datePath "logs"
    New-DirectorySafe -Path $logsPath
    
    # 创建日志模板
    foreach ($logType in $LogTypes) {
        $logPath = Join-Path $logsPath "$date-$logType.md"
        $title = "$logType - $date"
        $content = "## $date $logType`n`n待更新..."
        New-TemplateFile -Path $logPath -Title $title -Content $content
    }
    
    # 创建当日汇总模板
    $summaryPath = Join-Path $datePath "$date-summary.md"
    $summaryContent = "## 当日论文汇总`n`n### 统计`n- 总论文数：0`n- csAI: 0`n- csLG: 0`n- 其他：0`n`n### 重点论文`n`n待更新...`n`n### 标签云`n`n待更新..."
    New-TemplateFile -Path $summaryPath -Title "$date 汇总" -Content $summaryContent
    
    # 创建论文清单模板
    $indexPath = Join-Path $datePath "$date-index.md"
    $indexContent = "## 论文索引`n`n| ID | 标题 | 领域 | 状态 | 笔记 |`n|----|------|------|------|------|`n| 1  |      |      | 待处理 | [ ] |`n"
    New-TemplateFile -Path $indexPath -Title "$date 索引" -Content $indexContent
    
    Write-Host "`n✓ $date 每日目录创建完成" -ForegroundColor Green
    Write-Host "  路径：$datePath" -ForegroundColor Gray
}

function Create-WeeklyStructure {
    param([string]$InputDate)
    
    $date = Get-ISODate -InputDate $InputDate
    $weekNum = Get-WeekNumber -InputDate $date
    $year = $date.Substring(0,4)
    $weekId = "$year-W$weekNum"
    
    Write-Host "`n=== 创建 $weekId 周汇总 ===" -ForegroundColor Cyan
    
    $weeklyPath = Join-Path $VaultPath $SyncRoot "weekly"
    New-DirectorySafe -Path $weeklyPath
    
    $weekFile = Join-Path $weeklyPath "$weekId-summary.md"
    $weekContent = "## $weekId 周汇总`n`n### 本周统计`n- 总论文数：0`n- 重点领域：`n- 趋势主题：`n`n### 重要论文`n`n待更新...`n`n### 周洞察`n`n待更新..."
    New-TemplateFile -Path $weekFile -Title "$weekId 汇总" -Content $weekContent
    
    Write-Host "`n✓ $weekId 周汇总创建完成" -ForegroundColor Green
}

function Create-MonthlyStructure {
    param([string]$InputDate)
    
    $date = Get-ISODate -InputDate $InputDate
    $month = Get-MonthYear -InputDate $date
    
    Write-Host "`n=== 创建 $month 月汇总 ===" -ForegroundColor Cyan
    
    $monthlyPath = Join-Path $VaultPath $SyncRoot "monthly"
    New-DirectorySafe -Path $monthlyPath
    
    $monthFile = Join-Path $monthlyPath "$month-summary.md"
    $monthContent = "## $month 月汇总`n`n### 本月统计`n- 总论文数：0`n- 周数：4`n- 重点领域：`n`n### 月度趋势`n`n待更新...`n`n### 重要突破`n`n待更新..."
    New-TemplateFile -Path $monthFile -Title "$month 汇总" -Content $monthContent
    
    Write-Host "`n✓ $month 月汇总创建完成" -ForegroundColor Green
}

# ==================== 主逻辑 ====================

Write-Host "`n╔══════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Obsidian Sync 目录自动化脚本       ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host "Vault: $VaultPath" -ForegroundColor Gray
Write-Host "Sync Root: $SyncRoot" -ForegroundColor Gray

if ($DryRun) {
    Write-Host "模式：预览 (不执行)" -ForegroundColor Yellow
} else {
    Write-Host "模式：执行" -ForegroundColor Green
}

try {
    if ($Init) {
        Initialize-FullStructure
    }
    
    if ($CreateDaily) {
        Create-DailyStructure -InputDate $Date
    }
    
    if ($CreateWeekly) {
        Create-WeeklyStructure -InputDate $Date
    }
    
    if ($CreateMonthly) {
        Create-MonthlyStructure -InputDate $Date
    }
    
    # 默认行为：如果没有任何参数，创建今日目录
    if (-not ($Init -or $CreateDaily -or $CreateWeekly -or $CreateMonthly)) {
        Create-DailyStructure -InputDate $Date
    }
    
    Write-Host "`n✓ 所有操作完成" -ForegroundColor Green
    
} catch {
    Write-Host "`n✗ 错误：$($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
