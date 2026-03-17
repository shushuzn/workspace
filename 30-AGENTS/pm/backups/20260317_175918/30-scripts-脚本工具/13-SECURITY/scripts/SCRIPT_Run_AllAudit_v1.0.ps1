#!/usr/bin/env pwsh
# Run All Audit Scripts - 一键运行全部检查
# Usage: .\run-all-audit.ps1 [-Path <dir>] [-Verbose]

param(
    [string]$Path = "D:\OpenClaw\workspace",
    [switch]$Verbose
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Link Network Audit Suite" -ForegroundColor Cyan
Write-Host "  Running All Checks..." -ForegroundColor Cyan
Write-Host "========================================"
Write-Host ""
Write-Host "Path: $Path"
Write-Host "Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host ""

$startTime = Get-Date
$results = @{}

# 1. Broken Links Check
Write-Host "[1/5] Checking broken links..." -ForegroundColor Yellow
try {
    $output = & "$Path\30-scripts\check-broken-links.ps1" -Path $Path 2>&1
    if ($output -match "Broken links: (\d+)") {
        $results['BrokenLinks'] = $matches[1]
    }
    if ($output -match "Broken rate: ([\d.]+)%") {
        $results['BrokenRate'] = $matches[1]
    }
    Write-Host "  Done" -ForegroundColor Green
} catch {
    Write-Host "  Failed: $_" -ForegroundColor Red
    $results['BrokenLinks'] = "Error"
}
Write-Host ""

# 2. Link Heat Analysis
Write-Host "[2/5] Analyzing link heat..." -ForegroundColor Yellow
try {
    $output = & "$Path\30-scripts\analyze-link-heat.ps1" -Path $Path 2>&1
    if ($output -match "Total unique links: (\d+)") {
        $results['UniqueLinks'] = $matches[1]
    }
    if ($output -match "Total references: (\d+)") {
        $results['TotalRefs'] = $matches[1]
    }
    Write-Host "  Done" -ForegroundColor Green
} catch {
    Write-Host "  Failed: $_" -ForegroundColor Red
    $results['UniqueLinks'] = "Error"
}
Write-Host ""

# 3. Auto Backlink Generation
Write-Host "[3/5] Adding backlinks..." -ForegroundColor Yellow
try {
    $output = & "$Path\30-scripts\auto-backlink-generator.ps1" -Path $Path 2>&1
    if ($output -match "Files updated: (\d+)") {
        $results['BacklinksAdded'] = $matches[1]
    }
    Write-Host "  Done" -ForegroundColor Green
} catch {
    Write-Host "  Failed: $_" -ForegroundColor Red
    $results['BacklinksAdded'] = "Error"
}
Write-Host ""

# 4. Smart Recommendations
Write-Host "[4/5] Generating recommendations..." -ForegroundColor Yellow
try {
    $output = & "$Path\30-scripts\smart-link-recommender.ps1" -Path $Path 2>&1
    if ($output -match "Indexed (\d+) documents") {
        $results['IndexedDocs'] = $matches[1]
    }
    Write-Host "  Done" -ForegroundColor Green
} catch {
    Write-Host "  Failed: $_" -ForegroundColor Red
    $results['IndexedDocs'] = "Error"
}
Write-Host ""

# 5. Broken Link Fix Suggestions
Write-Host "[5/5] Generating fix suggestions..." -ForegroundColor Yellow
try {
    $output = & "$Path\30-scripts\broken-link-fixer.ps1" -Path $Path 2>&1
    $results['FixSuggestions'] = "Generated"
    Write-Host "  Done" -ForegroundColor Green
} catch {
    Write-Host "  Failed: $_" -ForegroundColor Red
    $results['FixSuggestions'] = "Error"
}
Write-Host ""

# Summary
$endTime = Get-Date
$duration = New-TimeSpan -Start $startTime -End $endTime

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Audit Summary" -ForegroundColor Cyan
Write-Host "========================================"
Write-Host ""
Write-Host "Duration: $($duration.Minutes)m $($duration.Seconds)s"
Write-Host ""

if ($results['BrokenLinks'] -ne "Error") {
    Write-Host "Broken Links: $($results['BrokenLinks'])" -ForegroundColor $(if ([int]$results['BrokenLinks'] -eq 0) { 'Green' } else { 'Yellow' })
}
if ($results['BrokenRate'] -ne $null) {
    Write-Host "Broken Rate: $($results['BrokenRate'])%" -ForegroundColor $(if ([float]$results['BrokenRate'] -lt 5) { 'Green' } else { 'Red' })
}
if ($results['UniqueLinks'] -ne "Error") {
    Write-Host "Unique Links: $($results['UniqueLinks'])" -ForegroundColor Cyan
}
if ($results['TotalRefs'] -ne "Error") {
    Write-Host "Total References: $($results['TotalRefs'])" -ForegroundColor Cyan
}
if ($results['BacklinksAdded'] -ne "Error") {
    Write-Host "Backlinks Added: $($results['BacklinksAdded'])" -ForegroundColor Green
}
if ($results['IndexedDocs'] -ne "Error") {
    Write-Host "Documents Indexed: $($results['IndexedDocs'])" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Reports generated:" -ForegroundColor Cyan
Write-Host "  - broken-links-report.md"
Write-Host "  - link-heat-report.md"
Write-Host "  - link-recommendations.md"
Write-Host "  - broken-link-fixes.md"
Write-Host ""
Write-Host "Done!" -ForegroundColor Green
