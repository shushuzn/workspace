# Medium Archive Full Verification Script
param(
    [string]$ArchivePath = "D:\obsidian\Vault\Medium\Archive",
    [string]$ReportPath = "D:\obsidian\Vault\Medium\Reports\full-verification-report.md"
)

$ErrorActionPreference = "Continue"

Write-Host "=== Medium Archive Verification ===" -ForegroundColor Cyan

$totalFiles = 0
$validFiles = 0
$invalidFiles = @()
$emptyFiles = @()
$missingFrontmatter = @()

$folderStats = @{}

Get-ChildItem -Path $ArchivePath -Directory | ForEach-Object {
    $folderName = $_.Name
    $folderPath = $_.FullName
    Write-Host "[$folderName] Scanning..." -ForegroundColor Yellow
    
    $files = Get-ChildItem -Path $folderPath -Filter "*.md"
    $folderCount = $files.Count
    $folderValid = 0
    $folderInvalid = @()
    
    Write-Host "  Found $folderCount files" -ForegroundColor Gray
    
    foreach ($file in $files) {
        $totalFiles++
        $fileName = $file.Name
        
        try {
            $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8
            $lines = Get-Content -Path $file.FullName -Encoding UTF8
            
            if ([string]::IsNullOrWhiteSpace($content)) {
                $emptyFiles += $fileName
                $folderInvalid += $fileName
                Write-Host "  EMPTY: $fileName" -ForegroundColor Red
                continue
            }
            
            $hasFrontmatter = $lines[0].Trim() -eq "---"
            if (-not $hasFrontmatter) {
                $missingFrontmatter += $fileName
                $folderInvalid += $fileName
                Write-Host "  NO-FM: $fileName" -ForegroundColor Orange
                continue
            }
            
            $endMarkers = ($lines | Where-Object { $_.Trim() -eq "---" }).Count
            if ($endMarkers -lt 2) {
                $missingFrontmatter += $fileName
                $folderInvalid += $fileName
                Write-Host "  BAD-FM: $fileName" -ForegroundColor Orange
                continue
            }
            
            $validFiles++
            Write-Host "  OK: $fileName" -ForegroundColor Green
            
        } catch {
            $invalidFiles += $fileName
            $folderInvalid += $fileName
            Write-Host "  ERROR: $fileName - $_" -ForegroundColor Red
        }
    }
    
    $folderStats[$folderName] = @{ Total = $folderCount; Valid = $validFiles; Invalid = $folderInvalid.Count }
    Write-Host ""
}

$passRate = [math]::Round($validFiles / $totalFiles * 100, 2)

Write-Host "=== Summary ===" -ForegroundColor Cyan
Write-Host "Total: $totalFiles | Valid: $validFiles | Invalid: $($invalidFiles.Count)"
Write-Host "Pass Rate: $passRate%"

if ($validFiles -eq $totalFiles) {
    Write-Host "ALL FILES VERIFIED!" -ForegroundColor Green
} else {
    Write-Host "Check report: $ReportPath" -ForegroundColor Yellow
}
