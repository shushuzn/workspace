#!/usr/bin/env pwsh
# LIG Graph Update and Validation Script

param(
    [string]$InputFile = "12-knowledge-graph/lig-graph.json",
    [string]$BackupDir = "12-knowledge-graph/backups",
    [int]$MaxBackups = 5,
    [string]$LogFile = "12-knowledge-graph/lig-update-log.md",
    [switch]$NoBackup,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

Write-Host "LIG Graph Update" -ForegroundColor Cyan
Write-Host "================" -ForegroundColor Cyan
Write-Host ""

if (!$NoBackup -and !(Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir | Out-Null
    Write-Host "Created backup directory: $BackupDir" -ForegroundColor Green
}

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupFile = Join-Path $BackupDir ("lig-graph-backup-" + $timestamp + ".json")

if (!$NoBackup -and (Test-Path $InputFile)) {
    Write-Host "Creating backup..." -ForegroundColor Cyan
    Copy-Item -Path $InputFile -Destination $backupFile
    Write-Host "  Backup: $backupFile" -ForegroundColor Green
    
    $backups = Get-ChildItem -Path $BackupDir -Filter "lig-graph-backup-*.json" | 
               Sort-Object LastWriteTime -Descending
    if ($backups.Count -gt $MaxBackups) {
        $oldBackups = $backups | Select-Object -Skip $MaxBackups
        foreach ($oldBackup in $oldBackups) {
            Remove-Item -Path $oldBackup.FullName -Force
            if ($Verbose) {
                Write-Host "  Deleted old backup: $($oldBackup.Name)" -ForegroundColor Gray
            }
        }
        Write-Host "  Cleaned old backups (kept latest $MaxBackups)" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Loading graph..." -ForegroundColor Cyan
$graph = Get-Content $InputFile | ConvertFrom-Json
Write-Host "  Loaded: $($graph.entities.Count) entities, $($graph.relations.Count) relations" -ForegroundColor Green

Write-Host ""
Write-Host "Validating graph..." -ForegroundColor Cyan

$errors = @()
$warnings = @()

$entityIds = @()
foreach ($entity in $graph.entities) {
    $entityIds += $entity.id
}

$uniqueIds = $entityIds | Select-Object -Unique
if ($uniqueIds.Count -lt $entityIds.Count) {
    $errors += "Duplicate entity IDs found"
} else {
    Write-Host "  OK: Entity IDs are unique" -ForegroundColor Green
}

$entityIdSet = New-Object System.Collections.Generic.HashSet[string]
foreach ($entity in $graph.entities) {
    $entityIdSet.Add($entity.id) | Out-Null
}

$orphanCount = 0
foreach ($relation in $graph.relations) {
    if (!$entityIdSet.Contains($relation.source)) {
        $orphanCount++
    }
    if (!$entityIdSet.Contains($relation.target)) {
        $orphanCount++
    }
}

if ($orphanCount -gt 0) {
    $warnings += "$orphanCount orphan relations found"
    Write-Host "  Warning: $orphanCount orphan relations" -ForegroundColor Yellow
} else {
    Write-Host "  OK: All relations reference valid entities" -ForegroundColor Green
}

$missingFields = 0
foreach ($entity in $graph.entities) {
    if (!$entity.type) {
        $missingFields++
    }
    if (!$entity.name -and !$entity.title) {
        $missingFields++
    }
}

if ($missingFields -gt 0) {
    $warnings += "$missingFields entities with missing fields"
    Write-Host "  Warning: $missingFields entities with missing fields" -ForegroundColor Yellow
} else {
    Write-Host "  OK: All required fields present" -ForegroundColor Green
}

Write-Host ""
Write-Host "Entity type statistics:" -ForegroundColor Cyan

$typeStats = @{}
foreach ($entity in $graph.entities) {
    $type = $entity.type
    if (!$typeStats.ContainsKey($type)) {
        $typeStats[$type] = 0
    }
    $typeStats[$type]++
}

foreach ($type in $typeStats.Keys | Sort-Object) {
    $count = $typeStats[$type]
    $pct = [Math]::Round(($count / $graph.entities.Count) * 100, 1)
    Write-Host "  - $type : $count ($pct%)" -ForegroundColor Green
}

Write-Host ""
Write-Host "Relation type statistics:" -ForegroundColor Cyan

$relationStats = @{}
foreach ($relation in $graph.relations) {
    $type = $relation.type
    if (!$relationStats.ContainsKey($type)) {
        $relationStats[$type] = 0
    }
    $relationStats[$type]++
}

foreach ($type in $relationStats.Keys | Sort-Object) {
    $count = $relationStats[$type]
    $pct = [Math]::Round(($count / $graph.relations.Count) * 100, 1)
    Write-Host "  - $type : $count ($pct%)" -ForegroundColor Green
}

$graph.stats = @{
    total_entities = $graph.entities.Count
    total_relations = $graph.relations.Count
    entity_types = $typeStats
    relation_types = $relationStats
    updated_at = Get-Date -Format "yyyy-MM-ddTHH:mm:ssK"
    last_update_source = $InputFile
}

Write-Host ""
Write-Host "Saving updated graph..." -ForegroundColor Cyan
$graph | ConvertTo-Json -Depth 10 | Set-Content $InputFile -Encoding UTF8
Write-Host "  Saved: $InputFile" -ForegroundColor Green

Write-Host ""
Write-Host "Writing update log..." -ForegroundColor Cyan

$logEntry = ""
$logEntry += "`n"
$logEntry += "## " + (Get-Date -Format "yyyy-MM-dd HH:mm:ss") + " - Auto Update"
$logEntry += "`n`n"
$logEntry += "### Statistics"
$logEntry += "`n"
$logEntry += "- **Entities**: " + $graph.entities.Count
$logEntry += "`n"
$logEntry += "- **Relations**: " + $graph.relations.Count
$logEntry += "`n"
$logEntry += "- **Entity Types**: " + $typeStats.Count
$logEntry += "`n`n"
$logEntry += "### Entity Types"
$logEntry += "`n"
foreach ($type in $typeStats.Keys | Sort-Object) {
    $logEntry += "- " + $type + ": " + $typeStats[$type]
    $logEntry += "`n"
}
$logEntry += "`n"
$logEntry += "### Validation"
$logEntry += "`n"
$logEntry += "- Errors: " + $errors.Count
$logEntry += "`n"
$logEntry += "- Warnings: " + $warnings.Count
$logEntry += "`n"
if (!$NoBackup) {
    $logEntry += "`n### Backup"
    $logEntry += "`n"
    $logEntry += "- File: " + $backupFile
    $logEntry += "`n"
}
$logEntry += "`n---`n"

if (Test-Path $LogFile) {
    $existingLog = Get-Content $LogFile -Raw
    $logEntry + $existingLog | Set-Content $LogFile -Encoding UTF8
} else {
    "# LIG Knowledge Graph Update Log`n`n" + $logEntry | Set-Content $LogFile -Encoding UTF8
}

Write-Host "  Log: $LogFile" -ForegroundColor Green

Write-Host ""
Write-Host "Results:" -ForegroundColor Cyan

if ($errors.Count -eq 0 -and $warnings.Count -eq 0) {
    Write-Host "  SUCCESS - No errors" -ForegroundColor Green
} elseif ($errors.Count -eq 0) {
    Write-Host "  SUCCESS - " + $warnings.Count + " warnings" -ForegroundColor Yellow
} else {
    Write-Host "  FAILED - " + $errors.Count + " errors" -ForegroundColor Red
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Green

return @{
    success = ($errors.Count -eq 0)
    entities = $graph.entities.Count
    relations = $graph.relations.Count
    errors = $errors
    warnings = $warnings
    backup = $backupFile
}
