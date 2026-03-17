#!/usr/bin/env pwsh
# Install Git hooks from 01-CONFIG/git-hooks/ to .git/hooks/
# Run this after cloning or when hooks are updated

$hooksDir = Join-Path $PSScriptRoot "..\..\.git\hooks"
$sourceDir = Join-Path $PSScriptRoot "git-hooks"

Write-Host "=== Git Hooks Installer ===" -ForegroundColor Cyan
Write-Host ""

# Create hooks directory if not exists
if (!(Test-Path $hooksDir)) {
    New-Item -ItemType Directory -Path $hooksDir -Force | Out-Null
    Write-Host "✓ Created $hooksDir" -ForegroundColor Green
}

# Copy all hooks
$hookFiles = Get-ChildItem -Path $sourceDir -File
foreach ($hook in $hookFiles) {
    $dest = Join-Path $hooksDir $hook.Name
    Copy-Item -Path $hook.FullName -Destination $dest -Force
    Write-Host "✓ Installed: $($hook.Name)" -ForegroundColor Green
    
    # Make executable on Unix-like systems
    if ($env:OS -ne "Windows_NT") {
        chmod +x $dest 2>$null
    }
}

Write-Host ""
Write-Host "Hooks installed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Available hooks:" -ForegroundColor Cyan
Write-Host "  - pre-commit: Validates file placement (12-core directory structure)"
Write-Host "                Blocks report files, enforces SOUL.md for important info"
Write-Host ""
Write-Host "To uninstall: Remove files from .git/hooks/"
