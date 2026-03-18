# LIG 研究团队监控脚本
# 每周一 9AM 执行，检查 Tour 组和叶汝权组新论文

$ErrorActionPreference = "Continue"

# PubMed 搜索 URL
$tourUrl = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=`"Tour+JM`"[Author]+AND+`"laser+induced+graphene`"&retmax=10&sort=publication+date"
$yeUrl = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=`"Ye+R`"[Author]+AND+`"laser+induced+graphene`"&retmax=10&sort=publication+date"

# 输出文件
$pmidFile = "D:\OpenClaw\workspace\13-memory\lig-team-pmids.txt"
$logFile = "D:\OpenClaw\workspace\30-scripts\lig-team-monitor.log"

# 获取已记录 PMID
$existingPMIDs = @()
if (Test-Path $pmidFile) {
    $existingPMIDs = Get-Content $pmidFile | Where-Object { $_ -match '^\d+$' }
}

Write-Host "=== LIG Team Monitor - $(Get-Date -Format 'yyyy-MM-dd HH:mm') ===" | Tee-Object -FilePath $logFile
Write-Host "Existing PMIDs: $($existingPMIDs.Count)" | Tee-Object -Append -FilePath $logFile

# Fetch Tour group latest PMIDs
try {
    $tourResult = Invoke-RestMethod $tourUrl -TimeoutSec 30
    $tourPMIDs = $tourResult.eSearchResult.IdList
    Write-Host "Tour group: $($tourPMIDs.Count) papers" | Tee-Object -Append -FilePath $logFile
} catch {
    Write-Host "[ERROR] Tour group search failed: $_" | Tee-Object -Append -FilePath $logFile
    $tourPMIDs = @()
}

# Fetch Ye group latest PMIDs
try {
    $yeResult = Invoke-RestMethod $yeUrl -TimeoutSec 30
    $yePMIDs = $yeResult.eSearchResult.IdList
    Write-Host "Ye group: $($yePMIDs.Count) papers" | Tee-Object -Append -FilePath $logFile
} catch {
    Write-Host "[ERROR] Ye group search failed: $_" | Tee-Object -Append -FilePath $logFile
    $yePMIDs = @()
}

# Check for new papers
$newTour = $tourPMIDs | Where-Object { $_ -notin $existingPMIDs }
$newYe = $yePMIDs | Where-Object { $_ -notin $existingPMIDs }

$newCount = 0

if ($newTour) {
    Write-Host "`n[NEW] Tour group: $($newTour -join ', ')" | Tee-Object -Append -FilePath $logFile
    $newCount += $newTour.Count
    
    foreach ($pmid in $newTour) {
        try {
            $summaryUrl = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=$pmid&retmode=json"
            $summary = Invoke-RestMethod $summaryUrl -TimeoutSec 30
            $title = $summary.result.$pmid.title
            $journal = $summary.result.$pmid.fulljournalname
            $pubdate = $summary.result.$pmid.pubdate
            Write-Host "  - ($pmid) $title | $journal ($pubdate)" | Tee-Object -Append -FilePath $logFile
        } catch {
            Write-Host "  - ($pmid) [details fetch failed]" | Tee-Object -Append -FilePath $logFile
        }
    }
}

if ($newYe) {
    Write-Host "`n[NEW] Ye group: $($newYe -join ', ')" | Tee-Object -Append -FilePath $logFile
    $newCount += $newYe.Count
    
    foreach ($pmid in $newYe) {
        try {
            $summaryUrl = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=$pmid&retmode=json"
            $summary = Invoke-RestMethod $summaryUrl -TimeoutSec 30
            $title = $summary.result.$pmid.title
            $journal = $summary.result.$pmid.fulljournalname
            $pubdate = $summary.result.$pmid.pubdate
            Write-Host "  - ($pmid) $title | $journal ($pubdate)" | Tee-Object -Append -FilePath $logFile
        } catch {
            Write-Host "  - ($pmid) [details fetch failed]" | Tee-Object -Append -FilePath $logFile
        }
    }
}

if ($newCount -eq 0) {
    Write-Host "`n[OK] No new papers" | Tee-Object -Append -FilePath $logFile
} else {
    Write-Host "`n[INFO] Total $newCount new papers found" | Tee-Object -Append -FilePath $logFile
    Write-Host "[ACTION] Add to arxiv-daily queue: --source pubmed" | Tee-Object -Append -FilePath $logFile
}

# Update PMID records
$allPMIDs = ($existingPMIDs + $tourPMIDs + $yePMIDs) | Select-Object -Unique
$allPMIDs | Set-Content $pmidFile -Encoding UTF8

Write-Host "`n[OK] Updated PMID records: $($allPMIDs.Count) total" | Tee-Object -Append -FilePath $logFile
Write-Host "=== Monitor Complete ===`n" | Tee-Object -Append -FilePath $logFile
