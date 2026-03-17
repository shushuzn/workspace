#!/usr/bin/env pwsh
# Test Medium collection with timeout
# Usage: .\test-medium-collection.ps1

Write-Host "Testing Medium collection..." -ForegroundColor Cyan

$timeout = 30  # seconds
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

try {
    # Test 1: Check if medium-watcher CLI exists
    Write-Host "`n[Test 1] Checking medium-watcher CLI..." -ForegroundColor Yellow
    $cli = Get-Command "medium-watcher" -ErrorAction SilentlyContinue
    if ($cli) {
        Write-Host "  OK: medium-watcher found" -ForegroundColor Green
    } else {
        Write-Host "  FAIL: medium-watcher not found" -ForegroundColor Red
        Write-Host "  Hint: Try 'npm install -g medium-watcher' or use Python script"
    }
    
    # Test 2: Check Python script
    Write-Host "`n[Test 2] Checking Python script..." -ForegroundColor Yellow
    $scriptPath = "D:\npm-global\node_modules\openclaw\skills\medium-watcher\medium_watcher.py"
    if (Test-Path $scriptPath) {
        Write-Host "  OK: Script found at $scriptPath" -ForegroundColor Green
    } else {
        Write-Host "  FAIL: Script not found" -ForegroundColor Red
    }
    
    # Test 3: Check output directory
    Write-Host "`n[Test 3] Checking output directory..." -ForegroundColor Yellow
    $outputDir = "D:\OpenClaw\workspace\41-medium"
    if (Test-Path $outputDir) {
        Write-Host "  OK: Directory exists" -ForegroundColor Green
        $fileCount = (Get-ChildItem $outputDir -Filter "*.md").Count
        Write-Host "  Files: $fileCount markdown files"
    } else {
        Write-Host "  FAIL: Directory not found" -ForegroundColor Red
    }
    
    # Test 4: Check dependencies
    Write-Host "`n[Test 4] Checking Python dependencies..." -ForegroundColor Yellow
    $deps = @("requests", "beautifulsoup4", "feedparser")
    foreach ($dep in $deps) {
        $result = pip show $dep 2>&1 | Select-String "Name:"
        if ($result) {
            Write-Host "  OK: $dep installed" -ForegroundColor Green
        } else {
            Write-Host "  MISSING: $dep" -ForegroundColor Yellow
        }
    }
    
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}

$stopwatch.Stop()
Write-Host "`nTest completed in $($stopwatch.ElapsedMilliseconds / 1000.0) seconds" -ForegroundColor Cyan
