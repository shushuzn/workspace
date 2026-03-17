#!/usr/bin/env pwsh
<#
.SYNOPSIS
    arxiv-daily + AI Research OS 编排脚本
    自动收集 arXiv 论文并调用 AI Research OS 进行深度解析

.DESCRIPTION
    1. 调用 arxiv-daily MCP 收集论文
    2. 筛选高优先级论文 (≥4.0 分)
    3. 限制解析数量 (每日 3 篇)
    4. 调用 AI Research OS 生成 P-Note/C-Note
    5. 保存到 11-research/papers/
    6. Git 自动提交

.EXAMPLE
    .\arxiv-research-orchestrator.ps1 -MinScore 4.0 -MaxPapers 3
#>

param(
    [double]$MinScore = 4.0,
    [int]$MaxPapers = 3,
    [string]$OutputDir = "D:\OpenClaw\workspace\11-research\papers",
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"
$StartTime = Get-Date

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  arXiv Research Orchestrator" -ForegroundColor Cyan
Write-Host "  Started: $($StartTime.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Step 1: 收集 arXiv 论文
Write-Host "[Step 1/5] Collecting arXiv papers..." -ForegroundColor Yellow
try {
    $collectResult = mcporter call arxiv-daily.collect --json 2>$null | ConvertFrom-Json
    
    if ($collectResult.error) {
        throw "MCP call failed: $($collectResult.error.message)"
    }
    
    $result = $collectResult.result.content[0].text | ConvertFrom-Json
    Write-Host "  Total papers: $($result.total)" -ForegroundColor Green
    Write-Host "  High priority (≥$MinScore): $($result.high_priority)" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Failed to collect papers: $_" -ForegroundColor Red
    exit 1
}

# Step 2: 筛选高优先级论文
Write-Host "`n[Step 2/5] Filtering high priority papers..." -ForegroundColor Yellow
$highPriorityPapers = $result.papers | Where-Object { $_.priority_score -ge $MinScore } | Select-Object -First $MaxPapers
Write-Host "  Selected for analysis: $($highPriorityPapers.Count)" -ForegroundColor Green

if ($highPriorityPapers.Count -eq 0) {
    Write-Host "  No papers selected. Exiting." -ForegroundColor Yellow
    exit 0
}

# Step 3: 创建输出目录
Write-Host "`n[Step 3/5] Creating output directory..." -ForegroundColor Yellow
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    Write-Host "  Created: $OutputDir" -ForegroundColor Green
}

# Step 4: 调用 AI Research OS 解析每篇论文
Write-Host "`n[Step 4/5] Analyzing papers with AI Research OS..." -ForegroundColor Yellow

$analyzedPapers = @()
foreach ($paper in $highPriorityPapers) {
    $arxivId = $paper.arxiv_id
    $title = $paper.title.Substring(0, [Math]::Min(50, $paper.title.Length))
    
    Write-Host "`n  Analyzing: $title..." -ForegroundColor Cyan
    Write-Host "  arXiv ID: $arxivId" -ForegroundColor Gray
    
    # 生成文件名
    $noteFile = "P-$arxivId.md"
    $notePath = Join-Path $OutputDir $noteFile
    
    # 检查是否已存在
    if (Test-Path $notePath) {
        Write-Host "  SKIP: Already exists" -ForegroundColor Yellow
        continue
    }
    
    # 准备 AI Research OS 输入
    $paperUrl = "https://arxiv.org/abs/$arxivId"
    $pdfUrl = "https://arxiv.org/pdf/$arxivId.pdf"
    
    Write-Host "  Downloading PDF..." -ForegroundColor Gray
    try {
        $pdfPath = Join-Path $OutputDir "$arxivId.pdf"
        Invoke-WebRequest -Uri $pdfUrl -OutFile $pdfPath -UseBasicParsing -ErrorAction Stop
        Write-Host "  PDF downloaded: $pdfPath" -ForegroundColor Green
    } catch {
        Write-Host "  WARNING: Failed to download PDF: $_" -ForegroundColor Yellow
        $pdfPath = $null
    }
    
    # 调用 AI Research OS (通过 Python 脚本)
    Write-Host "  Calling AI Research OS..." -ForegroundColor Gray
    
    $aiResearchScript = "D:\npm-global\node_modules\openclaw\skills\ai-research-os\scripts\analyze_paper.py"
    if (Test-Path $aiResearchScript) {
        # 调用 Python 脚本
        $analysisResult = py $aiResearchScript --arxiv-id $arxivId --output $OutputDir 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  Analysis complete" -ForegroundColor Green
        } else {
            Write-Host "  WARNING: AI Research OS failed, creating template" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  WARNING: AI Research OS script not found, creating template" -ForegroundColor Yellow
    }
    
    # 如果 AI Research OS 失败或未安装，创建 P-Note 模板
    if (-not (Test-Path $notePath)) {
        $noteContent = @"
# P-Note: $arxivId

**Title:** $($paper.title)

**Authors:** $($paper.authors -join ', ')

**Categories:** $($paper.categories -join ', ')

**arXiv:** https://arxiv.org/abs/$arxivId

**PDF:** $pdfUrl

**Priority Score:** $($paper.priority_score)

**Collected:** $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

---

## Research Question Card

**我想解决什么问题？**
<!-- 清晰表述研究问题 -->

**为什么重要？**
<!-- 技术/商业/学术价值 -->

**我的先验判断？**
<!-- 分析前的假设 -->

**什么证据会推翻我？**
<!-- 证伪条件 -->

---

## 1. 背景

<!-- 研究领域、历史脉络、关键挑战 -->

---

## 2. 核心问题

<!-- 精确定义要解决的问题 -->

---

## 3. 方法结构

<!-- 架构图、核心组件、数据流 -->

---

## 4. 关键假设

<!-- 方法依赖的前提条件 -->

---

## 5. 关键创新

<!-- 与 prior work 的本质差异 -->

---

## 6. 实验结果

<!-- 主实验、Ablation、对比基线 -->

---

## 7. 对抗式审稿

### 潜在弱点
<!-- 方法、实验、结论的潜在问题 -->

### 开放问题
<!-- 未解决的问题 -->

### 复现难度
<!-- 高/中/低 + 原因 -->

---

## 8. 优势

<!-- 相对现有方法的改进 -->

---

## 9. 局限

<!-- 明确边界和失败场景 -->

---

## 10. 本质抽象

<!-- 可迁移的核心思想 -->

---

## 与我工作的关联

### 技术坐标
<!-- 在技术演进中的位置 -->

### 可借鉴点
<!-- 可以学习的方法/思想 -->

### 下一步行动
<!-- 基于此论文的行动项 -->

---

## 参考资料

- [arXiv]($paperUrl)
- [PDF]($pdfUrl)
- [Code](<!-- 如果有代码仓库 -->)

---

*Generated by arxiv-research-orchestrator.ps1*
*AI Research OS Analysis: $([bool]$aiResearchScript)*
"@
        
        # 保存笔记
        $noteContent | Out-File -FilePath $notePath -Encoding UTF8
        Write-Host "  Saved: $notePath" -ForegroundColor Green
    }
    
    $analyzedPapers += @{
        arxiv_id = $arxivId
        title = $paper.title
        note_path = $notePath
        pdf_downloaded = [bool]$pdfPath
        ai_analyzed = $false  # TODO: Set to true if AI Research OS succeeded
    }
}

# Step 5: Git 提交
Write-Host "`n[Step 5/5] Committing to Git..." -ForegroundColor Yellow

if ($analyzedPapers.Count -gt 0) {
    Set-Location "D:\OpenClaw\workspace"
    
    git add $OutputDir | Out-Null
    
    $commitMessage = "Add $($analyzedPapers.Count) P-Note(s) from arXiv daily ($($StartTime.ToString('yyyy-MM-dd')))"
    git commit -m $commitMessage | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        git push | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  Committed and pushed: $commitMessage" -ForegroundColor Green
        } else {
            Write-Host "  WARNING: Push failed" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  WARNING: Commit failed (no changes?)" -ForegroundColor Yellow
    }
} else {
    Write-Host "  No new papers to commit" -ForegroundColor Gray
}

# 总结
$EndTime = Get-Date
$Duration = New-TimeSpan -Start $StartTime -End $EndTime

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Total collected: $($result.total)" -ForegroundColor White
Write-Host "  High priority: $($result.high_priority)" -ForegroundColor White
Write-Host "  Analyzed: $($analyzedPapers.Count)" -ForegroundColor Green
Write-Host "  Duration: $($Duration.Minutes)m $($Duration.Seconds)s" -ForegroundColor White
Write-Host "========================================`n" -ForegroundColor Cyan

# 输出 JSON 结果
$output = @{
    date = $StartTime.ToString('yyyy-MM-dd')
    total_collected = $result.total
    high_priority = $result.high_priority
    analyzed = $analyzedPapers.Count
    papers = $analyzedPapers
    duration_seconds = $Duration.TotalSeconds
}

$output | ConvertTo-Json | Out-File -FilePath "$OutputDir\orchestrator-result-$(Get-Date -Format 'yyyy-MM-dd').json" -Encoding UTF8

Write-Host "Result saved: orchestrator-result-$(Get-Date -Format 'yyyy-MM-dd').json`n" -ForegroundColor Green
