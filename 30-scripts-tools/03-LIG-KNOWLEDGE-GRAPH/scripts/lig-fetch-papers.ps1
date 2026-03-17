#!/usr/bin/env pwsh
# LIG Paper Collection Script (Fixed v4 - Invoke-WebRequest + XML)

param(
    [string]$ConfigFile = "30-scripts/lig-update-config.yaml",
    [int]$DaysBack = 7,
    [switch]$Force,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

Write-Host "LIG Paper Collection" -ForegroundColor Cyan
Write-Host "====================" -ForegroundColor Cyan
Write-Host ""

$outputDir = "40-arxiv"
if (!(Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
}

$cacheFile = Join-Path $outputDir "lig-papers-cache.json"
$outputFile = Join-Path $outputDir ("lig-papers-" + (Get-Date -Format 'yyyyMMdd-HHmmss') + ".json")

$existingPapers = @()
if ((Test-Path $cacheFile) -and (!$Force)) {
    $existingPapers = Get-Content $cacheFile | ConvertFrom-Json
    Write-Host "Loaded cache: $($existingPapers.Count) papers" -ForegroundColor Green
}

$allPapers = @()

Write-Host ""
Write-Host "Searching PubMed..." -ForegroundColor Cyan

try {
    $query = "laser-induced+graphene+OR+LIG+graphene"
    $maxResults = 50
    
    $baseUrl = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    $searchUrl = $baseUrl + "esearch.fcgi?db=pubmed&term=" + $query + "&retmax=" + $maxResults + "&retmode=json"
    
    Write-Host "  URL: $searchUrl" -ForegroundColor Gray
    
    $searchResult = Invoke-RestMethod -Uri $searchUrl -Method Get
    
    if ($searchResult.esearchresult.idlist) {
        $pmids = $searchResult.esearchresult.idlist
        Write-Host "  Found $($pmids.Count) papers" -ForegroundColor Green
        
        $batchSize = 200
        $i = 0
        while ($i -lt $pmids.Count) {
            $end = [Math]::Min($i + $batchSize - 1, $pmids.Count - 1)
            $batch = $pmids[$i..$end]
            $idList = $batch -join ","
            
            $fetchUrl = $baseUrl + "esummary.fcgi?db=pubmed&id=" + $idList + "&retmode=json"
            $summaryResult = Invoke-RestMethod -Uri $fetchUrl -Method Get
            
            # PubMed returns result as object with PMIDs as keys
            # Need to iterate over the property values, not the object itself
            $pmidList = $summaryResult.result.psobject.Properties.Name | Where-Object { $_ -ne 'uids' }
            
            foreach ($pmid in $pmidList) {
                $doc = $summaryResult.result.$pmid
                
                $year = $null
                if ($doc.pubdate) {
                    try { $year = $doc.pubdate.Substring(0,4) } catch { $year = $null }
                }
                
                $authors = ""
                if ($doc.authors) {
                    $authors = ($doc.authors | ForEach-Object { $_.name }) -join "; "
                }
                
                $paper = [PSCustomObject]@{
                    source = "PubMed"
                    pmid = $doc.uid
                    title = $doc.title
                    authors = $authors
                    journal = $doc.fulljournalname
                    pubdate = $doc.pubdate
                    doi = if ($doc.articleids) { ($doc.articleids | Where-Object { $_.idtype -eq "doi" }).value } else { $null }
                    url = "https://pubmed.ncbi.nlm.nih.gov/" + $doc.uid + "/"
                    year = $year
                    collected_at = Get-Date -Format "yyyy-MM-ddTHH:mm:ssK"
                }
                
                $isDuplicate = $false
                foreach ($existing in $existingPapers) {
                    if ($existing.pmid -eq $paper.pmid) {
                        $isDuplicate = $true
                        break
                    }
                    if ($existing.title -and $paper.title) {
                        if ($existing.title.ToLower() -eq $paper.title.ToLower()) {
                            $isDuplicate = $true
                            break
                        }
                    }
                }
                
                if (!$isDuplicate) {
                    $allPapers += $paper
                    if ($Verbose) {
                        Write-Host "  + [" + $year + "] " + $paper.title.Substring(0, [Math]::Min(60, $paper.title.Length)) -ForegroundColor Green
                    }
                }
            }
            
            $i = $i + $batchSize
        }
    }
} catch {
    Write-Host "  Warning: PubMed search failed - $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Searching arXiv..." -ForegroundColor Cyan

try {
    $query = "laser-induced+graphene"
    $maxResults = 30
    
    $arxivUrl = "http://export.arxiv.org/api/query?search_query=all:" + $query + "&max_results=" + $maxResults + "&sortBy=submittedDate&sortOrder=descending"
    
    Write-Host "  URL: $arxivUrl" -ForegroundColor Gray
    Write-Host "  Fetching raw XML..." -ForegroundColor Gray
    
    # Use Invoke-WebRequest to get raw XML
    $response = Invoke-WebRequest -Uri $arxivUrl -UseBasicParsing
    Write-Host "  Response length: $($response.Content.Length) chars" -ForegroundColor Gray
    
    # Parse as XML
    $xml = [xml]$response.Content
    
    # Create namespace manager for Atom namespace
    $ns = New-Object System.Xml.XmlNamespaceManager($xml.NameTable)
    $ns.AddNamespace("atom", "http://www.w3.org/2005/Atom")
    
    # Get entries (arXiv uses Atom namespace)
    $entries = $xml.SelectNodes("//atom:entry", $ns)
    
    Write-Host "  Found $($entries.Count) papers" -ForegroundColor Green
    
    foreach ($entry in $entries) {
        # Get ID
        $idNode = $entry.SelectSingleNode("atom:id", $ns)
        $arxivId = $null
        if ($idNode) {
            $idParts = $idNode.InnerText -split '/'
            $arxivId = $idParts[-1]
        }
        
        # Get title
        $titleNode = $entry.SelectSingleNode("atom:title", $ns)
        $title = ""
        if ($titleNode) { $title = $titleNode.InnerText -replace '\s+', ' ' }
        
        # Get published date and year
        $publishedNode = $entry.SelectSingleNode("atom:published", $ns)
        $published = ""
        $year = $null
        if ($publishedNode) {
            $published = $publishedNode.InnerText
            try { $year = $published.Substring(0,4) } catch { $year = $null }
        }
        
        # Get updated
        $updatedNode = $entry.SelectSingleNode("atom:updated", $ns)
        $updated = ""
        if ($updatedNode) { $updated = $updatedNode.InnerText }
        
        # Get summary
        $summaryNode = $entry.SelectSingleNode("atom:summary", $ns)
        $summary = ""
        if ($summaryNode) { $summary = $summaryNode.InnerText -replace '\s+', ' ' }
        
        # Get authors
        $authorNodes = $entry.SelectNodes("atom:author/atom:name", $ns)
        $authors = ""
        if ($authorNodes) {
            $authors = ($authorNodes | ForEach-Object { $_.InnerText }) -join "; "
        }
        
        # Get categories
        $categoryNodes = $entry.SelectNodes("atom:category", $ns)
        $categories = ""
        if ($categoryNodes) {
            $categories = ($categoryNodes | ForEach-Object { $_.getAttribute("term") }) -join ", "
        }
        
        $paper = [PSCustomObject]@{
            source = "arXiv"
            arxiv_id = $arxivId
            title = $title
            authors = $authors
            published = $published
            updated = $updated
            summary = $summary
            categories = $categories
            url = if ($idNode) { $idNode.InnerText } else { $null }
            year = $year
            collected_at = Get-Date -Format "yyyy-MM-ddTHH:mm:ssK"
        }
        
        $isDuplicate = $false
        foreach ($existing in $existingPapers) {
            if ($existing.arxiv_id -eq $paper.arxiv_id) {
                $isDuplicate = $true
                break
            }
            if ($existing.title -and $paper.title) {
                if ($existing.title.ToLower() -eq $paper.title.ToLower()) {
                    $isDuplicate = $true
                    break
                }
            }
        }
        
        if (!$isDuplicate) {
            $allPapers += $paper
            if ($Verbose) {
                Write-Host "  + [" + $year + "] " + $title.Substring(0, [Math]::Min(60, $title.Length)) -ForegroundColor Green
            }
        }
    }
} catch {
    Write-Host "  Warning: arXiv search failed - $($_.Exception.Message)" -ForegroundColor Yellow
    if ($Verbose) {
        Write-Host "  Error details: $($_.Exception.InnerException.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Saving Results..." -ForegroundColor Cyan

if ($allPapers.Count -gt 0) {
    $updatedCache = $existingPapers + $allPapers
    $updatedCache | ConvertTo-Json -Depth 10 | Set-Content $cacheFile -Encoding UTF8
    Write-Host "  Updated cache: $($updatedCache.Count) papers" -ForegroundColor Green
    
    $allPapers | ConvertTo-Json -Depth 10 | Set-Content $outputFile -Encoding UTF8
    Write-Host "  Saved: $outputFile" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "Statistics:" -ForegroundColor Cyan
    Write-Host "  New papers: $($allPapers.Count)" -ForegroundColor Green
    
    $pubmedCount = 0
    $arxivCount = 0
    $withYear = 0
    foreach ($p in $allPapers) {
        if ($p.source -eq 'PubMed') { $pubmedCount++ }
        if ($p.source -eq 'arXiv') { $arxivCount++ }
        if ($p.year) { $withYear++ }
    }
    Write-Host "  PubMed: $pubmedCount" -ForegroundColor Green
    Write-Host "  arXiv: $arxivCount" -ForegroundColor Green
    Write-Host "  With year: $withYear" -ForegroundColor Green
    
    # Show year distribution
    $yearDist = @{}
    foreach ($p in $allPapers) {
        if ($p.year) {
            if (!$yearDist.ContainsKey($p.year)) { $yearDist[$p.year] = 0 }
            $yearDist[$p.year]++
        }
    }
    if ($yearDist.Count -gt 0) {
        Write-Host ""
        Write-Host "  Year distribution:" -ForegroundColor Cyan
        foreach ($year in $yearDist.Keys | Sort-Object) {
            Write-Host "    $year`: $($yearDist[$year])" -ForegroundColor Green
        }
    }
} else {
    Write-Host "  No new papers found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Green
