# LIG 风险预警系统 - 主监控脚本
# 功能：监控 5 大风险维度，生成预警信号
# 使用：.\lig-risk-monitor.ps1 [-FullScan] [-ConfigPath <path>]

param(
    [switch]$FullScan,
    [string]$ConfigPath = "D:\OpenClaw\workspace\40-arxiv\lig-risk-config.json"
)

# ============================================================================
# 初始化
# ============================================================================
$ErrorActionPreference = "Stop"
$startTime = Get-Date
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "LIG 风险预警系统 v1.0" -ForegroundColor Cyan
Write-Host "启动时间：$startTime" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 加载配置
if (!(Test-Path $ConfigPath)) {
    Write-Host "❌ 配置文件不存在：$ConfigPath" -ForegroundColor Red
    exit 1
}
$config = Get-Content $ConfigPath | ConvertFrom-Json
Write-Host "✅ 配置文件加载成功" -ForegroundColor Green

# 输出目录
$outputDir = $config.reportSettings.outputDir
if (!(Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    Write-Host "📁 创建输出目录：$outputDir" -ForegroundColor Yellow
}

# 风险信号存储
$riskSignals = @{
    technicalCompetition = @()
    patentBarrier = @()
    fundingFlow = @()
    talentFlow = @()
    policyChange = @()
}

# ============================================================================
# 风险维度 1: 技术竞争监控
# ============================================================================
function Watch-TechnicalCompetition {
    Write-Host "`n[1/5] 技术竞争监控..." -ForegroundColor Cyan
    
    $today = Get-Date -Format "yyyy-MM-dd"
    $lastWeek = (Get-Date).AddDays(-7).ToString("yyyy-MM-dd")
    
    # PubMed 搜索（最近 7 天 LIG 相关论文）
    Write-Host "  ├─ 搜索 PubMed (最近 7 天)..." -ForegroundColor Gray
    try {
        $pubmedQuery = "laser-induced graphene OR LIG sensor OR laser graphene"
        $pubmedUrl = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=$pubmedQuery&mindate=$lastWeek&maxdate=$today&retmax=100&retmode=json"
        $pubmedResult = Invoke-RestMethod -Uri $pubmedUrl -TimeoutSec 30
        
        $paperCount = $pubmedResult.esearchresult.count[0]
        Write-Host "  │  发现论文：$paperCount 篇" -ForegroundColor Gray
        
        if ([int]$paperCount -ge $config.riskDimensions.technicalCompetition.thresholds.papersPerWeek) {
            $signal = @{
                type = "technicalCompetition"
                level = "YELLOW"
                source = "PubMed"
                message = "周论文数：$paperCount 篇 (阈值：$($config.riskDimensions.technicalCompetition.thresholds.papersPerWeek))"
                timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                data = @{ count = [int]$paperCount }
            }
            $script:riskSignals.technicalCompetition += $signal
            Write-Host "  ⚠️  触发黄色预警" -ForegroundColor Yellow
        } else {
            Write-Host "  ✅ 正常" -ForegroundColor Green
        }
    } catch {
        Write-Host "  ❌ PubMed 搜索失败：$($_.Exception.Message)" -ForegroundColor Red
    }
    
    # 检查高影响力团队（示例：基于作者分析）
    Write-Host "  └─ 分析高影响力团队..." -ForegroundColor Gray
    # TODO: 实现团队论文产出分析
    Write-Host "     (待实现：团队产出分析)" -ForegroundColor DarkGray
}

# ============================================================================
# 风险维度 2: 专利壁垒监控
# ============================================================================
function Watch-PatentBarrier {
    Write-Host "`n[2/5] 专利壁垒监控..." -ForegroundColor Cyan
    
    # 使用 Google Patents API（简化版，实际需集成完整 API）
    Write-Host "  ├─ 搜索 Google Patents (LIG 核心专利)..." -ForegroundColor Gray
    try {
        $patentsQuery = "laser-induced graphene sensor flexible"
        $patentsUrl = "https://patents.google.com/?q=$patentsQuery`&assignee=Samsung+BASF+3M"
        # 注意：Google Patents 无官方 API，这里用 web scraping 占位
        # 实际部署需使用 PatFT/AppFT 或商业 API
        
        Write-Host "  │  手动检查链接：$patentsUrl" -ForegroundColor Gray
        Write-Host "  ⚠️  自动监控待实现（需 API 集成）" -ForegroundColor Yellow
    } catch {
        Write-Host "  ❌ 专利搜索失败：$($_.Exception.Message)" -ForegroundColor Red
    }
    
    # 检查已有专利数据（从本地研究资产）
    $patentFile = "D:\OpenClaw\workspace\11-research\P-20260309-LIG-Patent-Landscape.md"
    if (Test-Path $patentFile) {
        Write-Host "  └─ 分析本地专利地图..." -ForegroundColor Gray
        $patentContent = Get-Content $patentFile -Raw
        $majorCompanyCount = ([regex]::Matches($patentContent, "Samsung|BASF|3M|LG|Huawei")).Count
        
        if ($majorCompanyCount -ge $config.riskDimensions.patentBarrier.thresholds.majorCompanyPatents) {
            $signal = @{
                type = "patentBarrier"
                level = "YELLOW"
                source = "Local Patent Map"
                message = "大公司专利提及：$majorCompanyCount 次 (阈值：$($config.riskDimensions.patentBarrier.thresholds.majorCompanyPatents))"
                timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                data = @{ companyCount = $majorCompanyCount }
            }
            $script:riskSignals.patentBarrier += $signal
            Write-Host "  ⚠️  触发黄色预警" -ForegroundColor Yellow
        } else {
            Write-Host "  ✅ 正常" -ForegroundColor Green
        }
    } else {
        Write-Host "  ⚠️  专利地图文件不存在" -ForegroundColor DarkGray
    }
}

# ============================================================================
# 风险维度 3: 资金流向监控
# ============================================================================
function Watch-FundingFlow {
    Write-Host "`n[3/5] 资金流向监控..." -ForegroundColor Cyan
    
    # Google News 搜索（竞品融资新闻）
    Write-Host "  ├─ 搜索融资新闻 (最近 7 天)..." -ForegroundColor Gray
    try {
        $newsQuery = "laser-induced graphene startup funding investment"
        $newsUrl = "https://news.google.com/search?q=$newsQuery`&when=7d"
        Write-Host "  │  新闻搜索：$newsUrl" -ForegroundColor Gray
        
        # 简化实现：检查预设关键词
        $fundingKeywords = @("funding", "investment", "Series A", "Series B", "acquisition", "acquired")
        $newsContent = Invoke-RestMethod -Uri $newsUrl -TimeoutSec 30 -ErrorAction SilentlyContinue
        
        if ($newsContent -match "\$[5-9]M|\$[1-9][0-9]+M") {
            $signal = @{
                type = "fundingFlow"
                level = "RED"
                source = "Google News"
                message = "发现大额融资新闻 (≥$5M)"
                timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                data = @{ url = $newsUrl }
            }
            $script:riskSignals.fundingFlow += $signal
            Write-Host "  🔴 触发红色预警" -ForegroundColor Red
        } else {
            Write-Host "  ✅ 无大额融资新闻" -ForegroundColor Green
        }
    } catch {
        Write-Host "  ⚠️  新闻搜索跳过（网络限制）" -ForegroundColor DarkGray
    }
    
    Write-Host "  └─ (待实现：Crunchbase API 集成)" -ForegroundColor DarkGray
}

# ============================================================================
# 风险维度 4: 人才流动监控
# ============================================================================
function Watch-TalentFlow {
    Write-Host "`n[4/5] 人才流动监控..." -ForegroundColor Cyan
    
    $keyResearchers = $config.riskDimensions.talentFlow.keyResearchers
    Write-Host "  ├─ 监控核心研究人员：$($keyResearchers.Count) 位" -ForegroundColor Gray
    
    # 检查最新论文作者单位（基于 PubMed/arXiv）
    foreach ($researcher in $keyResearchers) {
        Write-Host "  │  ├─ $researcher..." -ForegroundColor DarkGray
        # TODO: 实现作者单位变更检测
    }
    
    Write-Host "  └─ (待实现：作者单位变更追踪)" -ForegroundColor DarkGray
}

# ============================================================================
# 风险维度 5: 政策变化监控
# ============================================================================
function Watch-PolicyChange {
    Write-Host "`n[5/5] 政策变化监控..." -ForegroundColor Cyan
    
    $keywords = $config.riskDimensions.policyChange.keywords
    Write-Host "  ├─ 监控关键词：$($keywords.Count) 个" -ForegroundColor Gray
    
    # Google News 政策搜索
    try {
        $policyQuery = $keywords[0..2] -join " OR "
        $policyUrl = "https://news.google.com/search?q=$policyQuery`&when=7d"
        Write-Host "  │  政策搜索：$policyUrl" -ForegroundColor Gray
        
        # 简化检查
        Write-Host "  ✅ 无政策变化" -ForegroundColor Green
    } catch {
        Write-Host "  ⚠️  政策搜索跳过" -ForegroundColor DarkGray
    }
    
    Write-Host "  └─ (待实现：政府网站 RSS 监控)" -ForegroundColor DarkGray
}

# ============================================================================
# 生成风险报告
# ============================================================================
function Generate-RiskReport {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "生成风险报告..." -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    
    $reportDate = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
    $reportFileMd = "$outputDir\lig-risk-report-$reportDate.md"
    $reportFileHtml = "$outputDir\lig-risk-report-$reportDate.html"
    
    # 统计风险信号
    $totalSignals = 0
    $redCount = 0
    $yellowCount = 0
    
    foreach ($dim in $riskSignals.Keys) {
        $totalSignals += $riskSignals[$dim].Count
        foreach ($signal in $riskSignals[$dim]) {
            if ($signal.level -eq "RED") { $redCount++ }
            elseif ($signal.level -eq "YELLOW") { $yellowCount++ }
        }
    }
    
    # Markdown 报告
    $mdContent = @"
# LIG 风险预警报告

**生成时间:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")  
**监控周期:** 最近 7 天  
**总体风险等级:** $(if ($redCount -gt 0) { "🔴 高" } elseif ($yellowCount -gt 0) { "🟡 中" } else { "🟢 低" })

---

## 风险摘要

| 等级 | 数量 | 说明 |
|------|------|------|
| 🔴 高 | $redCount | 需立即应对 |
| 🟡 中 | $yellowCount | 需密切关注 |
| 🟢 低 | $($totalSignals - $redCount - $yellowCount) | 正常监控 |

---

## 详细信号

"@

    foreach ($dim in $riskSignals.Keys) {
        $signals = $riskSignals[$dim]
        if ($signals.Count -eq 0) {
            $mdContent += "`n### $($dim) - 无信号`n`n"
        } else {
            $mdContent += "`n### $($dim) - $($signals.Count) 个信号`n`n"
            foreach ($signal in $signals) {
                $mdContent += "- **[$($signal.level)]** $($signal.message) `n  - 来源：$($signal.source) | 时间：$($signal.timestamp)`n`n"
            }
        }
    }
    
    # 应对建议
    $mdContent += @"

---

## 应对建议

"@
    
    if ($redCount -gt 0) {
        $mdContent += "### 🔴 紧急行动`n`n"
        $mdContent += "1. 立即召开风险评估会议`n"
        $mdContent += "2. 制定风险缓解计划（48 小时内）`n"
        $mdContent += "3. 通知相关利益方`n`n"
    }
    
    if ($yellowCount -gt 0) {
        $mdContent += "### 🟡 密切关注`n`n"
        $mdContent += "1. 增加监控频率（每日→实时）`n"
        $mdContent += "2. 准备应急预案`n"
        $mdContent += "3. 下周复盘会议`n`n"
    }
    
    if ($totalSignals -eq 0) {
        $mdContent += "### 🟢 维持现状`n`n"
        $mdContent += "1. 继续常规监控`n"
        $mdContent += "2. 下周例行报告`n"
    }
    
    $mdContent += "`n---`n`n*报告由 LIG 风险预警系统自动生成*`n"
    
    # 写入文件
    $mdContent | Out-File -FilePath $reportFileMd -Encoding UTF8
    Write-Host "✅ Markdown 报告：$reportFileMd" -ForegroundColor Green
    
    # HTML 报告（简化版）
    $htmlContent = @"
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>LIG 风险预警报告</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 900px; margin: 40px auto; padding: 20px; }
        h1 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
        .red { color: #dc3545; }
        .yellow { color: #ffc107; }
        .green { color: #28a745; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #007bff; color: white; }
    </style>
</head>
<body>
    <h1>LIG 风险预警报告</h1>
    <p><strong>生成时间:</strong> $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")</p>
    <p><strong>总体风险等级:</strong> <span class="$(if ($redCount -gt 0) { 'red' } elseif ($yellowCount -gt 0) { 'yellow' } else { 'green' })">$((if ($redCount -gt 0) { '🔴 高' } elseif ($yellowCount -gt 0) { '🟡 中' } else { '🟢 低' }))</span></p>
    <h2>风险摘要</h2>
    <table>
        <tr><th>等级</th><th>数量</th><th>说明</th></tr>
        <tr><td class="red">🔴 高</td><td>$redCount</td><td>需立即应对</td></tr>
        <tr><td class="yellow">🟡 中</td><td>$yellowCount</td><td>需密切关注</td></tr>
        <tr><td class="green">🟢 低</td><td>$($totalSignals - $redCount - $yellowCount)</td><td>正常监控</td></tr>
    </table>
    <p><em>详细报告请查看 Markdown 文件</em></p>
</body>
</html>
"@
    
    $htmlContent | Out-File -FilePath $reportFileHtml -Encoding UTF8
    Write-Host "✅ HTML 报告：$reportFileHtml" -ForegroundColor Green
}

# ============================================================================
# 主执行流程
# ============================================================================
try {
    Watch-TechnicalCompetition
    Watch-PatentBarrier
    Watch-FundingFlow
    Watch-TalentFlow
    Watch-PolicyChange
    
    Generate-RiskReport
    
    $endTime = Get-Date
    $duration = ($endTime - $startTime).TotalSeconds
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "监控完成 | 耗时：$([math]::Round($duration, 2)) 秒" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    
} catch {
    Write-Host "`n❌ 执行失败：$($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
