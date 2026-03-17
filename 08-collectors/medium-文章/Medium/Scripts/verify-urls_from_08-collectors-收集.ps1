# Medium Archive URL Verification Script v2
param(
    [string]$ArchivePath = "D:\obsidian\Vault\Medium\Archive",
    [string]$ReportPath = "D:\obsidian\Vault\Medium\Reports\url-verification-report.md"
)

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "=== URL Verification ===" -ForegroundColor Cyan

$allUrls = @()

Get-ChildItem -Path $ArchivePath -Recurse -Filter "*.md" | ForEach-Object {
    $content = Get-Content -Path $_.FullName -Raw -Encoding UTF8
    $urls = [regex]::Matches($content, 'https?://[^\s\)]+') | ForEach-Object { $_.Value.TrimEnd('.', ',', ';', ')') }
    $urls | Where-Object { $_ -and $_.StartsWith('http') } | ForEach-Object {
        $allUrls += @{ Url = $_; File = $_.Name }
    }
}

Write-Host "Found $($allUrls.Count) URLs" -ForegroundColor Green

$validCount = 0
$invalidCount = 0
$timeoutCount = 0

foreach ($item in $allUrls) {
    try {
        $response = Invoke-WebRequest -Uri $item.Url -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 400) {
            $validCount++
            Write-Host "[OK] $($item.Url)" -ForegroundColor Green
        } else {
            $invalidCount++
            Write-Host "[HTTP $($response.StatusCode)] $($item.Url)" -ForegroundColor Red
        }
    } catch {
        $timeoutCount++
        Write-Host "[ERR] $($item.Url)" -ForegroundColor Yellow
    }
}

$totalUrls = $allUrls.Count
$passRate = [math]::Round($validCount / $totalUrls * 100, 2)

Write-Host ""
Write-Host "=== Summary ===" -ForegroundColor Cyan
Write-Host "Total: $totalUrls | Valid: $validCount ($passRate%) | Invalid: $invalidCount | Timeout: $timeoutCount"

if ($passRate -ge 95) {
    Write-Host "URL verification PASSED!" -ForegroundColor Green
}
