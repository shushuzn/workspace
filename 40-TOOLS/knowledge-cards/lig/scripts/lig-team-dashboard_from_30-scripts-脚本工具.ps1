#!/usr/bin/env pwsh
# LIG Research Team Dashboard Generator
# Creates interactive HTML visualization of author collaboration network

param(
    [string]$NetworkFile,
    [string]$TeamsFile,
    [string]$MetricsFile,
    [string]$OutputFile = "21-reports/LIG-Team-Dashboard.html"
)

$ErrorActionPreference = "Stop"

Write-Host "LIG Research Team Dashboard Generator" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Load data
if (!$NetworkFile -or !$TeamsFile -or !$MetricsFile) {
    $latestFiles = Get-ChildItem -Path "21-reports" -Filter "LIG-Author-*.json" | 
                   Sort-Object LastWriteTime -Descending | 
                   Select-Object -First 3
    
    if ($latestFiles.Count -lt 3) {
        Write-Host "ERROR: Not enough data files found" -ForegroundColor Red
        exit 1
    }
    
    $NetworkFile = $latestFiles[0].FullName
    $TeamsFile = $latestFiles[1].FullName
    $MetricsFile = $latestFiles[2].FullName
}

Write-Host "Loading network data..." -ForegroundColor Gray
$network = Get-Content $NetworkFile | ConvertFrom-Json
$teams = Get-Content $TeamsFile | ConvertFrom-Json
$metrics = Get-Content $MetricsFile | ConvertFrom-Json

Write-Host "  Network: $($network.nodes.Count) nodes, $($network.links.Count) links" -ForegroundColor Green
Write-Host "  Teams: $($teams.Count)" -ForegroundColor Green
Write-Host "  Authors: $($metrics.Count)" -ForegroundColor Green
Write-Host ""

# Calculate stats
$totalAuthors = $metrics.Count
$totalPapers = ($metrics | Measure-Object -Property paper_count -Sum).Sum
$totalCollabs = ($network.links | Measure-Object -Property value -Sum).Sum
$avgPapers = [Math]::Round($totalPapers / $totalAuthors, 2)
$topAuthor = $metrics | Sort-Object -Property paper_count -Descending | Select-Object -First 1

# Generate HTML
$html = @"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LIG Research Team Dashboard</title>
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
        .main-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; margin-bottom: 20px; }
        .panel { background: rgba(255,255,255,0.95); padding: 20px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.2); }
        .panel-title { font-size: 16px; color: #333; margin-bottom: 15px; font-weight: 600; display: flex; align-items: center; gap: 8px; }
        .network-viz { width: 100%; height: 500px; border: 1px solid #e0e0e0; border-radius: 8px; background: #fafafa; }
        .team-list { max-height: 500px; overflow-y: auto; }
        .team-card { background: #f5f5f5; padding: 12px; border-radius: 6px; margin-bottom: 10px; border-left: 4px solid #667eea; }
        .team-card:hover { background: #e8e8e8; }
        .team-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
        .team-size { background: #667eea; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold; }
        .team-papers { font-size: 12px; color: #666; }
        .team-members { font-size: 12px; color: #555; line-height: 1.4; }
        .author-table { width: 100%; border-collapse: collapse; font-size: 12px; }
        .author-table th { text-align: left; padding: 10px; background: #f0f0f0; border-bottom: 2px solid #ddd; }
        .author-table td { padding: 8px 10px; border-bottom: 1px solid #eee; }
        .author-table tr:hover { background: #f5f5f5; }
        .rank-badge { background: #667eea; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: bold; }
        .rank-1 { background: #ffd700; }
        .rank-2 { background: #c0c0c0; }
        .rank-3 { background: #cd7f32; }
        .export-btn { position: fixed; bottom: 20px; right: 20px; background: #4CAF50; color: white; padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); }
        .export-btn:hover { background: #45a049; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔬 LIG Research Team Dashboard</h1>
            <p>Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') | Analysis of $($metrics.Count) authors from $($totalPapers) papers</p>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">$($metrics.Count)</div>
                    <div class="stat-label">Total Authors</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">$totalPapers</div>
                    <div class="stat-label">Total Papers</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">$($network.links.Count)</div>
                    <div class="stat-label">Collaboration Links</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">$($teams.Count)</div>
                    <div class="stat-label">Research Teams</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">$avgPapers</div>
                    <div class="stat-label">Avg Papers/Author</div>
                </div>
            </div>
        </div>
        
        <div class="main-grid">
            <div class="panel">
                <div class="panel-title">🕸️ Author Collaboration Network</div>
                <div id="network" class="network-viz"></div>
            </div>
            
            <div class="panel">
                <div class="panel-title">👥 Research Teams</div>
                <div class="team-list">
"@

foreach ($team in $teams) {
    $members = ($team.members | Select-Object -First 5) -join ", "
    if ($team.members.Count -gt 5) {
        $members += "..."
    }
    
    $html += @"
                    <div class="team-card">
                        <div class="team-header">
                            <span class="team-size">$($team.size) members</span>
                            <span class="team-papers">$($team.total_papers) papers</span>
                        </div>
                        <div class="team-members">$members</div>
                    </div>
"@
}

$html += @"
                </div>
            </div>
        </div>
        
        <div class="panel">
            <div class="panel-title">📊 Top 20 Authors by Publication Count</div>
            <table class="author-table">
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Author</th>
                        <th>Papers</th>
                        <th>Collaborators</th>
                        <th>Avg Collaborations</th>
                    </tr>
                </thead>
                <tbody>
"@

$top20 = $metrics | Sort-Object -Property paper_count -Descending | Select-Object -First 20
for ($i = 0; $i -lt $top20.Count; $i++) {
    $author = $top20[$i]
    $rank = $i + 1
    $rankClass = ""
    if ($rank -eq 1) { $rankClass = "rank-1" }
    elseif ($rank -eq 2) { $rankClass = "rank-2" }
    elseif ($rank -eq 3) { $rankClass = "rank-3" }
    
    $html += @"
                    <tr>
                        <td><span class="rank-badge $rankClass">#$rank</span></td>
                        <td><strong>$($author.name)</strong></td>
                        <td>$($author.paper_count)</td>
                        <td>$($author.collaborator_count)</td>
                        <td>$($author.avg_collaborations)</td>
                    </tr>
"@
}

$html += @"
                </tbody>
            </table>
        </div>
    </div>
    
    <button class="export-btn" onclick="window.print()">📤 Export PDF</button>
    
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script>
        // Network visualization
        const networkData = {
            nodes: $(($network.nodes | ConvertTo-Json -Compress)),
            links: $(($network.links | ConvertTo-Json -Compress))
        };
        
        const width = document.getElementById('network').clientWidth;
        const height = 500;
        
        const svg = d3.select('#network')
            .append('svg')
            .attr('width', width)
            .attr('height', height)
            .attr('viewBox', [0, 0, width, height]);
        
        // Add zoom
        svg.call(d3.zoom().on('zoom', (event) => {
            g.attr('transform', event.transform);
        }));
        
        const g = svg.append('g');
        
        // Create force simulation
        const simulation = d3.forceSimulation(networkData.nodes)
            .force('link', d3.forceLink(networkData.links).id(d => d.id).distance(80))
            .force('charge', d3.forceManyBody().strength(-200))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collide', d3.forceCollide(20));
        
        // Draw links
        const link = g.append('g')
            .selectAll('line')
            .data(networkData.links)
            .join('line')
            .attr('stroke', '#999')
            .attr('stroke-opacity', 0.6)
            .attr('stroke-width', d => Math.sqrt(d.value));
        
        // Draw nodes
        const node = g.append('g')
            .selectAll('circle')
            .data(networkData.nodes)
            .join('circle')
            .attr('r', d => 5 + Math.sqrt(d.papers) * 2)
            .attr('fill', '#667eea')
            .attr('stroke', '#fff')
            .attr('stroke-width', 2)
            .call(d3.drag()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended));
        
        // Add tooltips
        node.append('title')
            .text(d => `${d.id}: ${d.papers} papers, ${d.collaborators} collaborators`);
        
        // Add labels
        const label = g.append('g')
            .selectAll('text')
            .data(networkData.nodes)
            .join('text')
            .text(d => d.id)
            .attr('font-size', '10px')
            .attr('fill', '#333')
            .attr('dx', 12)
            .attr('dy', 4);
        
        simulation.on('tick', () => {
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);
            
            node
                .attr('cx', d => d.x)
                .attr('cy', d => d.y);
            
            label
                .attr('x', d => d.x)
                .attr('y', d => d.y);
        });
        
        function dragstarted(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }
        
        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }
        
        function dragended(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
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
}
