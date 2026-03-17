# daily-brief.ps1 - 每日简报自动生成
# 用法：py daily-brief.ps1 [--date YYYY-MM-DD] [--send]
# 定时任务：每工作日 8:00 AM

param(
    [string]$Date = (Get-Date).AddDays(-1).ToString("yyyy-MM-dd"),
    [switch]$Send
)

$ErrorActionPreference = "Stop"
$Workspace = "D:\OpenClaw\workspace"
$BriefDir = "$Workspace\21-reports\daily-briefs"
$MemoryDir = "$Workspace\13-memory"

# 确保输出目录存在
if (!(Test-Path $BriefDir)) {
    New-Item -ItemType Directory -Path $BriefDir | Out-Null
}

Write-Host "📊 生成每日简报 | 日期：$Date" -ForegroundColor Cyan

# ============================================================================
# 1. 收集 arXiv 数据
# ============================================================================
Write-Host "`n📥 收集 arXiv 数据..." -ForegroundColor Yellow

$arxivDir = "$Workspace\40-arxiv\papers\$Date"
$arxivCount = 0
$arxivHighPriority = 0

if (Test-Path $arxivDir) {
    $papers = Get-ChildItem $arxivDir -Filter "*.md" | Where-Object { $_.Name -notlike "*~*" }
    $arxivCount = $papers.Count
    
    # 简单优先级判断 (文件名包含 high 或 在笔记中标记)
    $arxivHighPriority = ($papers | Where-Object { $_.Name -match "high|priority" }).Count
}

Write-Host "  ├─ 收集：$arxivCount 篇" -ForegroundColor Gray
Write-Host "  └─ 高优先级：$arxivHighPriority 篇" -ForegroundColor Gray

# ============================================================================
# 2. 收集 Medium 数据
# ============================================================================
Write-Host "`n📰 收集 Medium 数据..." -ForegroundColor Yellow

$mediumDir = "$Workspace\41-medium\analyzed\$Date"
$mediumCount = 0
$mediumDeep = 0

if (Test-Path $mediumDir) {
    $articles = Get-ChildItem $mediumDir -Filter "*.md" | Where-Object { $_.Name -notlike "*~*" }
    $mediumCount = $articles.Count
    # 深度解析 = 包含完整分析结构的文章
    $mediumDeep = ($articles | Where-Object { 
        (Get-Content $_.FullName -Raw) -match "## Core question" 
    }).Count
}

Write-Host "  ├─ 分析：$mediumCount 篇" -ForegroundColor Gray
Write-Host "  └─ 深度解析：$mediumDeep 篇" -ForegroundColor Gray

# ============================================================================
# 3. GitHub 同步状态
# ============================================================================
Write-Host "`n🐙 检查 GitHub 状态..." -ForegroundColor Yellow

$gitStatus = "✅"
$gitCommits = 0

try {
    Set-Location $Workspace
    $commitLog = git log --since="$Date 00:00" --until="$Date 23:59" --oneline 2>$null
    if ($commitLog) {
        $gitCommits = ($commitLog | Measure-Object).Count
    }
    
    # 检查是否有未推送的提交
    $unpushed = git rev-list --count HEAD @{u} 2>$null
    if ($unpushed -and $unpushed -gt 0) {
        $gitStatus = "⚠️ 待推送 ($unpushed)"
    }
} catch {
    $gitStatus = "❌ 检查失败"
}

Write-Host "  ├─ 提交：$gitCommits 次" -ForegroundColor Gray
Write-Host "  └─ 同步：$gitStatus" -ForegroundColor Gray

# ============================================================================
# 4. 领域段位变化
# ============================================================================
Write-Host "`n🏆 计算领域排名..." -ForegroundColor Yellow

$domainOutput = py "$Workspace\30-scripts\domain_ranker_v2.py" --compare 2>$null
$topDomains = @()

if ($domainOutput) {
    # 解析前 3 名
    $lines = $domainOutput -split "`n"
    foreach ($line in $lines) {
        if ($line -match "^\s*(\d+)\s+(\w+)\s+\[IRON\]\s+黑铁\s+(\d+)") {
            $topDomains += [PSCustomObject]@{
                Rank = $matches[1]
                Domain = $matches[2]
                Level = $matches[3]
            }
            if ($topDomains.Count -ge 3) { break }
        }
    }
}

# ============================================================================
# 5. 生成简报内容
# ============================================================================
Write-Host "`n📝 生成简报..." -ForegroundColor Yellow

$briefContent = @"
# 📊 每日简报 | $Date

**生成时间:** $(Get-Date -Format "yyyy-MM-dd HH:mm")  
**数据周期:** $Date 00:00 - $Date 23:59

---

## 🎯 核心指标

| 指标 | 数值 | 状态 |
|------|------|------|
| arXiv 收集 | $arxivCount 篇 | $(if ($arxivCount -gt 0) { "✅" } else { "⚠️" }) |
| 高优先级论文 | $arxivHighPriority 篇 | $(if ($arxivHighPriority -gt 0) { "🔥" } else { "- " }) |
| Medium 分析 | $mediumCount 篇 | $(if ($mediumCount -gt 0) { "✅" } else { "⚠️" }) |
| 深度解析 | $mediumDeep 篇 | $(if ($mediumDeep -gt 0) { "🧠" } else { "- " }) |
| GitHub 提交 | $gitCommits 次 | $(if ($gitCommits -gt 0) { "✅" } else { "⚠️" }) |
| 同步状态 | $gitStatus | $(if ($gitStatus -eq "✅") { "✅" } else { "⚠️" }) |

---

## 🏆 领域段位 Top 3

"@

if ($topDomains.Count -gt 0) {
    foreach ($d in $topDomains) {
        $briefContent += "- **#$($d.Rank) $($d.Domain):** 黑铁 $($d.Level) 级`n"
    }
} else {
    $briefContent += "- 暂无排名数据`n"
}

$briefContent += @"

---

## 🔥 高优先级内容

"@

# 添加高优先级论文标题 (前 5 篇)
if (Test-Path $arxivDir) {
    $highPriorityPapers = Get-ChildItem $arxivDir -Filter "*.md" | 
        Where-Object { $_.Name -match "high|priority" } | 
        Select-Object -First 5
    
    if ($highPriorityPapers.Count -gt 0) {
        $i = 1
        foreach ($paper in $highPriorityPapers) {
            $title = (Get-Content $paper.FullName -First 1) -replace "^# ", ""
            $briefContent += "$i. **$title**`n"
            $i++
        }
    } else {
        $briefContent += "- 无高优先级内容`n"
    }
} else {
    $briefContent += "- 无数据`n"
}

$briefContent += @"

---

## ⚠️ 待处理事项

"@

# 检查待解析论文
$pendingParse = 0
if (Test-Path "$Workspace\40-arxiv\queued") {
    $pendingParse = (Get-ChildItem "$Workspace\40-arxiv\queued" -Filter "*.md" 2>$null).Count
}

$briefContent += "- 待解析论文：$pendingParse 篇`n"

# 检查待同步文件
$pendingSync = 0
try {
    Set-Location $Workspace
    $pendingSync = git status --porcelain 2>$null | Measure-Object | Select-Object -ExpandProperty Count
} catch {}

$briefContent += "- Git 待提交：$pendingSync 个文件`n"

$briefContent += @"

---

## 📋 详细数据

- arXiv 目录：`$arxivDir
- Medium 目录：`$mediumDir
- 简报存档：`$BriefDir

---

*自动生成 by daily-brief.ps1 | OpenClaw Workspace*
"@

# 保存简报
$briefFile = "$BriefDir\brief-$Date.md"
$briefContent | Out-File -FilePath $briefFile -Encoding utf8

Write-Host "  └─ 已保存：$briefFile" -ForegroundColor Green

# ============================================================================
# 6. 可选：发送到 Feishu
# ============================================================================
if ($Send) {
    Write-Host "`n📤 发送到 Feishu..." -ForegroundColor Yellow
    
    # 使用 message 工具发送 (通过 OpenClaw)
    # 注意：这里需要调用 OpenClaw 的 message 工具，PowerShell 无法直接调用
    # 实际部署时可通过 openclaw CLI 或 API 触发
    
    Write-Host "  └─ Feishu 推送需通过 OpenClaw message 工具实现" -ForegroundColor Gray
    Write-Host "  └─ 手动发送：openclaw message send --channel feishu --file `"$briefFile`"" -ForegroundColor Gray
}

Write-Host "`n✅ 简报生成完成！" -ForegroundColor Green
Write-Host "📁 文件位置：$briefFile" -ForegroundColor Cyan
