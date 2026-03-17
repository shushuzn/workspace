# 30-scripts 完整重组脚本
# 用法：.\reorganize-now.ps1

$src = "D:\OpenClaw\workspace\30-scripts"
$ErrorActionPreference = "Continue"

function Move-File {
    param($from, $to)
    $srcPath = Join-Path $src $from
    $dstPath = Join-Path $src $to
    if (Test-Path $srcPath) {
        try {
            Move-Item -Path $srcPath -Destination $dstPath -Force -ErrorAction SilentlyContinue
            Write-Host "  ✅ $from → $to" -ForegroundColor Green
            return $true
        } catch {
            Write-Host "  ❌ $from → $to (失败：$_)" -ForegroundColor Red
            return $false
        }
    }
    return $false
}

function Move-Dir {
    param($from, $to)
    $srcPath = Join-Path $src $from
    $dstPath = Join-Path $src $to
    if (Test-Path $srcPath) {
        try {
            robocopy $srcPath $dstPath /E /NFL /NDL /NJH /NJS /MOVE | Out-Null
            Write-Host "  ✅ $from → $to" -ForegroundColor Green
            return $true
        } catch {
            Write-Host "  ❌ $from → $to (失败)" -ForegroundColor Red
            return $false
        }
    }
    return $false
}

Write-Host "`n🚀 开始重组 30-scripts..." -ForegroundColor Cyan
Write-Host "  源目录：$src" -ForegroundColor Gray
Write-Host "  时间：$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray

# 01-KNOWLEDGE-CARDS
Write-Host "`n📦 01-KNOWLEDGE-CARDS..." -ForegroundColor Yellow
Move-File "knowledge-card-generator.py" "01-KNOWLEDGE-CARDS/core/"
Move-File "knowledge-card-webui.py" "01-KNOWLEDGE-CARDS/core/"
Move-Dir "knowledge-card-generator" "01-KNOWLEDGE-CARDS/docs/"
Move-Dir "pdf-extractor" "01-KNOWLEDGE-CARDS/pdf/"
Move-Dir "figure-enhancer" "01-KNOWLEDGE-CARDS/figures/"
Move-File "prepare-formula-dataset.py" "01-KNOWLEDGE-CARDS/formula/"
Move-File "generate_formula_dataset.py" "01-KNOWLEDGE-CARDS/formula/"
Move-File "generate_handwritten_formulas.py" "01-KNOWLEDGE-CARDS/formula/"
Move-File "finetune-formula-model.py" "01-KNOWLEDGE-CARDS/formula/"
Move-File "prepare_complex_formulas.py" "01-KNOWLEDGE-CARDS/formula/"

# 02-DAILY-BRIEF
Write-Host "`n📦 02-DAILY-BRIEF..." -ForegroundColor Yellow
Move-Dir "daily-brief" "02-DAILY-BRIEF/core/"
Move-File "daily-brief.ps1" "02-DAILY-BRIEF/core/"
Move-Dir "weather" "02-DAILY-BRIEF/weather/"
Move-File "feishu-ui-sync.py" "02-DAILY-BRIEF/feishu/"
Move-File "feishu-ui-sync-cron.json" "02-DAILY-BRIEF/feishu/"
Move-File "process-feishu-queue.py" "02-DAILY-BRIEF/feishu/"
Move-File "start-feishu-ui-sync.bat" "02-DAILY-BRIEF/feishu/"
Move-File "README-feishu-ui-sync.md" "02-DAILY-BRIEF/feishu/"
Move-File "obsidian-sync-startup.bat" "02-DAILY-BRIEF/sync/"
Move-File "daily-brief-autorun.bat" "02-DAILY-BRIEF/"

# 03-LIG-KNOWLEDGE-GRAPH
Write-Host "`n📦 03-LIG-KNOWLEDGE-GRAPH..." -ForegroundColor Yellow
Move-Dir "graph-optimizer" "03-LIG-KNOWLEDGE-GRAPH/"
Move-Dir "multimodal-kg" "03-LIG-KNOWLEDGE-GRAPH/"
Get-ChildItem $src -Filter "lig-*.js" | ForEach-Object { Move-File $_.Name "03-LIG-KNOWLEDGE-GRAPH/workers/" }
Get-ChildItem $src -Filter "LIG-*.html" | ForEach-Object { Move-File $_.Name "03-LIG-KNOWLEDGE-GRAPH/html/" }
Get-ChildItem $src -Filter "lig-*.ps1" | ForEach-Object { Move-File $_.Name "03-LIG-KNOWLEDGE-GRAPH/scripts/" }
Move-File "lig-collect-industry.py" "03-LIG-KNOWLEDGE-GRAPH/scripts/"
Move-File "lig-create-outreach.py" "03-LIG-KNOWLEDGE-GRAPH/scripts/"
Move-File "organize-lig-outreach.py" "03-LIG-KNOWLEDGE-GRAPH/scripts/"
Move-File "fix-lig-outreach.py" "03-LIG-KNOWLEDGE-GRAPH/scripts/"
Move-File "train_lig_stability_model.py" "03-LIG-KNOWLEDGE-GRAPH/ml/"
Move-File "lig-update-config.yaml" "03-LIG-KNOWLEDGE-GRAPH/"

# 04-COLLECTORS
Write-Host "`n📦 04-COLLECTORS..." -ForegroundColor Yellow
Move-Dir "collectors" "04-COLLECTORS/"
Move-File "reddit-monitor.log" "04-COLLECTORS/reddit/"
Move-File "reddit-seen.db" "04-COLLECTORS/reddit/"
Move-File "x-twitter-monitor.py" "04-COLLECTORS/x-twitter/"
Move-File "x-twitter.log" "04-COLLECTORS/x-twitter/"
Move-File "x-twitter-seen.db" "04-COLLECTORS/x-twitter/"
Move-File "hn-comment-analyzer.py" "04-COLLECTORS/hn/"

# 05-AI-RESEARCH
Write-Host "`n📦 05-AI-RESEARCH..." -ForegroundColor Yellow
Move-Dir "ai-analysis" "05-AI-RESEARCH/"
Move-Dir "analysis" "05-AI-RESEARCH/"
Move-Dir "research" "05-AI-RESEARCH/"
Move-File "multi-agent-framework.py" "05-AI-RESEARCH/multi-agent/"
Move-File "multi-agent-executors.py" "05-AI-RESEARCH/multi-agent/"
Move-File "tdd-debug-agent.py" "05-AI-RESEARCH/tdd/"
Move-File "integrate-advanced-skills.py" "05-AI-RESEARCH/integration/"
Move-File "integrate-collectors.py" "05-AI-RESEARCH/integration/"

# 06-MONITORING
Write-Host "`n📦 06-MONITORING..." -ForegroundColor Yellow
Move-Dir "monitoring" "06-MONITORING/"
Move-File "METRICS_COLLECTOR.ps1" "06-MONITORING/scripts/"
Move-File "METRICS_DASHBOARD.html" "06-MONITORING/metrics/"
Move-File "metrics_history.csv" "06-MONITORING/metrics/"
Move-File "metrics_collector.log" "06-MONITORING/metrics/"
Move-File "heartbeat-check.ps1" "06-MONITORING/scripts/"
Move-File "heartbeat-exec.ps1" "06-MONITORING/scripts/"
Move-File "heartbeat-done.ps1" "06-MONITORING/scripts/"

# 07-DATA
Write-Host "`n📦 07-DATA..." -ForegroundColor Yellow
Move-Dir "api" "07-DATA/"
Move-Dir "api-server" "07-DATA/"
Move-Dir "data-lake" "07-DATA/"
Move-Dir "materials" "07-DATA/"
Move-File "domain_data_collector.py" "07-DATA/domain/"
Move-File "test_jina.py" "07-DATA/api/"
Move-File "test_rss.py" "07-DATA/api/"

# 08-AUTOMATION
Write-Host "`n📦 08-AUTOMATION..." -ForegroundColor Yellow
Move-Dir "auto-pnote" "08-AUTOMATION/auto-pnote/"
Move-File "auto-pnote.ps1" "08-AUTOMATION/auto-pnote/"
Move-File "github-repo-reorganize.py" "08-AUTOMATION/github-sync/"
Move-File "github-repo-reorganize-phase2.py" "08-AUTOMATION/github-sync/"
Move-File "github-repo-reorganize-phase3.py" "08-AUTOMATION/github-sync/"
Move-File "github-repo-reorganize-phase4.py" "08-AUTOMATION/github-sync/"
Move-File "setup-scheduled-task.py" "08-AUTOMATION/scheduled-tasks/"
Move-File "setup-daily-brief-task.ps1" "08-AUTOMATION/scheduled-tasks/"
Move-File "setup-domain-cron.ps1" "08-AUTOMATION/scheduled-tasks/"
Move-File "setup-arxiv-orchestrator-task.ps1" "08-AUTOMATION/scheduled-tasks/"
Move-File "feishu-ui-sync-cron.json" "08-AUTOMATION/scheduled-tasks/"
Move-File "lig-auto-update.ps1" "08-AUTOMATION/scripts/"
Move-File "organize_workspace.py" "08-AUTOMATION/scripts/"
Move-File "organize-reports-folder.py" "08-AUTOMATION/scripts/"
Move-File "auto_recovery.py" "08-AUTOMATION/scripts/"

# 09-TESTS
Write-Host "`n📦 09-TESTS..." -ForegroundColor Yellow
Move-Dir "testing" "09-TESTS/"
Move-File "test_pdf_extractor.py" "09-TESTS/pdf-extractor/"
Move-File "test_results.json" "09-TESTS/pdf-extractor/"
Move-File "test_suite.py" "09-TESTS/figure-enhancer/"
Move-File "benchmark.py" "09-TESTS/scripts/"
Move-File "check_classical_ratio.py" "09-TESTS/scripts/"
Move-File "check_recent.py" "09-TESTS/scripts/"
Move-File "check_recent_papers.py" "09-TESTS/scripts/"
Move-File "run-acceptance-test.ps1" "09-TESTS/scripts/"

# 10-DOMAIN-RANKING
Write-Host "`n📦 10-DOMAIN-RANKING..." -ForegroundColor Yellow
Move-File "domain_ranker_v2.py" "10-DOMAIN-RANKING/core/"
Move-File "domain_ranker.py" "10-DOMAIN-RANKING/core/"
Move-File "domain_ranking_report.py" "10-DOMAIN-RANKING/reports/"
Move-File "setup-domain-cron.ps1" "10-DOMAIN-RANKING/scripts/"

# 11-NOVEL-WRITING
Write-Host "`n📦 11-NOVEL-WRITING..." -ForegroundColor Yellow
Get-ChildItem $src -Filter "expand_chapter*.py" | ForEach-Object { Move-File $_.Name "11-NOVEL-WRITING/chapters/" }
Move-File "expand_chapters.py" "11-NOVEL-WRITING/chapters/"
Move-File "expand_chapters_5_6.py" "11-NOVEL-WRITING/chapters/"
Move-File "manage_chapters.py" "11-NOVEL-WRITING/chapters/"
Move-File "detect_ai_style.py" "11-NOVEL-WRITING/analysis/"
Move-File "check_word_count.py" "11-NOVEL-WRITING/analysis/"
Move-File "optimize_ai_rate.py" "11-NOVEL-WRITING/analysis/"
Move-File "track_writing_progress.py" "11-NOVEL-WRITING/analysis/"
Move-File "optimize_chapter3.py" "11-NOVEL-WRITING/chapters/"
Move-File "optimize_chapter7.py" "11-NOVEL-WRITING/chapters/"
Move-File "deep_optimize_chapter4.py" "11-NOVEL-WRITING/chapters/"
Move-File "enhance_chapters_2_3.py" "11-NOVEL-WRITING/chapters/"
Move-File "track_foreshadowing.py" "11-NOVEL-WRITING/foreshadowing/"
Move-File "read_chapter.py" "11-NOVEL-WRITING/utils/"
Move-File "fix_chapter5_count.py" "11-NOVEL-WRITING/utils/"

# 12-KNOWLEDGE-MANAGEMENT
Write-Host "`n📦 12-KNOWLEDGE-MANAGEMENT..." -ForegroundColor Yellow
Move-File "rename-knowledge-cards.py" "12-KNOWLEDGE-MANAGEMENT/rename/"
Move-File "rename-knowledge-cards-v2.py" "12-KNOWLEDGE-MANAGEMENT/rename/"

# 13-SECURITY
Write-Host "`n📦 13-SECURITY..." -ForegroundColor Yellow
Move-File "security_hardening.py" "13-SECURITY/scripts/"
Move-File "SCRIPT_Health_Check_v1.0.ps1" "13-SECURITY/scripts/"
Move-File "SCRIPT_Nightly_SecurityAudit_v1.0.ps1" "13-SECURITY/scripts/"
Move-File "SCRIPT_Run_AllAudit_v1.0.ps1" "13-SECURITY/scripts/"
Move-File "check-quality.sh" "13-SECURITY/scripts/"

# 14-PLUGIN
Write-Host "`n📦 14-PLUGIN..." -ForegroundColor Yellow
Move-File "plugin_marketplace.py" "14-PLUGIN/marketplace/"
Move-File "install-blogwatcher.bat" "14-PLUGIN/install/"
Move-File "install-summarize.bat" "14-PLUGIN/install/"
Move-File "SCRIPT_Install_Blogwatcher_v1.0.ps1" "14-PLUGIN/install/"
Move-File "SCRIPT_Install_Tools_v1.0.ps1" "14-PLUGIN/install/"

# 15-COGNITIVE-SYSTEM
Write-Host "`n📦 15-COGNITIVE-SYSTEM..." -ForegroundColor Yellow
Move-File "dump_cognitive.py" "15-COGNITIVE-SYSTEM/debug/"
Move-File "read_cognitive_system.py" "15-COGNITIVE-SYSTEM/debug/"
Move-File "cognitive_system_dump.json" "15-COGNITIVE-SYSTEM/debug/"

# 00-UTILS
Write-Host "`n📦 00-UTILS..." -ForegroundColor Yellow
Move-Dir "cache" "00-UTILS/"
Move-Dir "backups" "00-UTILS/"
Move-Dir "utils" "00-UTILS/"
Move-Dir "tools" "00-UTILS/"

# 99-ARCHIVE
Write-Host "`n📦 99-ARCHIVE..." -ForegroundColor Yellow
Move-Dir "level-0" "99-ARCHIVE/"
Move-Dir "early_exit_framework" "99-ARCHIVE/"
Move-Dir "feedback" "99-ARCHIVE/"
Move-Dir "intent-belief-integration" "99-ARCHIVE/"

# 其他散落文件
Write-Host "`n📦 清理散落文件..." -ForegroundColor Yellow
Move-File "arxiv-research-orchestrator.ps1" "04-COLLECTORS/arxiv/"
Move-File "arxiv_ops_cli.py" "04-COLLECTORS/arxiv/"
Move-File "context-compressor.py" "05-AI-RESEARCH/"
Move-File "difficulty-evaluator.py" "11-NOVEL-WRITING/analysis/"
Move-File "detect_sensitive_content.py" "04-COLLECTORS/"
Move-File "git-cleanup.ps1" "08-AUTOMATION/scripts/"
Move-File "mcp-integrator.log" "05-AI-RESEARCH/"
Move-File "performance_optimization.py" "05-AI-RESEARCH/"
Move-File "search.ps1" "00-UTILS/tools/"
Move-File "stop.sh" "00-UTILS/tools/"
Move-File "tag-tree.html" "00-UTILS/"
Move-File "view-tags.ps1" "00-UTILS/tools/"
Move-File "weather" "02-DAILY-BRIEF/weather/"
Move-File "weather-config.example.json" "02-DAILY-BRIEF/weather/"
Move-File "backup.sh" "00-UTILS/backups/"
Move-File "deploy.sh" "08-AUTOMATION/scripts/"
Move-File "fix-arxiv-task.bat" "08-AUTOMATION/scripts/"
Move-File "test-mcp.bat" "09-TESTS/"
Move-File "mcp-integrator.log" "05-AI-RESEARCH/"

Write-Host "`n✅ 重组完成!" -ForegroundColor Green
Write-Host "  请检查根目录是否还有遗漏文件" -ForegroundColor Gray
