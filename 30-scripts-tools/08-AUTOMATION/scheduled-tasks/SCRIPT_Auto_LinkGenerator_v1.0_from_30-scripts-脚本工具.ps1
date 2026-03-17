#!/usr/bin/env pwsh
# Auto-Link Generator - Auto categorize and generate internal links
# Usage: .\auto-link-generator.ps1 [-Path <dir>] [-DryRun]

param(
    [string]$Path = "D:\OpenClaw\workspace",
    [switch]$DryRun,
    [string]$OutputFile = "auto-link-report.md"
)

Write-Host "Auto-Link Generator - Auto categorize documents" -ForegroundColor Cyan
Write-Host "Path: $Path"
Write-Host "Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host ""

# Topic keyword library
$topicKeywords = @{
    "memory-system" = @("memory", "memor", "recall", "distill")
    "research-project" = @("research", "project", "study", "paper")
    "lig-conductivity" = @("lig", "conductivity", "graphene")
    "cnt-nanotube" = @("cnt", "nanotube", "carbon")
    "workflow" = @("workflow", "flow", "pipeline", "auto")
    "script-tool" = @("script", "tool", "utility", "powershell")
    "data-collection" = @("arxiv", "medium", "collect", "monitor")
    "knowledge-graph" = @("knowledge", "graph", "network", "entity")
    "model-training" = @("model", "train", "gp", "prediction")
    "doc-index" = @("index", "link", "inventory", "catalog")
}

$topicDisplayNames = @{
    "memory-system" = "Memory System"
    "research-project" = "Research Projects"
    "lig-conductivity" = "LIG Conductivity"
    "cnt-nanotube" = "CNT Nanotubes"
    "workflow" = "Workflows"
    "script-tool" = "Scripts & Tools"
    "data-collection" = "Data Collection"
    "knowledge-graph" = "Knowledge Graph"
    "model-training" = "Model Training"
    "doc-index" = "Documentation Index"
}

# Stats
$stats = @{
    Scanned = 0
    Categorized = 0
    LinksGenerated = 0
}

$docTopics = @{}
$topicDocs = @{}

Write-Host "Scanning Markdown files..." -ForegroundColor Yellow

$mdFiles = Get-ChildItem -Path $Path -Filter "*.md" -Recurse -Exclude $OutputFile,"broken-links-report.md","link-heat-report.md"
$totalFiles = $mdFiles.Count

foreach ($file in $mdFiles) {
    $stats.Scanned++
    
    # Skip small files
    if ($file.Length -lt 100) { continue }
    
    $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
    if (-not $content) { continue }
    
    # Extract title
    $title = ""
    $firstLines = $content -split "`n" | Select-Object -First 5
    foreach ($line in $firstLines) {
        if ($line -match "^#+\s*(.+)") {
            $title = $matches[1].Trim()
            break
        }
    }
    
    if (-not $title) { $title = $file.BaseName }
    
    # Keyword matching
    $matchedTopics = @()
    $contentLower = $content.ToLower()
    
    foreach ($topic in $topicKeywords.Keys) {
        $keywords = $topicKeywords[$topic]
        foreach ($keyword in $keywords) {
            if ($contentLower -like "*$keyword*") {
                $matchedTopics += $topic
                break
            }
        }
    }
    
    if ($matchedTopics.Count -gt 0) {
        $stats.Categorized++
        
        # Get primary topic (most matches)
        $primaryTopic = $matchedTopics | Group-Object | Sort-Object Count -Descending | Select-Object -First 1 -ExpandProperty Name
        
        $docInfo = @{
            Path = $file.FullName.Replace($Path, "").TrimStart('\')
            Title = $title
            Topics = $matchedTopics
            PrimaryTopic = $primaryTopic
        }
        
        $docTopics[$file.BaseName] = $docInfo
        
        if (-not $topicDocs[$primaryTopic]) {
            $topicDocs[$primaryTopic] = @()
        }
        $topicDocs[$primaryTopic] += $docInfo
    }
    
    # Progress
    if ($stats.Scanned % 100 -eq 0) {
        Write-Progress -Activity "Scanning documents" -Status "$($stats.Scanned)/$totalFiles" -PercentComplete (($stats.Scanned / $totalFiles) * 100)
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Classification Results" -ForegroundColor Cyan
Write-Host "========================================"
Write-Host "Files scanned: $($stats.Scanned)"
Write-Host "Categorized: $($stats.Categorized)"
Write-Host "Topics: $($topicDocs.Count)"
Write-Host ""

# Generate report
$report = @"
# Auto-Link Classification Report

**Generated:** $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  
**Files scanned:** $($stats.Scanned)  
**Categorized:** $($stats.Categorized)  
**Topics:** $($topicDocs.Count)

---

## Topic Classification

"@

foreach ($topic in $topicDocs.Keys | Sort-Object) {
    $docs = $topicDocs[$topic]
    $displayName = $topicDisplayNames[$topic]
    $report += "### $displayName ($($docs.Count) docs)`n`n"
    $report += "| Doc | Title | Related Topics |`n"
    $report += "|------|------|----------------|`n"
    
    foreach ($doc in $docs | Select-Object -First 20) {
        $link = "[[$($doc.Path -replace '.md$','')]]"
        $relatedTopics = ($doc.Topics | Where-Object { $_ -ne $topic } | ForEach-Object { $topicDisplayNames[$_] }) -join ", "
        $report += "| $link | $($doc.Title) | $relatedTopics |`n"
        $stats.LinksGenerated++
    }
    
    if ($docs.Count -gt 20) {
        $report += "| ... | $($docs.Count - 20) more | ... |`n"
    }
    
    $report += "`n"
}

$report += @"

---

## Cross-Topic Link Suggestions

Documents with multiple topics should have cross-references:

"@

$multiTopicDocs = $docTopics.Values | Where-Object { $_.Topics.Count -gt 1 }
if ($multiTopicDocs.Count -gt 0) {
    $report += "| Doc | Topics | Suggested Links |`n"
    $report += "|------|--------|-----------------|`n"
    
    foreach ($doc in $multiTopicDocs | Select-Object -First 30) {
        $topics = ($doc.Topics | ForEach-Object { $topicDisplayNames[$_] }) -join ", "
        $suggestedLinks = ($doc.Topics | ForEach-Object { "[[$_]]" }) -join ", "
        $report += "| ``$($doc.Path)`` | $topics | $suggestedLinks |`n"
    }
} else {
    $report += "*No multi-topic documents found*"
}

$report += @"

---

## Next Steps

1. **Review classification** - Ensure topic assignment is accurate
2. **Add cross-topic links** - For multi-topic documents
3. **Update LINK_INDEX.md** - Add newly generated links
4. **Run broken link check** - Ensure all links are valid

---

*Auto-generated by auto-link-generator.ps1*
"@

if (-not $DryRun) {
    $reportPath = Join-Path $Path $OutputFile
    $report | Out-File -FilePath $reportPath -Encoding utf8
    Write-Host "Report saved: $reportPath" -ForegroundColor Green
} else {
    Write-Host "`n[DRY RUN] Report not saved" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Generated links: $($stats.LinksGenerated)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Done!" -ForegroundColor Cyan
