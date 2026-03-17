# 30-scripts Maintenance Script
# Usage: .\maintain.ps1 [-CleanCache] [-HealthCheck] [-GenerateStats] [-All]

param(
    [switch]$CleanCache,
    [switch]$HealthCheck,
    [switch]$GenerateStats,
    [switch]$All
)

$src = "D:\OpenClaw\workspace\30-scripts"

function Write-Step { param($msg) Write-Host "`n$msg" -ForegroundColor Cyan }
function Write-Success { param($msg) Write-Host "  OK $msg" -ForegroundColor Green }
function Write-Warn { param($msg) Write-Host "  WARN $msg" -ForegroundColor Yellow }

# Clean Python cache
function Clean-PythonCache {
    Write-Step "Cleaning Python cache..."
    $pycacheDirs = Get-ChildItem $src -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue
    $deletedCount = 0
    foreach($dir in $pycacheDirs) {
        try {
            Remove-Item -Path $dir.FullName -Recurse -Force -ErrorAction SilentlyContinue
            $deletedCount++
        } catch {}
    }
    Write-Success "Cleaned $deletedCount __pycache__ directories"
}

# Health check
function Health-Check {
    Write-Step "Running health check..."
    
    # Check README files
    $projects = Get-ChildItem $src -Directory -Filter "??-*"
    $readmeCount = 0
    foreach($proj in $projects) {
        $readme = Join-Path $proj.FullName "README.md"
        if (Test-Path $readme) {
            $readmeCount++
        } else {
            Write-Warn "$($proj.Name) missing README.md"
        }
    }
    $pct = [math]::Round($readmeCount/$projects.Count*100)
    Write-Success "README coverage: $readmeCount/$($projects.Count) projects ($pct%)"
    
    # Check large files
    $largeFiles = Get-ChildItem $src -Recurse -File | Where-Object { $_.Length -gt 10MB }
    if ($largeFiles.Count -gt 0) {
        Write-Warn "Found $($largeFiles.Count) large files (>10MB)"
    } else {
        Write-Success "No large files (>10MB)"
    }
    
    # Check __pycache__
    $pycacheDirs = Get-ChildItem $src -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue
    if ($pycacheDirs.Count -gt 0) {
        Write-Warn "Found $($pycacheDirs.Count) __pycache__ directories"
    } else {
        Write-Success "No __pycache__ directories"
    }
}

# Generate stats
function Generate-Stats {
    Write-Step "Generating project stats..."
    
    $projects = Get-ChildItem $src -Directory -Filter "??-*"
    
    Write-Host "`nProject Statistics:" -ForegroundColor Cyan
    foreach($proj in $projects) {
        $files = Get-ChildItem $proj.FullName -Recurse -File -ErrorAction SilentlyContinue
        $fileCount = $files.Count
        $totalSize = [math]::Round(($files | Measure-Object -Property Length -Sum).Sum / 1MB, 2)
        Write-Host "  $($proj.Name): $fileCount files, $totalSize MB" -ForegroundColor Gray
    }
    
    $allFiles = Get-ChildItem $src -Recurse -File -ErrorAction SilentlyContinue
    $totalCount = $allFiles.Count
    $totalSize = [math]::Round(($allFiles | Measure-Object -Property Length -Sum).Sum / 1MB, 2)
    Write-Host "`n  Total: $totalCount files, $totalSize MB" -ForegroundColor Yellow
}

# Main
if (-not $CleanCache -and -not $HealthCheck -and -not $GenerateStats -and -not $All) {
    Write-Host "`nUsage:" -ForegroundColor Yellow
    Write-Host "  .\maintain.ps1 -CleanCache     # Clean cache" -ForegroundColor Gray
    Write-Host "  .\maintain.ps1 -HealthCheck    # Health check" -ForegroundColor Gray
    Write-Host "  .\maintain.ps1 -GenerateStats  # Generate stats" -ForegroundColor Gray
    Write-Host "  .\maintain.ps1 -All            # Run all" -ForegroundColor Gray
    exit
}

if ($All) {
    Clean-PythonCache
    Health-Check
    Generate-Stats
} else {
    if ($CleanCache) { Clean-PythonCache }
    if ($HealthCheck) { Health-Check }
    if ($GenerateStats) { Generate-Stats }
}

Write-Host "`nDONE!" -ForegroundColor Green
