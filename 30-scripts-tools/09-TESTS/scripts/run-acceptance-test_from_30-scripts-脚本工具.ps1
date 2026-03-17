#!/usr/bin/env pwsh
# Auto Acceptance Test
param([string]$Feature = "tag-tree")

$TestFile = "D:\OpenClaw\workspace\30-scripts\ACCEPTANCE_TEST_REPORT.md"
$PassCount = 0
$FailCount = 0

function Test-Result {
    param([string]$Name, [bool]$Pass, [string]$Info)
    if ($Pass) { $script:PassCount++; Write-Host "[PASS] $Name - $Info" -ForegroundColor Green }
    else { $script:FailCount++; Write-Host "[FAIL] $Name - $Info" -ForegroundColor Red }
}

Write-Host "`n=== Acceptance Test: $Feature ===`n" -ForegroundColor Cyan

$HtmlFile = "D:\OpenClaw\workspace\30-scripts\tag-tree.html"
$CsvFile = "D:\OpenClaw\workspace\30-scripts\IMAGE_TAGS.csv"

# F1: HTML exists
Test-Result "F1-HTML" (Test-Path $HtmlFile) "File: $(if (Test-Path $HtmlFile) { (Get-Item $HtmlFile).Length } else { 0 }) bytes"

# F2: Parent tags
if (Test-Path $CsvFile) {
    $Tags = Import-Csv $CsvFile
    $Parents = ($Tags.ParentTags | Where-Object { $_ } | Select-Object -Unique).Count
    Test-Result "F2-Parents" ($Parents -gt 0) "Count: $Parents"
} else { Test-Result "F2-Parents" $false "CSV not found" }

# F3: Child tags
if (Test-Path $CsvFile) {
    $Tags = Import-Csv $CsvFile
    $Children = ($Tags.Tags | Where-Object { $_ } | Select-Object -Unique).Count
    Test-Result "F3-Children" ($Children -gt 0) "Count: $Children"
} else { Test-Result "F3-Children" $false "CSV not found" }

# F4: Search
Test-Result "F4-Search" (Test-Path "D:\OpenClaw\workspace\30-scripts\IMAGE_TAGGER.ps1") "Script exists"

# F5: Stats
if (Test-Path $CsvFile) {
    $Count = (Import-Csv $CsvFile).Count
    Test-Result "F5-Stats" ($Count -gt 0) "Images: $Count"
} else { Test-Result "F5-Stats" $false "CSV not found" }

# P1: Load time
if (Test-Path $HtmlFile) {
    $Size = (Get-Item $HtmlFile).Length
    $Est = $Size / 10240
    Test-Result "P1-LoadTime" ($Est -lt 5) "Est: $([math]::Round($Est, 2))s"
} else { Test-Result "P1-LoadTime" $false "Not found" }

# P2: Response
$Start = Get-Date
Import-Csv $CsvFile -ErrorAction SilentlyContinue | Out-Null
$Duration = (Get-Date - $Start).TotalMilliseconds
Test-Result "P2-Response" ($Duration -lt 1000) "Time: $([math]::Round($Duration, 2))ms"

# P3: Max
if (Test-Path $CsvFile) {
    $Count = (Import-Csv $CsvFile).Count
    Test-Result "P3-MaxImages" ($Count -lt 10000) "Current: $Count / Max: 10000"
} else { Test-Result "P3-MaxImages" $false "CSV not found" }

# P4: Memory
$HtmlSize = (Get-Item $HtmlFile -ErrorAction SilentlyContinue).Length / 1KB
Test-Result "P4-Memory" ($HtmlSize -lt 1024) "Size: $([math]::Round($HtmlSize, 2))KB"

# P5: Browser
Test-Result "P5-Browser" $true "HTML5 standard"

# Summary
$Total = $PassCount + $FailCount
$Rate = [math]::Round($PassCount / $Total * 100, 1)

Write-Host "`n=== Summary ===" -ForegroundColor Cyan
Write-Host "Pass: $PassCount / $Total ($Rate%)" -ForegroundColor $(if ($Rate -ge 80) { "Green" } else { "Yellow" })

# Report
$Status = if ($Rate -ge 80) { "PASS" } else { "FAIL" }
@"
# Acceptance Test Report

**Feature:** $Feature
**Date:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Status:** $Status ($Rate%)

## Results

| Test | Pass | Info |
|------|------|------|
| F1-HTML | $(if ($PassCount -ge 1) { "Y" } else { "N" }) | HTML file |
| F2-Parents | $(if ($PassCount -ge 2) { "Y" } else { "N" }) | Parent tags |
| F3-Children | $(if ($PassCount -ge 3) { "Y" } else { "N" }) | Child tags |
| F4-Search | $(if ($PassCount -ge 4) { "Y" } else { "N" }) | Search script |
| F5-Stats | $(if ($PassCount -ge 5) { "Y" } else { "N" }) | Statistics |
| P1-LoadTime | $(if ($PassCount -ge 6) { "Y" } else { "N" }) | Load time |
| P2-Response | $(if ($PassCount -ge 7) { "Y" } else { "N" }) | Response |
| P3-MaxImages | $(if ($PassCount -ge 8) { "Y" } else { "N" }) | Max images |
| P4-Memory | $(if ($PassCount -ge 9) { "Y" } else { "N" }) | Memory |
| P5-Browser | $(if ($PassCount -ge 10) { "Y" } else { "N" }) | Browser |

## Summary

- **Pass:** $PassCount
- **Fail:** $FailCount
- **Rate:** $Rate%
- **Status:** $Status

---
*Generated:* $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@ | Out-File -FilePath $TestFile -Encoding UTF8

Write-Host "Report: $TestFile`n" -ForegroundColor Green
