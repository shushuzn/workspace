# arXiv Lite Collector - PowerShell
param([string]$Date = "2026-03-06")

Write-Host "arXiv Collect: $Date" -ForegroundColor Cyan

$OutputDir = "D:\OpenClaw\workspace\40-arxiv\daily\$Date"
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

$categories = @("cs.AI", "cs.LG", "cs.CL")
$allPapers = @()

foreach ($cat in $categories) {
    Write-Host "Fetching $cat..." -ForegroundColor Yellow
    $url = "http://export.arxiv.org/api/query?search_query=cat:$cat&start=0&max_results=5&sortBy=submittedDate&sortOrder=descending"
    
    try {
        $response = Invoke-WebRequest -Uri $url -TimeoutSec 30 -UseBasicParsing
        $xml = [xml]$response.Content
        
        foreach ($entry in $xml.feed.entry) {
            $allPapers += @{
                title = $entry.title -replace "`n", " "
                category = $cat
                published = $entry.published
                id = $entry.id
            }
        }
        Write-Host "  OK: $($xml.feed.entry.Count) papers" -ForegroundColor Green
    } catch {
        Write-Host "  Error: $_" -ForegroundColor Red
    }
}

if ($allPapers.Count -gt 0) {
    $jsonPath = Join-Path $OutputDir "arxiv-$Date.json"
    $allPapers | ConvertTo-Json -Depth 3 | Out-File -FilePath $jsonPath -Encoding utf8
    Write-Host "Saved: $jsonPath ($($allPapers.Count) papers)" -ForegroundColor Green
} else {
    Write-Host "No papers found" -ForegroundColor Yellow
}

Write-Host "Done!" -ForegroundColor Cyan
