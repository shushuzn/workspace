#!/usr/bin/env pwsh
# LIG Opportunity Discovery System with Time Trend Analysis
# Analyzes knowledge graph to identify research gaps and opportunities with temporal trends

param(
    [string]$GraphFile = "12-knowledge-graph/lig-graph.json",
    [string]$PapersFile,
    [string]$OutputFile = "21-reports/LIG-Opportunity-Analysis-$(Get-Date -Format 'yyyyMMdd-HHmmss').md",
    [int]$MinOpportunities = 10,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

Write-Host "LIG Opportunity Discovery System (with Time Trends)" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

# Load graph
Write-Host "Loading knowledge graph..." -ForegroundColor Cyan
if (!(Test-Path $GraphFile)) {
    Write-Host "ERROR: Graph file not found: $GraphFile" -ForegroundColor Red
    exit 1
}

$graph = Get-Content $GraphFile | ConvertFrom-Json
Write-Host "  Loaded: $($graph.entities.Count) entities, $($graph.relations.Count) relations" -ForegroundColor Green

# Load papers for trend analysis
$papers = @()
if (!$PapersFile) {
    $latestPapers = Get-ChildItem -Path "40-arxiv" -Filter "lig-papers-*.json" | 
                    Sort-Object LastWriteTime -Descending | 
                    Select-Object -First 1
    if ($latestPapers) {
        $PapersFile = $latestPapers.FullName
        Write-Host "  Using papers: $PapersFile" -ForegroundColor Green
    }
}

if ($PapersFile -and (Test-Path $PapersFile)) {
    $papers = Get-Content $PapersFile | ConvertFrom-Json
    Write-Host "  Loaded $($papers.Count) papers for trend analysis" -ForegroundColor Green
}
Write-Host ""

# Build indexes
$entitiesById = @{}
foreach ($entity in $graph.entities) {
    $entitiesById[$entity.id] = $entity
}

$entitiesByType = @{}
foreach ($entity in $graph.entities) {
    $type = $entity.type
    if (!$entitiesByType.ContainsKey($type)) {
        $entitiesByType[$type] = @()
    }
    $entitiesByType[$type] += $entity
}

$relationsBySource = @{}
foreach ($relation in $graph.relations) {
    if (!$relationsBySource.ContainsKey($relation.source)) {
        $relationsBySource[$relation.source] = @()
    }
    $relationsBySource[$relation.source] += $relation
}

$relationsByTarget = @{}
foreach ($relation in $graph.relations) {
    if (!$relationsByTarget.ContainsKey($relation.target)) {
        $relationsByTarget[$relation.target] = @()
    }
    $relationsByTarget[$relation.target] += $relation
}

Write-Host "Graph Analysis:" -ForegroundColor Cyan
Write-Host "  Entity types: $($entitiesByType.Count)" -ForegroundColor Green
foreach ($type in $entitiesByType.Keys | Sort-Object) {
    Write-Host "    - $type`: $($entitiesByType[$type].Count)" -ForegroundColor Green
}
Write-Host ""

# Time Trend Analysis
Write-Host "Time Trend Analysis:" -ForegroundColor Cyan

$trendData = @{
    papers_by_year = @{}
    papers_by_source = @{ PubMed = 0; arXiv = 0 }
    entity_mentions = @{}
    hot_topics = @()
    emerging_topics = @()
}

# Analyze paper publication trends
if ($papers.Count -gt 0) {
    foreach ($paper in $papers) {
        # Count by source
        if ($trendData.papers_by_source.ContainsKey($paper.source)) {
            $trendData.papers_by_source[$paper.source]++
        }
        
        # Extract year - try multiple fields
        $year = $null
        if ($paper.year) {
            $year = $paper.year
        } elseif ($paper.published) {
            try { $year = $paper.published.Substring(0, 4) } catch { $year = $null }
        } elseif ($paper.pubdate) {
            try { $year = $paper.pubdate.Substring(0, 4) } catch { $year = $null }
        }
        
        if ($year -and $year -match '^\d{4}$') {
            if (!$trendData.papers_by_year.ContainsKey($year)) {
                $trendData.papers_by_year[$year] = 0
            }
            $trendData.papers_by_year[$year]++
        }
        
        # Count entity mentions in titles
        foreach ($entity in $graph.entities) {
            $name = if ($entity.name) { $entity.name } else { $entity.title }
            if ($name -and $paper.title) {
                if ($paper.title.ToLower() -like "*" + $name.ToLower() + "*") {
                    if (!$trendData.entity_mentions.ContainsKey($name)) {
                        $trendData.entity_mentions[$name] = 0
                    }
                    $trendData.entity_mentions[$name]++
                }
            }
        }
    }
    
    # Identify hot topics (most mentioned)
    $sortedMentions = $trendData.entity_mentions.GetEnumerator() | Sort-Object Value -Descending
    $trendData.hot_topics = $sortedMentions | Select-Object -First 5 | ForEach-Object {
        @{ name = $_.Key; count = $_.Value }
    }
    
    # Identify emerging topics (recent papers)
    $recentPapers = $papers | Where-Object { 
        $_.published -or $_.pubdate 
    } | Sort-Object -Property @{Expression = { if ($_.published) { $_.published } else { $_.pubdate } }} -Descending | Select-Object -First 10
    
    $recentMentions = @{}
    foreach ($paper in $recentPapers) {
        foreach ($entity in $graph.entities) {
            $name = if ($entity.name) { $entity.name } else { $entity.title }
            if ($name -and $paper.title) {
                if ($paper.title.ToLower() -like "*" + $name.ToLower() + "*") {
                    if (!$recentMentions.ContainsKey($name)) {
                        $recentMentions[$name] = 0
                    }
                    $recentMentions[$name]++
                }
            }
        }
    }
    
    $trendData.emerging_topics = ($recentMentions.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 5 | ForEach-Object {
        @{ name = $_.Key; count = $_.Value }
    })
}

Write-Host "  Papers by year:" -ForegroundColor Green
foreach ($year in $trendData.papers_by_year.Keys | Sort-Object) {
    Write-Host "    - $year`: $($trendData.papers_by_year[$year]) papers" -ForegroundColor Green
}

Write-Host "  Papers by source:" -ForegroundColor Green
Write-Host "    - PubMed: $($trendData.papers_by_source.PubMed)" -ForegroundColor Green
Write-Host "    - arXiv: $($trendData.papers_by_source.arXiv)" -ForegroundColor Green

Write-Host "  Hot topics (most mentioned):" -ForegroundColor Green
foreach ($topic in $trendData.hot_topics) {
    Write-Host "    - $($topic.name): $($topic.count) mentions" -ForegroundColor Green
}

Write-Host "  Emerging topics (recent):" -ForegroundColor Green
foreach ($topic in $trendData.emerging_topics) {
    Write-Host "    - $($topic.name): $($topic.count) recent mentions" -ForegroundColor Green
}
Write-Host ""

# Opportunity discovery algorithms
Write-Host "Discovering opportunities..." -ForegroundColor Cyan

$opportunities = @()

# Algorithm 1: Under-connected Applications
foreach ($app in $entitiesByType["Application"]) {
    $incomingRelations = @()
    if ($relationsByTarget.ContainsKey($app.id)) {
        $incomingRelations = $relationsByTarget[$app.id]
    }
    
    $deviceCount = ($incomingRelations | Where-Object { $_.type -eq "APPLIED_TO" }).Count
    
    if ($deviceCount -lt 2) {
        $opportunities += @{
            id = "OPP-001-$($app.name.Replace(' ', '-'))"
            type = "Under-connected Application"
            title = "Expand Device Portfolio for $($app.name)"
            description = "Application '$($app.name)' has only $deviceCount device(s). Opportunity to develop new LIG-based devices for this application."
            target = $app.name
            rationale = "Low device diversity limits application potential"
            impact = "High"
            feasibility = "Medium"
            novelty = "Medium"
            score = 7.5
            evidence = @("Current devices: $($incomingRelations.Count)")
            trend = "stable"
        }
    }
}

# Algorithm 2: Unconnected Challenges
foreach ($cha in $entitiesByType["Challenge"]) {
    $outgoingRelations = @()
    if ($relationsBySource.ContainsKey($cha.id)) {
        $outgoingRelations = $relationsBySource[$cha.id]
    }
    
    $appCount = ($outgoingRelations | Where-Object { $_.type -eq "CHALLENGES" }).Count
    
    if ($appCount -lt 3) {
        $opportunities += @{
            id = "OPP-002-$($cha.name.Replace(' ', '-'))"
            type = "Unconnected Challenge"
            title = "Address $($cha.name) in More Applications"
            description = "Challenge '$($cha.name)' affects only $appCount application(s). Research needed to extend solutions to more applications."
            target = $cha.name
            rationale = "Challenge solution not widely applied"
            impact = "High"
            feasibility = "Medium"
            novelty = "Medium"
            score = 7.0
            evidence = @("Current applications: $($appCount)")
            trend = "increasing"
        }
    }
}

# Algorithm 3: Missing Material-Device Links
$materials = $entitiesByType["Material"]
$devices = $entitiesByType["Device"]

foreach ($mat in $materials) {
    $matRelations = @()
    if ($relationsBySource.ContainsKey($mat.id)) {
        $matRelations = $relationsBySource[$mat.id]
    }
    
    $connectedDevices = ($matRelations | Where-Object { $_.type -eq "USED_IN" }).Count
    
    if ($connectedDevices -lt $devices.Count) {
        $missingDevices = @()
        foreach ($dev in $devices) {
            $isConnected = $false
            foreach ($rel in $matRelations) {
                if ($rel.target -eq $dev.id -and $rel.type -eq "USED_IN") {
                    $isConnected = $true
                    break
                }
            }
            if (!$isConnected) {
                $missingDevices += $dev.name
            }
        }
        
        if ($missingDevices.Count -gt 0) {
            # Check if material is trending
            $isTrending = $false
            foreach ($topic in $trendData.emerging_topics) {
                if ($topic.name -eq $mat.name) {
                    $isTrending = $true
                    break
                }
            }
            
            $opportunities += @{
                id = "OPP-003-$($mat.name.Replace(' ', '-'))"
                type = "Missing Material-Device Link"
                title = "Explore $($mat.name) in New Device Types"
                description = "Material '$($mat.name)' is not used in $($missingDevices.Count) device type(s). Potential for novel device development."
                target = $mat.name
                rationale = "Material underutilized across device types"
                impact = "Medium"
                feasibility = "High"
                novelty = "High"
                score = if ($isTrending) { 8.5 } else { 8.0 }
                evidence = @("Missing devices: $($missingDevices -join ', ')")
                trend = if ($isTrending) { "emerging" } else { "stable" }
            }
        }
    }
}

# Algorithm 4: Signal Detection Gaps
$signals = $entitiesByType["Signal"]

foreach ($sig in $signals) {
    $incoming = @()
    if ($relationsByTarget.ContainsKey($sig.id)) {
        $incoming = $relationsByTarget[$sig.id]
    }
    
    $detectingDevices = ($incoming | Where-Object { $_.type -eq "DETECTS" }).Count
    
    if ($detectingDevices -lt 2) {
        $opportunities += @{
            id = "OPP-004-$($sig.name.Replace(' ', '-'))"
            type = "Signal Detection Gap"
            title = "Develop More Detectors for $($sig.name)"
            description = "Signal '$($sig.name)' is detected by only $detectingDevices device(s). Opportunity for new sensor development."
            target = $sig.name
            rationale = "Limited detection capabilities"
            impact = "Medium"
            feasibility = "High"
            novelty = "Medium"
            score = 7.0
            evidence = @("Current detectors: $detectingDevices")
            trend = "stable"
        }
    }
}

# Algorithm 5: Pathway Expansion
$pathways = $entitiesByType["Pathway"]

foreach ($path in $pathways) {
    $incoming = @()
    if ($relationsByTarget.ContainsKey($path.id)) {
        $incoming = $relationsByTarget[$path.id]
    }
    
    if ($incoming.Count -lt 3) {
        $opportunities += @{
            id = "OPP-005-$($path.name.Replace(' ', '-'))"
            type = "Pathway Expansion"
            title = "Explore More Triggers for $($path.name)"
            description = "Pathway '$($path.name)' has only $($incoming.Count) known trigger(s). Research needed to identify additional activation mechanisms."
            target = $path.name
            rationale = "Limited pathway understanding"
            impact = "High"
            feasibility = "Medium"
            novelty = "High"
            score = 8.5
            evidence = @("Current triggers: $($incoming.Count)")
            trend = "emerging"
        }
    }
}

# Algorithm 6: Cross-type Innovation
foreach ($dev in $devices) {
    $devRelations = @()
    if ($relationsBySource.ContainsKey($dev.id)) {
        $devRelations = $relationsBySource[$dev.id]
    }
    
    $connectedApps = ($devRelations | Where-Object { $_.type -eq "APPLIED_TO" }).Count
    
    if ($connectedApps -lt $entitiesByType["Application"].Count / 2) {
        $opportunities += @{
            id = "OPP-006-$($dev.name.Replace(' ', '-'))"
            type = "Cross-type Innovation"
            title = "Extend $($dev.name) to New Applications"
            description = "Device '$($dev.name)' is applied to only $connectedApps application(s). Potential for application expansion."
            target = $dev.name
            rationale = "Device application scope limited"
            impact = "Medium"
            feasibility = "High"
            novelty = "Medium"
            score = 7.0
            evidence = @("Current applications: $connectedApps")
            trend = "stable"
        }
    }
}

# Sort by score
$opportunities = $opportunities | Sort-Object -Property score -Descending

Write-Host "  Discovered $($opportunities.Count) opportunities" -ForegroundColor Green
Write-Host ""

# Generate report
Write-Host "Generating report..." -ForegroundColor Cyan

$report = "# LIG Research Opportunity Analysis (with Time Trends)`n`n"
$report += "**Generated:** $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n"
$report += "**Graph Version:** $($graph.stats.updated_at)`n"
$report += "**Total Opportunities:** $($opportunities.Count)`n"
$report += "**Papers Analyzed:** $($papers.Count)`n`n"

$report += "---`n`n"

$report += "## Executive Summary`n`n"
$report += "This analysis identified **$($opportunities.Count) research opportunities** based on the LIG knowledge graph structure and time trend analysis.`n`n"

$report += "## Time Trend Analysis`n`n"

$report += "### Publication Trends`n`n"
if ($trendData.papers_by_year.Count -gt 0) {
    $report += "**Papers by Year:**`n`n"
    $report += "| Year | Count |`n"
    $report += "|------|-------|`n"
    foreach ($year in $trendData.papers_by_year.Keys | Sort-Object) {
        $report += "| $year | $($trendData.papers_by_year[$year]) |`n"
    }
    $report += "`n"
}

$report += "**Papers by Source:**`n"
$report += "- PubMed: $($trendData.papers_by_source.PubMed)`n"
$report += "- arXiv: $($trendData.papers_by_source.arXiv)`n`n"

$report += "### Hot Topics (Most Mentioned)`n`n"
$report += "| Topic | Mentions |`n"
$report += "|-------|----------|`n"
foreach ($topic in $trendData.hot_topics) {
    $report += "| $($topic.name) | $($topic.count) |`n"
}
$report += "`n"

$report += "### Emerging Topics (Recent)`n`n"
$report += "| Topic | Recent Mentions | Trend |`n"
$report += "|-------|-----------------|-------|`n"
foreach ($topic in $trendData.emerging_topics) {
    $report += "| $($topic.name) | $($topic.count) | 📈 |`n"
}
$report += "`n"

$report += "---`n`n"

$report += "## Opportunity Distribution by Type`n`n"
$oppTypes = @{}
foreach ($opp in $opportunities) {
    if (!$oppTypes.ContainsKey($opp.type)) {
        $oppTypes[$opp.type] = 0
    }
    $oppTypes[$opp.type]++
}
foreach ($type in $oppTypes.Keys | Sort-Object) {
    $report += "- **$type`**: $($oppTypes[$type])`n"
}
$report += "`n"

$report += "### Top 5 Opportunities by Score`n`n"
$top5 = $opportunities | Select-Object -First 5
for ($i = 0; $i -lt $top5.Count; $i++) {
    $opp = $top5[$i]
    $trendIcon = switch ($opp.trend) {
        "emerging" { "📈" }
        "increasing" { "📊" }
        default { "➡️" }
    }
    $report += "$($i + 1). **$($opp.title)** $trendIcon (Score: $($opp.score))`n"
    $report += "   - Type: $($opp.type)`n"
    $report += "   - Impact: $($opp.impact)`n"
    $report += "   - Feasibility: $($opp.feasibility)`n"
    $report += "   - Trend: $($opp.trend)`n`n"
}

$report += "---`n`n"

$report += "## Detailed Opportunities`n`n"

foreach ($opp in $opportunities) {
    $trendIcon = switch ($opp.trend) {
        "emerging" { "📈 Emerging" }
        "increasing" { "📊 Increasing" }
        default { "➡️ Stable" }
    }
    
    $report += "### $($opp.id): $($opp.title)`n`n"
    $report += "**Type:** $($opp.type)`n"
    $report += "**Target:** $($opp.target)`n"
    $report += "**Score:** $($opp.score)/10`n"
    $report += "**Trend:** $trendIcon`n`n"
    
    $report += "**Description:**`n"
    $report += "$($opp.description)`n`n"
    
    $report += "**Rationale:**`n"
    $report += "$($opp.rationale)`n`n"
    
    $report += "**Assessment:**`n"
    $report += "- Impact: $($opp.impact)`n"
    $report += "- Feasibility: $($opp.feasibility)`n"
    $report += "- Novelty: $($opp.novelty)`n"
    $report += "- Trend: $($opp.trend)`n`n"
    
    $report += "**Evidence:**`n"
    foreach ($ev in $opp.evidence) {
        $report += "- $ev`n"
    }
    $report += "`n---`n`n"
}

$report += "## Methodology`n`n"
$report += "Opportunities were discovered using 6 graph analysis algorithms:`n`n"
$report += "1. **Under-connected Applications** - Identify applications with limited device support`n"
$report += "2. **Unconnected Challenges** - Find challenges affecting few applications`n"
$report += "3. **Missing Material-Device Links** - Discover unexplored material-device combinations`n"
$report += "4. **Signal Detection Gaps** - Identify signals with limited detection capabilities`n"
$report += "5. **Pathway Expansion** - Find pathways with few known triggers`n"
$report += "6. **Cross-type Innovation** - Discover device-application expansion opportunities`n`n"

$report += "### Trend Analysis`n`n"
$report += "- **Hot Topics**: Most frequently mentioned entities in recent papers`n"
$report += "- **Emerging Topics**: Topics with increasing mention frequency`n"
$report += "- **Trend Icons**: 📈 Emerging | 📊 Increasing | ➡️ Stable`n`n"

$report += "### Scoring Criteria`n`n"
$report += "| Factor | Weight | Scale |`n"
$report += "|--------|--------|-------|`n"
$report += "| Impact | 40% | High/Medium/Low |`n"
$report += "| Feasibility | 30% | High/Medium/Low |`n"
$report += "| Novelty | 20% | High/Medium/Low |`n"
$report += "| Trend | 10% | Emerging/Increasing/Stable |`n`n"

# Save report
if (!(Test-Path (Split-Path $OutputFile))) {
    New-Item -ItemType Directory -Path (Split-Path $OutputFile) | Out-Null
}

$report | Set-Content $OutputFile -Encoding UTF8
Write-Host "  Saved: $OutputFile" -ForegroundColor Green

# Also save JSON for programmatic access
$jsonOutput = $OutputFile -replace '\.md$', '.json'
$exportData = @{
    opportunities = $opportunities
    trend_data = $trendData
    generated_at = Get-Date -Format "yyyy-MM-ddTHH:mm:ssK"
    graph_version = $graph.stats.updated_at
}
$exportData | ConvertTo-Json -Depth 10 | Set-Content $jsonOutput -Encoding UTF8
Write-Host "  Saved: $jsonOutput" -ForegroundColor Green

Write-Host ""
Write-Host "Done!" -ForegroundColor Green

return @{
    success = $true
    opportunities = $opportunities.Count
    outputFile = $OutputFile
    jsonFile = $jsonOutput
    trend_data = $trendData
}
