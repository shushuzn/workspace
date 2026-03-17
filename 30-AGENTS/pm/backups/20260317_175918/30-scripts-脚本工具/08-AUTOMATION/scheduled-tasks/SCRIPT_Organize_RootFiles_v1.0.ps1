# Organize root files into folders

$files = @{
    # Config files -> 03-config
    ".flake8"        = "03-config"
    "mypy.ini"       = "03-config"
    "pyproject.toml" = "03-config"
    "requirements.txt" = "03-config"
    
    # Scripts -> 30-scripts
    "backup.sh"      = "30-scripts"
    "deploy.sh"      = "30-scripts"
    "stop.sh"        = "30-scripts"
    "organize_workspace.py" = "30-scripts"
    
    # Core docs -> 15-docs
    "AGENTS.md"      = "15-docs"
    "SOUL.md"        = "15-docs"
    "USER.md"        = "15-docs"
    "TOOLS.md"       = "15-docs"
    "IDENTITY.md"    = "15-docs"
    "READ.md"        = "15-docs"
    "README.md"      = "15-docs"
    "WORKSPACE-LAYOUT.md" = "15-docs"
    "REORGANIZATION-FINAL-REPORT.md" = "15-docs"
    
    # Memory files -> 13-memory
    "MEMORY.md"      = "13-memory"
    "HEARTBEAT.md"   = "13-memory"
}

$basePath = "D:\OpenClaw\workspace"

foreach ($file in $files.Keys) {
    $targetFolder = $files[$file]
    $sourcePath = Join-Path $basePath $file
    $destPath = Join-Path $basePath $targetFolder
    
    if (Test-Path $sourcePath) {
        Write-Host "Move: $file -> $targetFolder/" -ForegroundColor Cyan
        Move-Item -Path $sourcePath -Destination $destPath -Force
    } else {
        Write-Host "Not found: $file" -ForegroundColor Yellow
    }
}

Write-Host "`nDone! Root files organized." -ForegroundColor Green
