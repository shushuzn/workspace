#!/usr/bin/env pwsh
# Auto Link Index Updater - Auto update LINK_INDEX.md
# Usage: .\auto-link-index-updater.ps1 [-Path <dir>] [-DryRun]

param(
    [string]$Path = "D:\OpenClaw\workspace",
    [switch]$DryRun
)

Write-Host "Auto Link Index Updater" -ForegroundColor Cyan
Write-Host "Path: $Path"
Write-Host ""

$stats = @{
    NewLinks = 0
    Updated = 0
}

$linkIndex = Join-Path $Path "15-docs\LINK_INDEX.md"

if (-not (Test-Path $linkIndex)) {
    Write-Host "Error: LINK_INDEX.md not found" -ForegroundColor Red
    exit 1
}

Write-Host "Step 1: Scanning for new index files..." -ForegroundColor Yellow

# Find all README.md files that could be index files
$indexCandidates = Get-ChildItem -Path $Path -Filter "README.md" -Recurse |
    Where-Object { $_.FullName -notlike "*node_modules*" -and $_.FullName -notlike "*\.git*" }

$newLinks = @()

foreach ($file in $indexCandidates) {
    $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
    if (-not $content) { continue }
    
    # Check if it has internal links
    if ($content -match '\[\[[^\]]+\]\]') {
        $relPath = $file.FullName.Replace($Path, "").TrimStart('\') -replace 'README.md$','' -replace '\\README$',''
        $relPath = $relPath.TrimEnd('/')
        
        # Check if already in LINK_INDEX.md
        $linkIndexContent = Get-Content $linkIndex -Raw
        if ($linkIndexContent -notlike "*[[$relPath]]*" -and $linkIndexContent -notlike "*[[$relPath/README]]*") {
            $newLinks += $relPath
            $stats.NewLinks++
        }
    }
}

Write-Host "Found $($newLinks.Count) new index files" -ForegroundColor Cyan

if ($newLinks.Count -gt 0) {
    Write-Host ""
    Write-Host "Step 2: Updating LINK_INDEX.md..." -ForegroundColor Yellow
    
    $newSection = "`n## New Indexes Added`n`n"
    $newSection += "Added on $(Get-Date -Format 'yyyy-MM-dd HH:mm'):`n`n"
    
    foreach ($link in $newLinks | Select-Object -First 20) {
        $newSection += "- [[$link]]`n"
    }
    
    if ($newLinks.Count -gt 20) {
        $newSection += "`n- ... and $($newLinks.Count - 20) more`n"
    }
    
    # Read current content
    $content = Get-Content $linkIndex -Raw
    
    # Find position to insert (before last update line)
    if ($content -match '\*last update\*:.*\n') {
        $insertPos = $content.LastIndexOf($matches[0]) + $matches[0].Length
        $newContent = $content.Insert($insertPos, "`n$newSection")
    } else {
        $newContent = $content + "`n$newSection"
    }
    
    if (-not $DryRun) {
        Set-Content -Path $linkIndex -Value $newContent -Encoding utf8
        $stats.Updated++
        Write-Host "LINK_INDEX.md updated" -ForegroundColor Green
    } else {
        Write-Host "[DRY RUN] Would update LINK_INDEX.md" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Results" -ForegroundColor Cyan
Write-Host "========================================"
Write-Host "New indexes found: $($stats.NewLinks)"
Write-Host "Files updated: $($stats.Updated)"
Write-Host ""

Write-Host "Done!" -ForegroundColor Cyan
