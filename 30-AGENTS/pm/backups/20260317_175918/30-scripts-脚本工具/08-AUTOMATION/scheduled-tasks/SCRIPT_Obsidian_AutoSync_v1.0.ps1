# Obsidian Auto Sync Script
# Sync OpenClaw workspace files to Obsidian Vault

param(
    [switch]$Verbose,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

# Configuration
$WorkspacePath = "D:\OpenClaw\workspace"
$VaultPath = "D:\obsidian\Vault"

# Stats
$FilesCopied = 0
$FilesSkipped = 0

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Obsidian Auto Sync" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Workspace: $WorkspacePath"
Write-Host "Vault: $VaultPath"
Write-Host ""

# Validate Vault path
if (-not (Test-Path $VaultPath)) {
    Write-Host "ERROR: Vault not found: $VaultPath" -ForegroundColor Red
    exit 1
}

# Sync function
function Sync-Folder {
    param($Src, $Dst)
    $srcPath = Join-Path $WorkspacePath $Src
    $dstPath = Join-Path $VaultPath $Dst
    
    if (-not (Test-Path $srcPath)) {
        Write-Host "SKIP: $Src (not found)" -ForegroundColor Yellow
        return
    }
    
    Write-Host "SYNC: $Src -> $Dst" -ForegroundColor Green
    
    $files = Get-ChildItem -Path $srcPath -Recurse -File -Include *.md,*.json,*.yaml,*.txt,*.graphml,*.mmd,*.html
    foreach ($file in $files) {
        $relPath = $file.FullName.Substring($srcPath.Length).TrimStart('\')
        $targetFile = Join-Path $dstPath $relPath
        $targetDir = Split-Path $targetFile -Parent
        
        if (-not (Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        
        $needsUpdate = $true
        if (Test-Path $targetFile) {
            $srcTime = (Get-Item $file.FullName).LastWriteTime
            $dstTime = (Get-Item $targetFile).LastWriteTime
            if ($srcTime -le $dstTime) {
                $needsUpdate = $false
                $script:FilesSkipped++
            }
        }
        
        if ($needsUpdate) {
            Copy-Item -Path $file.FullName -Destination $targetFile -Force
            Write-Host "  COPY: $relPath" -ForegroundColor Gray
            $script:FilesCopied++
        }
    }
}

# Execute sync
Sync-Folder -Src "memory" -Dst "memory"
Sync-Folder -Src "Medium" -Dst "Medium"
Sync-Folder -Src "knowledge-graph" -Dst "knowledge-graph"
Sync-Folder -Src "reports" -Dst "reports"

# Sync MEMORY.md
if (Test-Path (Join-Path $WorkspacePath "MEMORY.md")) {
    Copy-Item -Path (Join-Path $WorkspacePath "MEMORY.md") -Destination (Join-Path $VaultPath "MEMORY.md") -Force
    Write-Host "COPY: MEMORY.md" -ForegroundColor Gray
    $FilesCopied++
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Sync Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Copied: $FilesCopied files" -ForegroundColor Green
Write-Host "Skipped: $FilesSkipped files" -ForegroundColor Yellow
Write-Host ""
