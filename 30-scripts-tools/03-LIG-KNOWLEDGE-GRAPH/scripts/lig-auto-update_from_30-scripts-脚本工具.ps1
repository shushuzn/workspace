#!/usr/bin/env pwsh
# LIG Knowledge Graph Auto-Update Main Script
# Coordinates: paper collection -> entity extraction -> graph update

param(
    [string]$ConfigFile = "30-scripts/lig-update-config.yaml",
    [int]$DaysBack = 7,
    [switch]$Force,
    [switch]$NoBackup,
    [switch]$Verbose,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

Write-Host "LIG Knowledge Graph Auto-Update" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan
Write-Host "Start Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n" -ForegroundColor Gray

$startTime = Get-Date

$results = @{
    papers_collected = 0
    entities_extracted = 0
    relations_extracted = 0
    errors = @()
    warnings = @()
    success = $true
}

try {
    # Step 1: Paper Collection
    Write-Host "Step 1/3: Collecting Papers..." -ForegroundColor Cyan
    Write-Host "-------------------------------" -ForegroundColor Gray
    
    if ($DryRun) {
        Write-Host "   [DRY RUN] Skipping paper collection" -ForegroundColor Yellow
    } else {
        $fetchScript = "30-scripts/lig-fetch-papers.ps1"
        if (Test-Path $fetchScript) {
            & $fetchScript -ConfigFile $ConfigFile -DaysBack $DaysBack -Force:$Force -Verbose:$Verbose
            
            $latestPapersFile = Get-ChildItem -Path "40-arxiv" -Filter "lig-papers-*.json" | 
                               Sort-Object LastWriteTime -Descending | 
                               Select-Object -First 1
            
            if ($latestPapersFile) {
                $papers = Get-Content $latestPapersFile.FullName | ConvertFrom-Json
                $results.papers_collected = $papers.Count
                Write-Host "   OK: Collected $($results.papers_collected) papers" -ForegroundColor Green
            }
        } else {
            Write-Host "   ERROR: Script not found: $fetchScript" -ForegroundColor Red
            $results.errors += "Paper collection script not found"
            $results.success = $false
        }
    }
    
    Write-Host ""
    
    # Step 2: Entity Extraction
    Write-Host "Step 2/3: Extracting Entities..." -ForegroundColor Cyan
    Write-Host "-------------------------------" -ForegroundColor Gray
    
    if ($DryRun) {
        Write-Host "   [DRY RUN] Skipping entity extraction" -ForegroundColor Yellow
    } elseif ($results.success) {
        $extractScript = "30-scripts/lig-extract-entities.ps1"
        if (Test-Path $extractScript) {
            & $extractScript -OutputFile "12-knowledge-graph/lig-graph.json" -ConfigFile $ConfigFile -Verbose:$Verbose
            
            if (Test-Path "12-knowledge-graph/lig-graph.json") {
                $graph = Get-Content "12-knowledge-graph/lig-graph.json" | ConvertFrom-Json
                $results.entities_extracted = $graph.entities.Count
                $results.relations_extracted = $graph.relations.Count
                Write-Host "   OK: Extracted $($results.entities_extracted) entities" -ForegroundColor Green
                Write-Host "   OK: Extracted $($results.relations_extracted) relations" -ForegroundColor Green
            }
        } else {
            Write-Host "   ERROR: Script not found: $extractScript" -ForegroundColor Red
            $results.errors += "Entity extraction script not found"
            $results.success = $false
        }
    } else {
        Write-Host "   SKIPPED (previous step failed)" -ForegroundColor Yellow
    }
    
    Write-Host ""
    
    # Step 3: Graph Validation
    Write-Host "Step 3/3: Validating Graph..." -ForegroundColor Cyan
    Write-Host "-------------------------------" -ForegroundColor Gray
    
    if ($DryRun) {
        Write-Host "   [DRY RUN] Skipping graph validation" -ForegroundColor Yellow
    } elseif ($results.success) {
        $updateScript = "30-scripts/lig-update-graph.ps1"
        if (Test-Path $updateScript) {
            $updateResult = & $updateScript -NoBackup:$NoBackup -Verbose:$Verbose
            
            if (!$updateResult.success) {
                $results.errors += $updateResult.errors
                $results.warnings += $updateResult.warnings
            }
        } else {
            Write-Host "   ERROR: Script not found: $updateScript" -ForegroundColor Red
            $results.errors += "Graph update script not found"
            $results.success = $false
        }
    } else {
        Write-Host "   SKIPPED (previous step failed)" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "`nERROR: $($_.Exception.Message)" -ForegroundColor Red
    $results.errors += $_.Exception.Message
    $results.success = $false
}

$endTime = Get-Date
$duration = New-TimeSpan -Start $startTime -End $endTime

Write-Host "`n" -NoNewline
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Results" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Status: $(if ($results.success) { 'SUCCESS' } else { 'FAILED' })" -ForegroundColor $(if ($results.success) { 'Green' } else { 'Red' })
Write-Host "Duration: $($duration.Minutes)m $($duration.Seconds)s" -ForegroundColor Gray
Write-Host "Papers: $($results.papers_collected)" -ForegroundColor Green
Write-Host "Entities: $($results.entities_extracted)" -ForegroundColor Green
Write-Host "Relations: $($results.relations_extracted)" -ForegroundColor Green

if ($results.errors.Count -gt 0) {
    Write-Host "`nErrors:" -ForegroundColor Red
    foreach ($err in $results.errors) {
        Write-Host "  - $err" -ForegroundColor Red
    }
}

if ($results.warnings.Count -gt 0) {
    Write-Host "`nWarnings:" -ForegroundColor Yellow
    foreach ($warn in $results.warnings) {
        Write-Host "  - $warn" -ForegroundColor Yellow
    }
}

Write-Host "`nEnd Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n" -ForegroundColor Gray

return $results
