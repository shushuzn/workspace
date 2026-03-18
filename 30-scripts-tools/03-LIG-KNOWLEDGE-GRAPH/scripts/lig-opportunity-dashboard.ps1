#!/usr/bin/env pwsh
# LIG Opportunity Dashboard Generator with Time Trends
# Creates interactive HTML visualization with trend analysis

param(
    [string]$JsonFile,
    [string]$OutputFile = "21-reports/LIG-Opportunity-Dashboard.html"
)

$ErrorActionPreference = "Stop"

Write-Host "LIG Opportunity Dashboard Generator (with Trends)" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

if (!$JsonFile) {
    $latestJson = Get-ChildItem -Path "21-reports" -Filter "LIG-Opportunity-Analysis-*.json" | 
                  Sort-Object LastWriteTime -Descending | 
                  Select-Object -First 1
    if ($latestJson) {
        $JsonFile = $latestJson.FullName
        Write-Host "Using latest JSON: $JsonFile" -ForegroundColor Green
    } else {
        Write-Host "ERROR: No opportunity JSON found" -ForegroundColor Red
        exit 1
    }
}

$data = Get-Content $JsonFile | ConvertFrom-Json
$opportunities = $data.opportunities
$trendData = $data.trend_data

Write-Host "Loaded $($opportunities.Count) opportunities" -ForegroundColor Green
Write-Host ""

# Group by type
$byType = @{}
foreach ($opp in $opportunities) {
    $type = $opp.type
    if (!$byType.ContainsKey($type)) {
        $byType[$type] = @()
    }
    $byType[$type] += $opp
}

# Group by trend
$byTrend = @{ emerging = 0; increasing = 0; stable = 0 }
foreach ($opp in $opportunities) {
    $trend = $opp.trend
    if ($byTrend.ContainsKey($trend)) {
        $byTrend[$trend]++
    }
}

# Calculate stats
$avgScore = ($opportunities | Measure-Object -Property score -Average).Average
$highImpact = ($opportunities | Where-Object { $_.impact -eq "High" }).Count
$highFeasibility = ($opportunities | Where-Object { $_.feasibility -eq "High" }).Count
$emergingCount = $byTrend.emerging

# Build paper trend chart data
$paperTrendLabels = @()
$paperTrendData = @()
if ($trendData.papers_by_year) {
    $sortedYears = $trendData.papers_by_year.PSBase.Keys | Sort-Object
    foreach ($year in $sortedYears) {
        $paperTrendLabels += $year
        $paperTrendData += $trendData.papers_by_year.$year
    }
}

# Build hot topics data
$hotTopicLabels = @()
$hotTopicData = @()
if ($trendData.hot_topics) {
    foreach ($topic in $trendData.hot_topics) {
        $hotTopicLabels += $topic.name
        $hotTopicData += $topic.count
    }
}

$html = @"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LIG Research Opportunities Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 1400px; margin: 0 auto; }
        .header { background: rgba(255,255,255,0.95); padding: 30px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.2); }
        .header h1 { color: #333; font-size: 28px; margin-bottom: 10px; }
        .header p { color: #666; font-size: 14px; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; margin-top: 20px; }
        .stat-card { background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px; border-radius: 8px; text-align: center; }
        .stat-value { font-size: 32px; font-weight: bold; }
        .stat-label { font-size: 12px; opacity: 0.9; margin-top: 5px; }
        .charts-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .chart-container { background: rgba(255,255,255,0.95); padding: 20px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.2); }
        .chart-title { font-size: 16px; color: #333; margin-bottom: 15px; font-weight: 600; display: flex; align-items: center; gap: 8px; }
        .trend-indicator { font-size: 18px; }
        .line-chart { width: 100%; height: 200px; position: relative; border-left: 2px solid #333; border-bottom: 2px solid #333; margin: 20px 0; }
        .line-chart svg { width: 100%; height: 100%; }
        .line-chart .axis-label { font-size: 10px; fill: #666; }
        .line-chart .grid-line { stroke: #e0e0e0; stroke-dasharray: 2,2; }
        .line-chart .data-line { fill: none; stroke: #667eea; stroke-width: 3; }
        .line-chart .data-point { fill: #667eea; stroke: white; stroke-width: 2; }
        .bar-chart { display: flex; flex-direction: column; gap: 10px; }
        .bar-item { display: flex; align-items: center; gap: 10px; }
        .bar-label { width: 150px; font-size: 12px; color: #666; text-align: right; }
        .bar-container { flex: 1; background: #f0f0f0; height: 28px; border-radius: 4px; overflow: hidden; }
        .bar-fill { height: 100%; background: linear-gradient(90deg, #667eea, #764ba2); transition: width 0.5s; display: flex; align-items: center; justify-content: flex-end; padding-right: 8px; color: white; font-size: 11px; font-weight: bold; }
        .trend-badges { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 15px; }
        .trend-badge { padding: 8px 16px; border-radius: 20px; font-size: 12px; font-weight: 600; }
        .trend-badge.emerging { background: #f44336; color: white; }
        .trend-badge.increasing { background: #ff9800; color: white; }
        .trend-badge.stable { background: #4CAF50; color: white; }
        .filters { background: rgba(255,255,255,0.95); padding: 20px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.2); }
        .filter-group { display: inline-block; margin-right: 20px; }
        .filter-group label { font-size: 12px; color: #666; display: block; margin-bottom: 5px; }
        .filter-group select { padding: 8px 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
        .opportunities { display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 20px; }
        .opp-card { background: rgba(255,255,255,0.95); border-radius: 12px; padding: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.2); transition: transform 0.3s; }
        .opp-card:hover { transform: translateY(-5px); }
        .opp-card.emerging { border-left: 4px solid #f44336; }
        .opp-card.increasing { border-left: 4px solid #ff9800; }
        .opp-card.stable { border-left: 4px solid #4CAF50; }
        .opp-header { display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px; }
        .opp-id { background: #667eea; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }
        .opp-score { background: #4CAF50; color: white; padding: 6px 12px; border-radius: 20px; font-size: 14px; font-weight: bold; }
        .opp-score.high { background: #f44336; }
        .opp-score.medium { background: #ff9800; }
        .opp-trend { font-size: 18px; margin-left: 8px; }
        .opp-title { font-size: 16px; color: #333; margin: 10px 0; font-weight: 600; }
        .opp-type { font-size: 12px; color: #666; background: #f0f0f0; padding: 4px 8px; border-radius: 4px; display: inline-block; margin-bottom: 10px; }
        .opp-description { font-size: 13px; color: #555; line-height: 1.5; margin-bottom: 15px; }
        .opp-meta { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 15px; }
        .meta-item { text-align: center; padding: 8px; background: #f5f5f5; border-radius: 6px; }
        .meta-label { font-size: 9px; color: #888; text-transform: uppercase; }
        .meta-value { font-size: 12px; font-weight: 600; color: #333; margin-top: 4px; }
        .meta-value.high { color: #f44336; }
        .meta-value.medium { color: #ff9800; }
        .meta-value.low { color: #4CAF50; }
        .opp-evidence { background: #e3f2fd; padding: 10px; border-radius: 6px; font-size: 12px; color: #1565c0; }
        .opp-evidence strong { display: block; margin-bottom: 5px; }
        .export-btn { position: fixed; bottom: 20px; right: 20px; background: #4CAF50; color: white; padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); }
        .export-btn:hover { background: #45a049; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔬 LIG Research Opportunities Dashboard</h1>
            <p>Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') | Total Opportunities: $($opportunities.Count)</p>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">$($opportunities.Count)</div>
                    <div class="stat-label">Total Opportunities</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">$([Math]::Round($avgScore, 1))</div>
                    <div class="stat-label">Average Score</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">$highImpact</div>
                    <div class="stat-label">High Impact</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">$emergingCount</div>
                    <div class="stat-label">📈 Emerging</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">$highFeasibility</div>
                    <div class="stat-label">High Feasibility</div>
                </div>
            </div>
            
            <div class="trend-badges">
                <div class="trend-badge emerging">📈 Emerging: $emergingCount</div>
                <div class="trend-badge increasing">📊 Increasing: $($byTrend.increasing)</div>
                <div class="trend-badge stable">➡️ Stable: $($byTrend.stable)</div>
            </div>
        </div>
        
        <div class="charts-grid">
            <div class="chart-container">
                <div class="chart-title">
                    <span class="trend-indicator">📈</span>
                    Publication Trend
                </div>
                <div class="line-chart">
                    <svg viewBox="0 0 400 150" preserveAspectRatio="none">
"@

# Generate line chart
if ($paperTrendData.Count -gt 0) {
    $maxVal = ($paperTrendData | Measure-Object -Maximum).Maximum
    if ($maxVal -eq 0) { $maxVal = 1 }
    
    $points = @()
    for ($i = 0; $i -lt $paperTrendData.Count; $i++) {
        $x = ($i / ($paperTrendData.Count - 1)) * 380 + 10
        $y = 140 - (($paperTrendData[$i] / $maxVal) * 120)
        $points += "$x,$y"
    }
    
    $polyline = $points -join " "
    
    $html += "<polyline points=`"$polyline`" class=`"data-line`" />`n"
    
    for ($i = 0; $i -lt $paperTrendData.Count; $i++) {
        $x = ($i / ($paperTrendData.Count - 1)) * 380 + 10
        $y = 140 - (($paperTrendData[$i] / $maxVal) * 120)
        $html += "<circle cx=`"$x`" cy=`"$y`" r=`"5`" class=`"data-point`" />`n"
    }
    
    # Grid lines
    for ($i = 0; $i -le 4; $i++) {
        $y = 20 + ($i * 30)
        $html += "<line x1='10' y1='$y' x2='390' y2='$y' class='grid-line' />`n"
    }
    
    # Y-axis labels
    for ($i = 0; $i -le 4; $i++) {
        $y = 20 + ($i * 30)
        $val = [Math]::Round($maxVal * (1 - $i / 4))
        $html += "<text x='5' y='$([int]$y + 4)' class='axis-label'>$val</text>`n"
    }
    
    # X-axis labels
    for ($i = 0; $i -lt $paperTrendLabels.Count; $i++) {
        $x = ($i / ($paperTrendLabels.Count - 1)) * 380 + 10
        $html += "<text x='$x' y='148' class='axis-label' text-anchor='middle'>$($paperTrendLabels[$i])</text>`n"
    }
}

$html += @"
                    </svg>
                </div>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">
                    <span class="trend-indicator">🔥</span>
                    Hot Topics
                </div>
                <div class="bar-chart">
"@

$maxHotTopic = if ($hotTopicData.Count -gt 0) { ($hotTopicData | Measure-Object -Maximum).Maximum } else { 1 }
if ($maxHotTopic -eq 0) { $maxHotTopic = 1 }

for ($i = 0; $i -lt $hotTopicLabels.Count; $i++) {
    $pct = ($hotTopicData[$i] / $maxHotTopic) * 100
    $html += @"
                    <div class="bar-item">
                        <div class="bar-label">$($hotTopicLabels[$i])</div>
                        <div class="bar-container">
                            <div class="bar-fill" style="width: $pct%">$($hotTopicData[$i])</div>
                        </div>
                    </div>
"@
}

$html += @"
                </div>
            </div>
        </div>
        
        <div class="chart-container">
            <div class="chart-title">📊 Opportunities by Type</div>
            <div class="bar-chart">
"@

foreach ($type in $byType.Keys | Sort-Object) {
    $count = $byType[$type].Count
    $pct = [Math]::Round(($count / $opportunities.Count) * 100)
    $html += @"
                <div class="bar-item">
                    <div class="bar-label">$type</div>
                    <div class="bar-container">
                        <div class="bar-fill" style="width: $pct%">$count ($pct%)</div>
                    </div>
                </div>
"@
}

$html += @"
            </div>
        </div>
        
        <div class="filters">
            <div class="filter-group">
                <label>Filter by Type</label>
                <select id="typeFilter" onchange="filterOpps()">
                    <option value="all">All Types</option>
"@

foreach ($type in $byType.Keys | Sort-Object) {
    $html += "<option value=`"$type`">$type</option>`n"
}

$html += @"
                </select>
            </div>
            <div class="filter-group">
                <label>Filter by Trend</label>
                <select id="trendFilter" onchange="filterOpps()">
                    <option value="all">All Trends</option>
                    <option value="emerging">📈 Emerging</option>
                    <option value="increasing">📊 Increasing</option>
                    <option value="stable">➡️ Stable</option>
                </select>
            </div>
            <div class="filter-group">
                <label>Min Score</label>
                <select id="scoreFilter" onchange="filterOpps()">
                    <option value="0">All Scores</option>
                    <option value="7">7+ (High)</option>
                    <option value="8">8+ (Very High)</option>
                </select>
            </div>
            <div class="filter-group">
                <label>Sort by</label>
                <select id="sortFilter" onchange="filterOpps()">
                    <option value="score">Score</option>
                    <option value="trend">Trend</option>
                    <option value="impact">Impact</option>
                    <option value="type">Type</option>
                </select>
            </div>
        </div>
        
        <div class="opportunities" id="oppGrid">
"@

foreach ($opp in $opportunities) {
    $scoreClass = if ($opp.score -ge 8) { "high" } elseif ($opp.score -ge 7) { "medium" } else { "" }
    $impactClass = $opp.impact.ToLower()
    $feasibilityClass = $opp.feasibility.ToLower()
    $noveltyClass = $opp.novelty.ToLower()
    $trendClass = $opp.trend
    $trendIcon = switch ($opp.trend) {
        "emerging" { "📈" }
        "increasing" { "📊" }
        default { "➡️" }
    }
    
    $evidenceText = if ($opp.evidence) { $opp.evidence -join "; " } else { "N/A" }
    
    $html += @"
            <div class="opp-card $trendClass" data-type="$($opp.type)" data-score="$($opp.score)" data-trend="$($opp.trend)" data-impact="$($opp.impact)">
                <div class="opp-header">
                    <span class="opp-id">$($opp.id)</span>
                    <div>
                        <span class="opp-trend">$trendIcon</span>
                        <span class="opp-score $scoreClass">$($opp.score)/10</span>
                    </div>
                </div>
                <div class="opp-title">$($opp.title)</div>
                <span class="opp-type">$($opp.type)</span>
                <div class="opp-description">$($opp.description)</div>
                
                <div class="opp-meta">
                    <div class="meta-item">
                        <div class="meta-label">Impact</div>
                        <div class="meta-value $impactClass">$($opp.impact)</div>
                    </div>
                    <div class="meta-item">
                        <div class="meta-label">Feasibility</div>
                        <div class="meta-value $feasibilityClass">$($opp.feasibility)</div>
                    </div>
                    <div class="meta-item">
                        <div class="meta-label">Novelty</div>
                        <div class="meta-value $noveltyClass">$($opp.novelty)</div>
                    </div>
                    <div class="meta-item">
                        <div class="meta-label">Trend</div>
                        <div class="meta-value">$($opp.trend)</div>
                    </div>
                </div>
                
                <div class="opp-evidence">
                    <strong>Evidence:</strong>
                    $evidenceText
                </div>
            </div>
"@
}

$html += @"
        </div>
    </div>
    
    <button class="export-btn" onclick="window.print()">📤 Export PDF</button>
    
    <script>
        function filterOpps() {
            const typeFilter = document.getElementById('typeFilter').value;
            const trendFilter = document.getElementById('trendFilter').value;
            const scoreFilter = parseFloat(document.getElementById('scoreFilter').value);
            const sortFilter = document.getElementById('sortFilter').value;
            
            const cards = Array.from(document.querySelectorAll('.opp-card'));
            
            let filtered = cards.filter(card => {
                const type = card.getAttribute('data-type');
                const score = parseFloat(card.getAttribute('data-score'));
                const trend = card.getAttribute('data-trend');
                
                const typeMatch = typeFilter === 'all' || type === typeFilter;
                const trendMatch = trendFilter === 'all' || trend === trendFilter;
                const scoreMatch = score >= scoreFilter;
                
                return typeMatch && trendMatch && scoreMatch;
            });
            
            // Sort
            filtered.sort((a, b) => {
                if (sortFilter === 'score') {
                    return parseFloat(b.getAttribute('data-score')) - parseFloat(a.getAttribute('data-score'));
                } else if (sortFilter === 'trend') {
                    const trendOrder = { 'emerging': 0, 'increasing': 1, 'stable': 2 };
                    return trendOrder[a.getAttribute('data-trend')] - trendOrder[b.getAttribute('data-trend')];
                } else if (sortFilter === 'impact') {
                    const impactOrder = { 'High': 0, 'Medium': 1, 'Low': 2 };
                    return impactOrder[a.getAttribute('data-impact')] - impactOrder[b.getAttribute('data-impact')];
                } else {
                    return a.getAttribute('data-type').localeCompare(b.getAttribute('data-type'));
                }
            });
            
            const grid = document.getElementById('oppGrid');
            filtered.forEach(card => grid.appendChild(card));
        }
    </script>
</body>
</html>
"@

$html | Set-Content $OutputFile -Encoding UTF8
Write-Host "Dashboard saved: $OutputFile" -ForegroundColor Green
Write-Host ""
Write-Host "Done!" -ForegroundColor Green

return @{
    success = $true
    outputFile = $OutputFile
    opportunities = $opportunities.Count
}
