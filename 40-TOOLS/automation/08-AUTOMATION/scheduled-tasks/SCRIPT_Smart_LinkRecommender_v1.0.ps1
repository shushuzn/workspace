#!/usr/bin/env pwsh
# Smart Link Recommender - 智能链接推荐系统
# 用法：.\smart-link-recommender.ps1 [-Path <dir>] [-File <specific_file>]

param(
    [string]$Path = "D:\OpenClaw\workspace",
    [string]$File = "",
    [string]$OutputFile = "link-recommendations.md"
)

Write-Host "Smart Link Recommender - 智能链接推荐" -ForegroundColor Cyan
Write-Host ""

# Topic keyword library
$topicKeywords = @{
    "memory" = @("memory", "memor", "recall")
    "research" = @("research", "project", "paper")
    "lig" = @("lig", "conductivity", "graphene")
    "cnt" = @("cnt", "nanotube")
    "workflow" = @("workflow", "pipeline", "auto")
    "script" = @("script", "tool", "utility")
    "data" = @("arxiv", "medium", "collect")
    "graph" = @("knowledge", "graph", "network")
    "model" = @("model", "train", "gp", "prediction")
    "index" = @("index", "link", "catalog")
}

function Get-DocumentTopics {
    param([string]$Content)
    
    $topics = @()
    $contentLower = $Content.ToLower()
    
    foreach ($topic in $topicKeywords.Keys) {
        foreach ($keyword in $topicKeywords[$topic]) {
            if ($contentLower -like "*$keyword*") {
                $topics += $topic
                break
            }
        }
    }
    
    return $topics
}

if ($File) {
    # Single file mode
    $targetPath = Join-Path $Path $File
    if (-not (Test-Path $targetPath)) {
        Write-Host "Error: File not found: $File" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Analyzing: $File" -ForegroundColor Yellow
    
    $content = Get-Content $targetPath -Raw
    $targetTopics = Get-DocumentTopics $content
    
    Write-Host "Topics: $($targetTopics -join ', ')" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "Finding similar documents..." -ForegroundColor Yellow
    
    $similarDocs = @()
    $mdFiles = Get-ChildItem -Path $Path -Filter "*.md" -Recurse |
        Where-Object { $_.FullName -ne $targetPath }
    
    foreach ($mdFile in $mdFiles) {
        $fileContent = Get-Content $mdFile.FullName -Raw -ErrorAction SilentlyContinue
        if (-not $fileContent) { continue }
        
        $fileTopics = Get-DocumentTopics $fileContent
        
        # Calculate similarity (shared topics)
        $sharedTopics = $targetTopics | Where-Object { $fileTopics -contains $_ }
        $similarity = $sharedTopics.Count
        
        if ($similarity -gt 0) {
            $relPath = $mdFile.FullName.Replace($Path, "").TrimStart('\') -replace '.md$',''
            $similarDocs += @{
                Path = $relPath
                Topics = $fileTopics
                SharedTopics = $sharedTopics
                Similarity = $similarity
            }
        }
    }
    
    # Sort by similarity
    $similarDocs = $similarDocs | Sort-Object Similarity -Descending | Select-Object -First 10
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Recommendations for: $File" -ForegroundColor Cyan
    Write-Host "========================================"
    
    $i = 1
    foreach ($doc in $similarDocs) {
        $sharedTopicsStr = ($doc.SharedTopics | ForEach-Object { $topicKeywords[$_] | Select-Object -First 1 }) -join ', '
        Write-Host "$i. [[$($doc.Path)]] - Shared: $sharedTopicsStr (Score: $($doc.Similarity))"
        $i++
    }
    
} else {
    # Batch mode - generate recommendations for all documents
    Write-Host "Batch mode: Generating recommendations for all documents..." -ForegroundColor Yellow
    Write-Host ""
    
    $allDocs = @{}
    $mdFiles = Get-ChildItem -Path $Path -Filter "*.md" -Recurse
    
    Write-Host "Step 1: Indexing documents..." -ForegroundColor Yellow
    foreach ($mdFile in $mdFiles) {
        $content = Get-Content $mdFile.FullName -Raw -ErrorAction SilentlyContinue
        if (-not $content) { continue }
        
        $topics = Get-DocumentTopics $content
        if ($topics.Count -gt 0) {
            $relPath = $mdFile.FullName.Replace($Path, "").TrimStart('\') -replace '.md$',''
            $allDocs[$relPath] = $topics
        }
    }
    
    Write-Host "Indexed $($allDocs.Count) documents" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "Step 2: Generating recommendations..." -ForegroundColor Yellow
    
    $report = @"
# Smart Link Recommendations

**Generated:** $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  
**Documents indexed:** $($allDocs.Count)

---

## Top Recommended Links by Topic

"@
    
    foreach ($topic in $topicKeywords.Keys) {
        $docsWithTopic = $allDocs.GetEnumerator() | Where-Object { $_.Value -contains $topic } | Select-Object -First 10
        
        if ($docsWithTopic.Count -gt 0) {
            $report += "### $topic`n`n"
            foreach ($doc in $docsWithTopic) {
                $report += "- [[$($doc.Key)]]`n"
            }
            $report += "`n"
        }
    }
    
    $report += @"

---

## How to Use

1. **Single file mode:**
   ```powershell
   .\smart-link-recommender.ps1 -File "path/to/file.md"
   ```

2. **Batch mode (this report):**
   ```powershell
   .\smart-link-recommender.ps1
   ```

3. **Add recommendations to documents:**
   Review and manually add relevant links to your documents.

---

*Auto-generated by smart-link-recommender.ps1*
"@
    
    $report | Out-File -FilePath (Join-Path $Path $OutputFile) -Encoding utf8
    Write-Host "Report saved: $OutputFile" -ForegroundColor Green
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Cyan
