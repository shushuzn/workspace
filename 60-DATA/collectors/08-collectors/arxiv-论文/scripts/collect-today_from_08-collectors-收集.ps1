# arXiv 轻量收集脚本 - 无需 Python
# 使用 PowerShell + arXiv API

param(
    [string]$Date = (Get-Date -Format "yyyy-MM-dd"),
    [string]$OutputDir = "daily\$Date"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "arXiv 轻量收集 - $Date" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 创建输出目录
$fullPath = Join-Path $PSScriptRoot $OutputDir
if (-not (Test-Path $fullPath)) {
    New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
    Write-Host "[OK] 创建目录：$fullPath" -ForegroundColor Green
}

# arXiv API 端点
$categories = @("cs.AI", "cs.LG", "cs.CL", "cs.NE", "cs.AR", "cs.SE")
$keywords = @("agent", "reasoning", "efficient", "adaptive", "routing", "planning", "MCP", "tool", "autonomous")

$allPapers = @()

foreach ($cat in $categories) {
    Write-Host "`n[1/$($categories.Count)] 获取 $cat 类别..." -ForegroundColor Yellow
    
    $url = "http://export.arxiv.org/api/query?search_query=cat:$cat&start=0&max_results=10&sortBy=submittedDate&sortOrder=descending"
    
    try {
        $response = Invoke-WebRequest -Uri $url -TimeoutSec 30 -UseBasicParsing
        $xml = [xml]$response.Content
        
        foreach ($entry in $xml.feed.entry) {
            $title = $entry.title -replace "`n", " "
            $summary = $entry.summary -replace "`n", " "
            $published = $entry.published
            $id = $entry.id
            
            # 关键词匹配
            $score = 0
            foreach ($kw in $keywords) {
                if ($title -match $kw -or $summary -match $kw) {
                    $score++
                }
            }
            
            if ($score -ge 1) {
                $allPapers += @{
                    title = $title
                    summary = $summary
                    published = $published
                    id = $id
                    category = $cat
                    score = $score
                }
            }
        }
        
        Write-Host "  [OK] 获取 $($xml.feed.entry.Count) 篇" -ForegroundColor Green
    } catch {
        Write-Host "  [ERROR] 获取失败：$_" -ForegroundColor Red
    }
}

# 保存结果
if ($allPapers.Count -gt 0) {
    $jsonPath = Join-Path $fullPath "arxiv-$Date.json"
    $allPapers | ConvertTo-Json -Depth 5 | Out-File -FilePath $jsonPath -Encoding utf8
    Write-Host "`n[OK] 保存：$jsonPath" -ForegroundColor Green
    Write-Host "  总计：$($allPapers.Count) 篇论文" -ForegroundColor Cyan
} else {
    Write-Host "`n[WARN] 未找到匹配的论文" -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "完成!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
