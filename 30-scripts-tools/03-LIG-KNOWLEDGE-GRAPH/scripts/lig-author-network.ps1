#!/usr/bin/env pwsh
# LIG Author Collaboration Network Analysis (Optimized)
# Extracts authors from papers, builds collaboration network, identifies research teams

param(
    [string]$PapersFile,
    [string]$OutputDir = "21-reports",
    [int]$MinCollaborations = 2,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

Write-Host "LIG Author Collaboration Network Analysis" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Load papers
if (!$PapersFile) {
    $latestPapers = Get-ChildItem -Path "40-arxiv" -Filter "lig-papers-*.json" | 
                    Sort-Object LastWriteTime -Descending | 
                    Select-Object -First 1
    if ($latestPapers) {
        $PapersFile = $latestPapers.FullName
        Write-Host "Using latest papers: $PapersFile" -ForegroundColor Green
    } else {
        Write-Host "ERROR: No papers file found" -ForegroundColor Red
        exit 1
    }
}

$papers = Get-Content $PapersFile | ConvertFrom-Json
Write-Host "Loaded $($papers.Count) papers" -ForegroundColor Green
Write-Host ""

# Data structures
$authors = @{}  # Author -> { papers, collaborator_count }
$collaborations = @{}  # "Author1|Author2" -> count

Write-Host "Extracting authors and collaborations..." -ForegroundColor Cyan

foreach ($paper in $papers) {
    $paperId = if ($paper.pmid) { "PMID:" + $paper.pmid } elseif ($paper.arxiv_id) { "arXiv:" + $paper.arxiv_id } else { $null }
    
    # Parse authors
    $authorList = @()
    if ($paper.authors) {
        $rawAuthors = $paper.authors -split ';|,'
        foreach ($rawAuthor in $rawAuthors) {
            $authorName = $rawAuthor.Trim()
            if ([string]::IsNullOrWhiteSpace($authorName)) { continue }
            
            $authorName = ($authorName -split '\s+' | Where-Object { $_ }) -join ' '
            
            if ($authorName) {
                $authorList += $authorName
                
                if (!$authors.ContainsKey($authorName)) {
                    $authors[$authorName] = @{
                        papers = @()
                        paper_count = 0
                    }
                }
                
                $authors[$authorName].papers += $paperId
                $authors[$authorName].paper_count++
            }
        }
    }
    
    # Build collaboration pairs
    for ($i = 0; $i -lt $authorList.Count; $i++) {
        for ($j = $i + 1; $j -lt $authorList.Count; $j++) {
            $author1 = $authorList[$i]
            $author2 = $authorList[$j]
            
            $key = if ($author1 -lt $author2) { "$author1|$author2" } else { "$author2|$author1" }
            
            if (!$collaborations.ContainsKey($key)) {
                $collaborations[$key] = 0
            }
            $collaborations[$key]++
        }
    }
}

Write-Host "  Extracted $($authors.Count) unique authors" -ForegroundColor Green
Write-Host "  Found $($collaborations.Count) collaboration pairs" -ForegroundColor Green
Write-Host ""

# Identify research teams using Union-Find (optimized)
Write-Host "Identifying research teams..." -ForegroundColor Cyan

# Union-Find data structure
$parent = @{}
$rank = @{}

foreach ($author in $authors.Keys) {
    $parent[$author] = $author
    $rank[$author] = 0
}

function Find-Root {
    param($x)
    if ($parent[$x] -ne $x) {
        $parent[$x] = Find-Root -x $parent[$x]  # Path compression
    }
    return $parent[$x]
}

function Union-Sets {
    param($x, $y)
    $rootX = Find-Root -x $x
    $rootY = Find-Root -x $y
    
    if ($rootX -eq $rootY) { return }
    
    # Union by rank
    if ($rank[$rootX] -lt $rank[$rootY]) {
        $parent[$rootX] = $rootY
    } elseif ($rank[$rootX] -gt $rank[$rootY]) {
        $parent[$rootY] = $rootX
    } else {
        $parent[$rootY] = $rootX
        $rank[$rootX]++
    }
}

# Union authors with >= MinCollaborations
$edgeCount = 0
foreach ($collab in $collaborations.GetEnumerator()) {
    if ($collab.Value -ge $MinCollaborations) {
        $parts = $collab.Key -split '\|'
        Union-Sets -x $parts[0] -y $parts[1]
        $edgeCount++
    }
}

Write-Host "  Processed $edgeCount collaboration edges" -ForegroundColor Green

# Group authors by root
$teamsMap = @{}
foreach ($author in $authors.Keys) {
    $root = Find-Root -x $author
    if (!$teamsMap.ContainsKey($root)) {
        $teamsMap[$root] = @()
    }
    $teamsMap[$root] += $author
}

# Convert to teams array
$teams = @()
foreach ($root in $teamsMap.Keys) {
    $members = $teamsMap[$root]
    if ($members.Count -ge 2) {
        $totalPapers = ($members | ForEach-Object { $authors[$_].paper_count }) | Measure-Object -Sum | Select-Object -ExpandProperty Sum
        $teams += @{
            members = $members
            size = $members.Count
            total_papers = $totalPapers
        }
    }
}

# Sort teams by size
$teams = $teams | Sort-Object -Property @{Expression = { $_.size }; Descending = $true }

Write-Host "  Identified $($teams.Count) research teams (min 2 members)" -ForegroundColor Green
Write-Host ""

# Calculate author metrics
Write-Host "Calculating author metrics..." -ForegroundColor Cyan

$authorMetrics = @()
foreach ($authorName in $authors.Keys) {
    $authorData = $authors[$authorName]
    
    # Count collaborators
    $collaboratorCount = 0
    $totalCollabs = 0
    foreach ($collab in $collaborations.GetEnumerator()) {
        $parts = $collab.Key -split '\|'
        if ($parts[0] -eq $authorName -or $parts[1] -eq $authorName) {
            $collaboratorCount++
            $totalCollabs += $collab.Value
        }
    }
    
    $avgCollabs = 0
    if ($collaboratorCount -gt 0) {
        $avgCollabs = [Math]::Round($totalCollabs / $collaboratorCount, 2)
    }
    
    $authorMetrics += [PSCustomObject]@{
        name = $authorName
        paper_count = $authorData.paper_count
        collaborator_count = $collaboratorCount
        avg_collaborations = $avgCollabs
        total_collaborations = $totalCollabs
    }
}

# Sort by paper count
$topAuthors = $authorMetrics | Sort-Object -Property @{Expression = { $_.paper_count }; Descending = $true } | Select-Object -First 20

Write-Host "  Top author: $($topAuthors[0].name) ($($topAuthors[0].paper_count) papers)" -ForegroundColor Green
Write-Host ""

# Generate network data for visualization
Write-Host "Generating network data..." -ForegroundColor Cyan

$networkNodes = @()
$networkLinks = @()

# Add nodes (top 50 authors by paper count)
$top50Authors = $authorMetrics | Sort-Object -Property paper_count -Descending | Select-Object -First 50
$authorIndex = @{}
for ($i = 0; $i -lt $top50Authors.Count; $i++) {
    $author = $top50Authors[$i]
    $authorIndex[$author.name] = $i
    $networkNodes += @{
        id = $author.name
        group = 1
        papers = $author.paper_count
        collaborators = $author.collaborator_count
    }
}

# Add links
foreach ($collab in $collaborations.GetEnumerator()) {
    $parts = $collab.Key -split '\|'
    $author1 = $parts[0]
    $author2 = $parts[1]
    
    if ($authorIndex.ContainsKey($author1) -and $authorIndex.ContainsKey($author2)) {
        $networkLinks += @{
            source = $authorIndex[$author1]
            target = $authorIndex[$author2]
            value = $collab.Value
        }
    }
}

$networkData = @{
    nodes = $networkNodes
    links = $networkLinks
}

Write-Host "  Network: $($networkNodes.Count) nodes, $($networkLinks.Count) links" -ForegroundColor Green
Write-Host ""

# Save outputs
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"

# Save network JSON
$networkFile = Join-Path $OutputDir "LIG-Author-Network-$timestamp.json"
$networkData | ConvertTo-Json -Depth 10 | Set-Content $networkFile -Encoding UTF8
Write-Host "Saved network: $networkFile" -ForegroundColor Green

# Save team data
$teamsFile = Join-Path $OutputDir "LIG-Research-Teams-$timestamp.json"
$teams | ConvertTo-Json -Depth 10 | Set-Content $teamsFile -Encoding UTF8
Write-Host "Saved teams: $teamsFile" -ForegroundColor Green

# Save author metrics
$metricsFile = Join-Path $OutputDir "LIG-Author-Metrics-$timestamp.json"
$authorMetrics | Sort-Object -Property paper_count -Descending | ConvertTo-Json -Depth 10 | Set-Content $metricsFile -Encoding UTF8
Write-Host "Saved metrics: $metricsFile" -ForegroundColor Green

# Generate markdown report
Write-Host ""
Write-Host "Generating report..." -ForegroundColor Cyan

$report = "# LIG Author Collaboration Network Analysis`n`n"
$report += "**Generated:** $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n"
$report += "**Papers Analyzed:** $($papers.Count)`n"
$report += "**Total Authors:** $($authors.Count)`n"
$report += "**Collaboration Pairs:** $($collaborations.Count)`n`n"

$report += "---`n`n"

$report += "## Executive Summary`n`n"
$report += "This analysis identified **$($authors.Count) unique authors** and **$($collaborations.Count) collaboration pairs** from $($papers.Count) LIG-related papers.`n`n"
$report += "**Key Findings:**`n"
$report += "- **$($teams.Count)** research teams identified (min 2 members with ≥$MinCollaborations collaborations)`n"
if ($teams.Count -gt 0) {
    $report += "- **Largest team:** $($teams[0].size) members`n"
}
$report += "- **Most prolific author:** $($topAuthors[0].name) ($($topAuthors[0].paper_count) papers)`n`n"

$report += "---`n`n"

$report += "## Top Authors by Publication Count`n`n"
$report += "| Rank | Author | Papers | Collaborators | Avg Collaborations |`n"
$report += "|------|--------|--------|---------------|-------------------|`n"
for ($i = 0; $i -lt $topAuthors.Count; $i++) {
    $author = $topAuthors[$i]
    $report += "| $($i + 1) | $($author.name) | $($author.paper_count) | $($author.collaborator_count) | $($author.avg_collaborations) |`n"
}
$report += "`n"

$report += "---`n`n"

$report += "## Research Teams`n`n"
$report += "Teams are identified as connected components in the collaboration network (authors with ≥$MinCollaborations joint papers).`n`n"

$report += "### Top 10 Research Teams by Size`n`n"
$report += "| Rank | Team Size | Total Papers | Members |`n"
$report += "|------|-----------|--------------|---------|`n"

$maxTeams = [Math]::Min(10, $teams.Count)
for ($i = 0; $i -lt $maxTeams; $i++) {
    $team = $teams[$i]
    $members = ($team.members | Select-Object -First 5) -join ", "
    if ($team.members.Count -gt 5) {
        $members += "..."
    }
    $report += "| $($i + 1) | $($team.size) | $($team.total_papers) | $members |`n"
}
$report += "`n"

$report += "---`n`n"

$report += "## Collaboration Network Statistics`n`n"
$report += "| Metric | Value |`n"
$report += "|--------|-------|`n"
$report += "| Total Authors | $($authors.Count) |`n"
$report += "| Total Papers | $($papers.Count) |`n"
$report += "| Collaboration Pairs | $($collaborations.Count) |`n"
$report += "| Research Teams | $($teams.Count) |`n"

$totalPapers = ($authors.Values | ForEach-Object { $_.paper_count }) | Measure-Object -Sum | Select-Object -ExpandProperty Sum
$avgPapers = [Math]::Round($totalPapers / $authors.Count, 2)
$report += "| Avg Papers/Author | $avgPapers |`n"

if ($collaborations.Count -gt 0) {
    $maxCollabs = ($collaborations.Values | Measure-Object -Maximum).Maximum
    $topCollabPair = $collaborations.GetEnumerator() | Where-Object { $_.Value -eq $maxCollabs } | Select-Object -First 1
    $report += "| Most Frequent Collaboration | $(if ($topCollabPair) { $topCollabPair.Key -replace '\|', ' & ' } else { 'N/A' }) ($maxCollabs papers) |`n"
}
$report += "`n"

$report += "---`n`n"

$report += "## Methodology`n`n"
$report += "### Data Extraction`n"
$report += "- Authors extracted from PubMed and arXiv paper metadata`n"
$report += "- Names normalized (extra spaces removed)`n"
$report += "- Collaboration pairs identified from co-authorship`n`n"

$report += "### Team Identification`n"
$report += "- Union-Find (Disjoint Set Union) algorithm`n"
$report += "- Path compression + union by rank for O(αn) efficiency`n"
$report += "- Minimum $MinCollaborations joint papers required for team edge`n"
$report += "- Teams with ≥2 members reported`n`n"

$report += "### Metrics`n"
$report += "- **Paper Count**: Total papers authored`n"
$report += "- **Collaborator Count**: Unique co-authors`n"
$report += "- **Avg Collaborations**: Average joint papers per collaborator`n`n"

$report += "---`n`n"

$report += "## Data Files`n`n"
$report += "- **Network Data:** $(Split-Path $networkFile -Leaf)`n"
$report += "- **Research Teams:** $(Split-Path $teamsFile -Leaf)`n"
$report += "- **Author Metrics:** $(Split-Path $metricsFile -Leaf)`n`n"

$report += "Generated by LIG Author Network Analysis Script`n"

$reportFile = Join-Path $OutputDir "LIG-Author-Network-Analysis-$timestamp.md"
$report | Set-Content $reportFile -Encoding UTF8
Write-Host "Saved report: $reportFile" -ForegroundColor Green

Write-Host ""
Write-Host "Done!" -ForegroundColor Green

return @{
    success = $true
    authors = $authors.Count
    collaborations = $collaborations.Count
    teams = $teams.Count
    top_author = $topAuthors[0].name
    network_file = $networkFile
    teams_file = $teamsFile
    metrics_file = $metricsFile
    report_file = $reportFile
}
