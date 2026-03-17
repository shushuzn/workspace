#!/usr/bin/env pwsh
# LIG Entity and Relation Extraction Script

param(
    [string]$InputFile,
    [string]$OutputFile = "12-knowledge-graph/lig-graph.json",
    [double]$ConfidenceThreshold = 0.75,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

Write-Host "LIG Entity Extraction" -ForegroundColor Cyan
Write-Host "=====================" -ForegroundColor Cyan
Write-Host ""

if (!$InputFile) {
    $arxivDir = "40-arxiv"
    $latestFile = Get-ChildItem -Path $arxivDir -Filter "lig-papers-*.json" | 
                  Sort-Object LastWriteTime -Descending | 
                  Select-Object -First 1
    
    if ($latestFile) {
        $InputFile = $latestFile.FullName
        Write-Host "Using latest paper file: $InputFile" -ForegroundColor Green
    } else {
        Write-Host "ERROR: No paper file found" -ForegroundColor Red
        exit 1
    }
}

$papers = Get-Content $InputFile | ConvertFrom-Json
Write-Host "Loaded papers: $($papers.Count)" -ForegroundColor Green
Write-Host ""

$existingGraph = @{ entities = @(); relations = @() }
if (Test-Path $OutputFile) {
    $existingGraph = Get-Content $OutputFile | ConvertFrom-Json
    Write-Host "Loaded existing graph: $($existingGraph.entities.Count) entities, $($existingGraph.relations.Count) relations" -ForegroundColor Green
    Write-Host ""
}

$LIG_KEYWORDS = @("lig", "laser-induced graphene", "laser scribed graphene")
$MATERIAL_KEYWORDS = @("graphene", "go", "graphene oxide", "rgo", "polyimide", "pi", "cuo", "copper oxide", "zno", "tio2")
$DEVICE_KEYWORDS = @("sensor", "biosensor", "electrode", "neural probe", "wearable", "patch", "implant", "transistor", "supercapacitor", "battery")
$SIGNAL_KEYWORDS = @("electrical", "electrochemical", "impedance", "voltage", "current", "fluorescence", "optical", "thermal", "strain", "pressure")
$APPLICATION_KEYWORDS = @("biomedical", "health monitoring", "diagnostic", "neural", "brain", "glucose", "cancer", "tumor", "gas sensor", "humidity")
$CHALLENGE_KEYWORDS = @("stability", "biocompatibility", "toxicity", "scalability", "reproducibility", "selectivity", "sensitivity", "drift")

function Extract-Entities {
    param($Paper)
    
    $entities = @()
    $title = $Paper.title
    $summary = if ($Paper.summary) { $Paper.summary } else { "" }
    $text = ($title + " " + $summary).ToLower()
    
    $entityId = 0
    
    if ($text -like "*paper*") {
        $paperId = if ($Paper.pmid) { "paper-pmid-" + $Paper.pmid } else { "paper-arxiv-" + $Paper.arxiv_id }
        $year = if ($Paper.pubdate) { $Paper.pubdate.Substring(0,4) } elseif ($Paper.published) { $Paper.published.Substring(0,4) } else { (Get-Date).ToString("yyyy") }
        
        $entities += @{
            id = $paperId
            type = "Paper"
            title = $Paper.title
            authors = $Paper.authors
            source = $Paper.source
            url = $Paper.url
            year = $year
        }
    }
    
    foreach ($keyword in $MATERIAL_KEYWORDS) {
        if ($text -like "*" + $keyword + "*") {
            $entities += @{
                id = "mat-" + $entityId
                type = "Material"
                name = $keyword
                source = $Paper.source
                paper_id = if ($Paper.pmid) { $Paper.pmid } else { $Paper.arxiv_id }
                confidence = 0.9
            }
            $entityId++
        }
    }
    
    foreach ($keyword in $DEVICE_KEYWORDS) {
        if ($text -like "*" + $keyword + "*") {
            $entities += @{
                id = "dev-" + $entityId
                type = "Device"
                name = $keyword
                source = $Paper.source
                paper_id = if ($Paper.pmid) { $Paper.pmid } else { $Paper.arxiv_id }
                confidence = 0.85
            }
            $entityId++
        }
    }
    
    foreach ($keyword in $SIGNAL_KEYWORDS) {
        if ($text -like "*" + $keyword + "*") {
            $entities += @{
                id = "sig-" + $entityId
                type = "Signal"
                name = $keyword
                source = $Paper.source
                paper_id = if ($Paper.pmid) { $Paper.pmid } else { $Paper.arxiv_id }
                confidence = 0.8
            }
            $entityId++
        }
    }
    
    foreach ($keyword in $APPLICATION_KEYWORDS) {
        if ($text -like "*" + $keyword + "*") {
            $entities += @{
                id = "app-" + $entityId
                type = "Application"
                name = $keyword
                source = $Paper.source
                paper_id = if ($Paper.pmid) { $Paper.pmid } else { $Paper.arxiv_id }
                confidence = 0.85
            }
            $entityId++
        }
    }
    
    foreach ($keyword in $CHALLENGE_KEYWORDS) {
        if ($text -like "*" + $keyword + "*") {
            $entities += @{
                id = "cha-" + $entityId
                type = "Challenge"
                name = $keyword
                source = $Paper.source
                paper_id = if ($Paper.pmid) { $Paper.pmid } else { $Paper.arxiv_id }
                confidence = 0.75
            }
            $entityId++
        }
    }
    
    return $entities
}

function Extract-Relations {
    param($Entities, $Paper)
    
    $relations = @()
    
    $paperEntity = $null
    foreach ($e in $entities) {
        if ($e.type -eq "Paper") {
            $paperEntity = $e
            break
        }
    }
    
    if (!$paperEntity) {
        return $relations
    }
    
    $materials = @()
    $devices = @()
    $applications = @()
    
    foreach ($e in $entities) {
        if ($e.type -eq "Material") { $materials += $e }
        if ($e.type -eq "Device") { $devices += $e }
        if ($e.type -eq "Application") { $applications += $e }
    }
    
    foreach ($mat in $materials) {
        $relations += @{
            source = $paperEntity.id
            target = $mat.id
            type = "PUBLISHED"
            confidence = 0.95
        }
    }
    
    foreach ($dev in $devices) {
        foreach ($mat in $materials) {
            $relations += @{
                source = $mat.id
                target = $dev.id
                type = "USED_IN"
                confidence = 0.8
            }
        }
    }
    
    foreach ($app in $applications) {
        foreach ($dev in $devices) {
            $relations += @{
                source = $dev.id
                target = $app.id
                type = "APPLIED_TO"
                confidence = 0.75
            }
        }
    }
    
    return $relations
}

function Deduplicate-Entities {
    param($Entities)
    
    $unique = @{}
    foreach ($entity in $entities) {
        $name = if ($entity.name) { $entity.name } else { $entity.title }
        $key = ($entity.type + "_" + $name).ToLower()
        if (!$unique.ContainsKey($key)) {
            $unique[$key] = $entity
        }
    }
    
    return $unique.Values
}

Write-Host "Extracting entities and relations..." -ForegroundColor Cyan

$allEntities = @()
$allRelations = @()

foreach ($entity in $existingGraph.entities) {
    $allEntities += $entity
}
foreach ($relation in $existingGraph.relations) {
    $allRelations += $relation
}

foreach ($paper in $papers) {
    if ($Verbose) {
        $titlePreview = $paper.title
        if ($titlePreview.Length -gt 60) {
            $titlePreview = $titlePreview.Substring(0, 60) + "..."
        }
        Write-Host "  Processing: $titlePreview" -ForegroundColor Gray
    }
    
    $entities = Extract-Entities -Paper $paper
    $relations = Extract-Relations -Entities $entities -Paper $paper
    
    foreach ($entity in $entities) {
        $allEntities += $entity
    }
    foreach ($relation in $relations) {
        $allRelations += $relation
    }
}

Write-Host ""
Write-Host "Deduplicating..." -ForegroundColor Cyan

$uniqueEntities = Deduplicate-Entities -Entities $allEntities
Write-Host "  After dedup: $($uniqueEntities.Count) entities (original: $($allEntities.Count))" -ForegroundColor Green

$entityTypeCount = @{}
foreach ($entity in $uniqueEntities) {
    $type = $entity.type
    if (!$entityTypeCount.ContainsKey($type)) {
        $entityTypeCount[$type] = 0
    }
    $entityTypeCount[$type]++
}

$output = @{
    entities = $uniqueEntities
    relations = $allRelations
    stats = @{
        total_entities = $uniqueEntities.Count
        total_relations = $allRelations.Count
        entity_types = $entityTypeCount
        updated_at = Get-Date -Format "yyyy-MM-ddTHH:mm:ssK"
        source_files = @($InputFile)
    }
}

Write-Host ""
Write-Host "Saving graph..." -ForegroundColor Cyan

$output | ConvertTo-Json -Depth 10 | Set-Content $OutputFile -Encoding UTF8
Write-Host "  Saved: $OutputFile" -ForegroundColor Green

Write-Host ""
Write-Host "Statistics:" -ForegroundColor Cyan
Write-Host "  Total entities: $($output.stats.total_entities)" -ForegroundColor Green
Write-Host "  Total relations: $($output.stats.total_relations)" -ForegroundColor Green
Write-Host "  Entity types:" -ForegroundColor Green

foreach ($type in $entityTypeCount.Keys | Sort-Object) {
    Write-Host "    - $type`: $($entityTypeCount[$type])" -ForegroundColor Green
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Green
