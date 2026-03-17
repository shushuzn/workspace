# Obsidian Sync - Watch Mode (No Admin Required)
# Monitors file changes and syncs every 30 minutes

$ErrorActionPreference = "Continue"

$WorkspacePath = "D:\OpenClaw\workspace"
$VaultPath = "D:\obsidian\Vault"
$IntervalMinutes = 30

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Obsidian Sync Watch Mode" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Interval: Every $IntervalMinutes minutes"
Write-Host "Press Ctrl+C to stop"
Write-Host ""

function Sync-Files {
    $filesCopied = 0
    
    # Sync directories
    $mappings = @(
        @{Src="memory"; Dst="memory"},
        @{Src="Medium"; Dst="Medium"},
        @{Src="knowledge-graph"; Dst="knowledge-graph"},
        @{Src="reports"; Dst="reports"}
    )
    
    foreach ($map in $mappings) {
        $src = Join-Path $WorkspacePath $map.Src
        $dst = Join-Path $VaultPath $map.Dst
        
        if (Test-Path $src) {
            $files = Get-ChildItem -Path $src -Recurse -File -Include *.md,*.json,*.yaml,*.txt,*.graphml,*.mmd,*.html
            foreach ($file in $files) {
                $rel = $file.FullName.Substring($src.Length).TrimStart('\')
                $target = Join-Path $dst $rel
                $targetDir = Split-Path $target -Parent
                
                if (-not (Test-Path $targetDir)) {
                    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
                }
                
                $needsUpdate = $true
                if (Test-Path $target) {
                    if ((Get-Item $file).LastWriteTime -le (Get-Item $target).LastWriteTime) {
                        $needsUpdate = $false
                    }
                }
                
                if ($needsUpdate) {
                    Copy-Item -Path $file.FullName -Destination $target -Force
                    $filesCopied++
                }
            }
        }
    }
    
    # Sync MEMORY.md
    $memSrc = Join-Path $WorkspacePath "MEMORY.md"
    $memDst = Join-Path $VaultPath "MEMORY.md"
    if (Test-Path $memSrc) {
        Copy-Item -Path $memSrc -Destination $memDst -Force
        $filesCopied++
    }
    
    return $filesCopied
}

# Initial sync
Write-Host "Initial sync..." -ForegroundColor Green
$copied = Sync-Files
Write-Host "Synced: $copied files" -ForegroundColor Green
Write-Host ""

# Continuous sync
while ($true) {
    $nextTime = (Get-Date).AddMinutes($IntervalMinutes)
    Write-Host "Next sync: $($nextTime.ToString('HH:mm:ss'))" -ForegroundColor Gray
    
    Start-Sleep -Seconds ($IntervalMinutes * 60)
    
    Write-Host "Syncing..." -ForegroundColor Green
    $copied = Sync-Files
    Write-Host "Synced: $copied files" -ForegroundColor Green
}
