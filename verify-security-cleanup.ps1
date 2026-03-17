#!/usr/bin/env pwsh
# Verify no sensitive files in Git history
# Usage: .\verify-security-cleanup.ps1

$ErrorActionPreference = "Stop"

Write-Host "=================================================="
Write-Host "[Security Audit] Checking for sensitive files"
Write-Host "=================================================="

# Check Git history for .env files
Write-Host "`nChecking Git history..."
$gitLog = git log --all --oneline --name-only 2>$null
$envFiles = $gitLog | Select-String -Pattern "^\.env$|^41-medium/\.env$"

if ($envFiles) {
    Write-Host "  WARNING: Found .env references in history:" -ForegroundColor Yellow
    $envFiles | ForEach-Object { Write-Host "    $_" }
} else {
    Write-Host "  PASS: No .env files in history" -ForegroundColor Green
}

# Check current branch
Write-Host "`nChecking current branch..."
$currentEnv = git ls-files | Select-String -Pattern "^\.env$"
if ($currentEnv) {
    Write-Host "  FAIL: Found .env in current branch" -ForegroundColor Red
} else {
    Write-Host "  PASS: No .env in current branch" -ForegroundColor Green
}

Write-Host "`n=================================================="
Write-Host "[Security Audit] Complete"
Write-Host "=================================================="
