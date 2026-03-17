#!/usr/bin/env pwsh
# Auto Backlink Generator - 自动为文档添加反向链接
# 用法：.\auto-backlink-generator.ps1 [-Path <dir>] [-DryRun]

param(
    [string]$Path = "D:\OpenClaw\workspace",
    [switch]$DryRun,
    [switch]$Verbose
)

Write-Host "Auto Backlink Generator - 自动添加反向链接" -ForegroundColor Cyan
Write-Host "Path: $Path"
Write-Host "Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host ""

$stats = @{
    Scanned = 0
    FoundLinks = 0
    Updated = 0
}

$backlinks = @{}  # { target => @([source1, source2, ...]) }

Write-Host "Step 1: Scanning for links..." -ForegroundColor Yellow

$mdFiles = Get-ChildItem -Path $Path -Filter "*.md" -Recurse
$totalFiles = $mdFiles.Count
$linkPattern = '\[\[([^\]|]+)(?:\|[^\]]+)?\]\]'

foreach ($file in $mdFiles) {
    $stats.Scanned++
    
    # Skip small files and reports
    if ($file.Length -lt 100) { continue }
    if ($file.Name -like "*-report.md" -or $file.Name -like "auto-*") { continue }
    
    $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
    if (-not $content) { continue }
    
    $links = [regex]::Matches($content, $linkPattern)
    $sourcePath = $file.FullName.Replace($Path, "").TrimStart('\') -replace '.md$',''
    
    foreach ($link in $links) {
        $stats.FoundLinks++
        $target = $link.Groups[1].Value.Trim()
        
        # Skip external links
        if ($target -match '^(http|https|mailto:)') { continue }
        
        # Normalize target
        $normalizedTarget = $target -replace '/README$','' -replace '\.md$',''
        
        if (-not $backlinks.ContainsKey($normalizedTarget)) {
            $backlinks[$normalizedTarget] = @()
        }
        $backlinks[$normalizedTarget] += $sourcePath
    }
    
    # Progress
    if ($stats.Scanned % 100 -eq 0) {
        Write-Progress -Activity "Scanning for links" -Status "$($stats.Scanned)/$totalFiles" -PercentComplete (($stats.Scanned / $totalFiles) * 100)
    }
}

Write-Host ""
Write-Host "Found $($backlinks.Count) documents with incoming links" -ForegroundColor Cyan
Write-Host "Total links found: $($stats.FoundLinks)" -ForegroundColor Cyan
Write-Host ""

Write-Host "Step 2: Adding backlinks to documents..." -ForegroundColor Yellow

$backlinkSection = @"

---

## 🔙 Backlinks

**Documents linking here:**
"@

foreach ($target in $backlinks.Keys) {
    $sources = $backlinks[$target]
    
    # Find target file
    $possiblePaths = @(
        (Join-Path $Path "$target.md"),
        (Join-Path $Path "$target/README.md")
    )
    
    $targetFile = $null
    foreach ($p in $possiblePaths) {
        if (Test-Path $p -PathType Leaf) {
            $targetFile = $p
            break
        }
    }
    
    if (-not $targetFile) { continue }
    
    $content = Get-Content $targetFile -Raw -ErrorAction SilentlyContinue
    if (-not $content) { continue }
    
    # Check if backlink section already exists
    if ($content -match '## 🔙') {
        if ($Verbose) {
            Write-Host "  Skip (exists): $target" -ForegroundColor Gray
        }
        continue
    }
    
    # Generate backlink list
    $backlinkList = ""
    foreach ($source in $sources | Select-Object -Unique | Select-Object -First 20) {
        $sourceName = Split-Path $source -Leaf
        $backlinkList += "`n- [[$source]] - $sourceName"
    }
    
    if ($sources.Count -gt 20) {
        $backlinkList += "`n- ... and $($sources.Count - 20) more"
    }
    
    $newContent = $content + $backlinkSection + $backlinkList + "`n"
    
    if (-not $DryRun) {
        Set-Content -Path $targetFile -Value $newContent -Encoding utf8
        $stats.Updated++
        
        if ($Verbose) {
            Write-Host "  Updated: $target ($($sources.Count) backlinks)" -ForegroundColor Green
        }
    } else {
        Write-Host "  Would update: $target ($($sources.Count) backlinks)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Results" -ForegroundColor Cyan
Write-Host "========================================"
Write-Host "Files scanned: $($stats.Scanned)"
Write-Host "Links found: $($stats.FoundLinks)"
Write-Host "Documents with incoming links: $($backlinks.Count)"
Write-Host "Files updated: $($stats.Updated)"
Write-Host ""

if ($DryRun) {
    Write-Host "[DRY RUN] No files were modified" -ForegroundColor Yellow
} else {
    Write-Host "Backlinks added successfully!" -ForegroundColor Green
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Cyan
