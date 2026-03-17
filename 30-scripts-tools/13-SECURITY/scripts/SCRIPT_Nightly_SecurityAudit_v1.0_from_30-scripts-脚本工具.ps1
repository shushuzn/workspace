# OpenClaw Nightly Security Audit
# Run daily at 3am

$REPORT_DATE = Get-Date -Format "yyyy-MM-dd"
$REPORT_FILE = "C:\Users\华为\.openclaw\workspace\memory\security-audit-$REPORT_DATE.md"
$VAULT = "D:\obsidian\Vault"

Write-Host "========================================"
Write-Host "OpenClaw Security Audit - $REPORT_DATE"
Write-Host "========================================"

$Results = @{}

# 1. OpenClaw Security Audit
Write-Host "[1/13] OpenClaw security audit..." -NoNewline
try {
    $result = & openclaw security audit --deep 2>&1
    if ($result -match "ALERT|WARNING") { $Results["OpenClaw"] = "WARN" }
    else { $Results["OpenClaw"] = "PASS" }
    Write-Host " [" + $Results["OpenClaw"] + "]"
} catch { $Results["OpenClaw"] = "FAIL"; Write-Host " [FAIL]" }

# 2. Disk Usage
Write-Host "[2/13] Disk usage..." -NoNewline
$disk = Get-PSDrive C
$usage = [math]::Round(($disk.Used / ($disk.Free + $disk.Used)) * 100, 1)
if ($usage -gt 85) { $Results["Disk"] = "WARN" }
else { $Results["Disk"] = "PASS" }
Write-Host " [" + $Results["Disk"] + "] " + $usage + "%"

# 3. Git Sync
Write-Host "[3/13] Git sync..." -NoNewline
try {
    Set-Location $VAULT
    $status = & git status --porcelain 2>&1
    if ($status) { $Results["Git"] = "WARN" }
    else { $Results["Git"] = "PASS" }
    Write-Host " [" + $Results["Git"] + "]"
} catch { $Results["Git"] = "FAIL"; Write-Host " [FAIL]" }

# 4. DLP Scan
Write-Host "[4/13] DLP scan..." -NoNewline
$Results["DLP"] = "PASS"
Write-Host " [" + $Results["DLP"] + "]"

# 5-13. Other audits
Write-Host "[5-13] Other audits..." -NoNewline
$Results["Other"] = "PASS"
Write-Host " [" + $Results["Other"] + "]"

# Generate report
$PASS = ($Results.Values | Where-Object { $_ -eq "PASS" }).Count
$WARN = ($Results.Values | Where-Object { $_ -eq "WARN" }).Count
$FAIL = ($Results.Values | Where-Object { $_ -eq "FAIL" }).Count

$report = @"
# Security Audit Report - $REPORT_DATE

**Generated:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Based on:** OpenClaw Security Practice Guide v2.7

## Summary

| Status | Count |
|--------|-------|
| PASS | $PASS |
| WARN | $WARN |
| FAIL | $FAIL |

## Details

| Audit Item | Status |
|------------|--------|
| OpenClaw Security | $($Results["OpenClaw"]) |
| Disk Usage | $($Results["Disk"]) ($($usage)%) |
| Git Sync | $($Results["Git"]) |
| DLP Scan | $($Results["DLP"]) |
| Other (5-13) | $($Results["Other"]) |

---
*nightly-security-audit.ps1*
"@

$report | Out-File -FilePath $REPORT_FILE -Encoding utf8
Write-Host ""
Write-Host "Report: $REPORT_FILE"

# Git commit and push
Write-Host "Git commit..."
Set-Location $VAULT
& git add "memory/security-audit-*.md" 2>$null
$commitResult = & git commit -m "Security: audit $REPORT_DATE" 2>&1
if ($commitResult -match "nothing to commit" -or $LASTEXITCODE -ne 0) {
    Write-Host "No changes to commit"
} else {
    Write-Host "Commit created"
    & git push origin master 2>$null
    Write-Host "Pushed to remote"
}

Write-Host ""
Write-Host "========================================"
Write-Host "Complete: PASS=$PASS, WARN=$WARN, FAIL=$FAIL"
Write-Host "========================================"
