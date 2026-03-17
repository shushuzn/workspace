# Arxiv Workflow Script
# One-click execution for paper collection, scoring, download, and parsing

param(
    [ValidateSet("collect", "score", "download", "parse", "all")]
    [string]$Mode = "all",
    
    [string]$Date = (Get-Date -Format "yyyy-MM-dd"),
    
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$WORKSPACE = "D:\OpenClaw\workspace"
$SCRIPTS_DIR = "D:\obsidian\Vault\scripts"
$VAULT = "D:\obsidian\Vault"

# ==================== Helper Functions ====================

function Write-Step {
    param([string]$Message)
    Write-Host "`n$('='*60)" -ForegroundColor Cyan
    Write-Host $Message -ForegroundColor Cyan
    Write-Host $('='*60) -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "  [OK] $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "  [ERROR] $Message" -ForegroundColor Red
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "  [WARN] $Message" -ForegroundColor Yellow
}

# ==================== Step 1: Collect Papers ====================

function Invoke-Collect {
    param([string]$Date)
    
    Write-Step "[1/4] Collecting arXiv papers"
    
    if ($DryRun) {
        Write-Warning-Custom "DryRun mode: skipping collection"
        return
    }
    
    Set-Location $SCRIPTS_DIR
    python arxiv-collector-v2.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Paper collection completed"
    } else {
        Write-Error-Custom "Paper collection failed"
        exit 1
    }
}

# ==================== Step 2: Priority Scoring ====================

function Invoke-Score {
    param([string]$Date)
    
    Write-Step "[2/4] Calculating paper priority scores"
    
    if ($DryRun) {
        Write-Warning-Custom "DryRun mode: skipping scoring"
        return
    }
    
    Set-Location $WORKSPACE
    python arxiv-priority-scorer.py -Date $Date
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Priority scoring completed"
    } else {
        Write-Error-Custom "Priority scoring failed"
        exit 1
    }
}

# ==================== Step 3: Download PDFs ====================

function Invoke-Download {
    param([string]$Date)
    
    Write-Step "[3/4] Downloading high-priority paper PDFs"
    
    $priorityFile = "$VAULT\arxiv\daily\$($Date.Substring(0,4))\$($Date.Substring(5,2))\$Date-priority.md"
    
    if (-not (Test-Path $priorityFile)) {
        Write-Error-Custom "Priority file not found: $priorityFile"
        Write-Warning-Custom "Please run scoring step first"
        return
    }
    
    Write-Host "  Priority report: $priorityFile"
    Write-Host "`n  Please download PDFs for high-priority papers to:"
    Write-Host "  $VAULT\arxiv\pdfs\$Date\"
    Write-Host "`n  Manual download:"
    Write-Host "  1. Open priority report"
    Write-Host "  2. Click arXiv links"
    Write-Host "  3. Download PDFs to target directory"
    Write-Host "`n  Or use batch download script (TBD):"
    Write-Host "  .\arxiv-download-pdfs.ps1 -Date $Date"
    Write-Host ""
    Write-Warning-Custom "Auto mode: continuing to next step"
    # Automated mode: continue without waiting for user input
}

# ==================== Step 4: Paper2MD Parsing ====================

function Invoke-Parse {
    param([string]$Date)
    
    Write-Step "[4/4] Paper2MD deep parsing"
    
    $pdfDir = "$VAULT\arxiv\pdfs\$Date"
    $outputDir = "$VAULT\arxiv\deep\$Date"
    
    if (-not (Test-Path $pdfDir)) {
        Write-Error-Custom "PDF directory not found: $pdfDir"
        Write-Warning-Custom "Please download PDF files first"
        return
    }
    
    if ($DryRun) {
        Write-Warning-Custom "DryRun mode: skipping parsing"
        return
    }
    
    # Create output directory
    if (-not (Test-Path $outputDir)) {
        New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    }
    
    # Get PDF files
    $pdfFiles = Get-ChildItem -Path $pdfDir -Filter "*.pdf"
    
    if ($pdfFiles.Count -eq 0) {
        Write-Warning-Custom "No PDF files found in $pdfDir"
        return
    }
    
    Write-Host "  Found $($pdfFiles.Count) PDF files"
    
    # Parse each PDF
    foreach ($pdf in $pdfFiles) {
        Write-Host "  Processing: $($pdf.Name)"
        python "$WORKSPACE\scripts\paper2md.py" -i $pdf.FullName -o $outputDir
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Parsed: $($pdf.Name)"
        } else {
            Write-Error-Custom "Failed: $($pdf.Name)"
        }
    }
    
    Write-Success "Paper parsing completed"
}

# ==================== Main Execution ====================

Write-Host "`n"
Write-Step "Arxiv Workflow - Mode: $Mode, Date: $Date"
Write-Host "Workspace: $WORKSPACE"
Write-Host "DryRun: $($DryRun.IsPresent)"

try {
    if ($Mode -eq "all" -or $Mode -eq "collect") {
        Invoke-Collect -Date $Date
    }
    
    if ($Mode -eq "all" -or $Mode -eq "score") {
        Invoke-Score -Date $Date
    }
    
    if ($Mode -eq "all" -or $Mode -eq "download") {
        Invoke-Download -Date $Date
    }
    
    if ($Mode -eq "all" -or $Mode -eq "parse") {
        Invoke-Parse -Date $Date
    }
    
    Write-Step "Workflow completed successfully"
    
} catch {
    Write-Error-Custom "Workflow failed: $($_.Exception.Message)"
    exit 1
}
