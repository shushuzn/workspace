#!/usr/bin/env node
/**
 * Cognitive Annealing Visualizer
 * Generates interactive HTML visualization of cognitive annealing process.
 *
 * Reads annealing history from JSON file and produces a self-contained HTML
 * with D3 charts showing temperature, deltaS (concept jump magnitude), and energy.
 *
 * Usage:
 *   node scripts/visualize-annealing.js --input <json> --output <html>
 *   node scripts/visualize-annealing.js --input <json> --open
 */

import * as fs from 'node:fs';
import { fileURLToPath } from 'node:url';
import { execSync } from 'node:child_process';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
import * as path from 'node:path';

const HTML_PIECE1 = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Cognitive Annealing Visualizer</title>
<script src="https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js"></script>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0d1117; color: #e6edf3; padding: 24px; }
  h1 { font-size: 1.5rem; margin-bottom: 8px; color: #58a6ff; }
  .subtitle { color: #8b949e; font-size: 0.875rem; margin-bottom: 24px; }
  .charts { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  .chart { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 16px; }
  .chart h2 { font-size: 0.9rem; color: #8b949e; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.05em; }
  svg { width: 100%; }
  .axis text { fill: #8b949e; font-size: 11px; }
  .axis line, .axis path { stroke: #30363d; }
  .grid line { stroke: #21262d; stroke-dasharray: 2,2; }
  .line-temp { fill: none; stroke: #f97316; stroke-width: 2; }
  .line-delta { fill: none; stroke: #22d3ee; stroke-width: 2; }
  .line-energy { fill: none; stroke: #a78bfa; stroke-width: 2; }
  .dot { fill: #f97316; }
  .dot-delta { fill: #22d3ee; }
  .dot-energy { fill: #a78bfa; }
  .legend { display: flex; gap: 16px; margin-bottom: 16px; }
  .legend-item { display: flex; align-items: center; gap: 6px; font-size: 0.8rem; color: #8b949e; }
  .legend-line { width: 20px; height: 2px; }
  .summary { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 24px; }
  .stat { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 12px; text-align: center; }
  .stat-value { font-size: 1.5rem; font-weight: 600; color: #58a6ff; }
  .stat-label { font-size: 0.75rem; color: #8b949e; margin-top: 4px; }
  .tooltip { position: absolute; background: #21262d; border: 1px solid #30363d; border-radius: 4px; padding: 8px; font-size: 12px; pointer-events: none; }
</style>
</head>
<body>
<h1>Cognitive Annealing Process</h1>
<p class="subtitle">Temperature调度 · ΔS概念跳跃幅度 · 能量曲线</p>

<div class="summary">
  <div class="stat"><div class="stat-value" id="stat-rounds">-</div><div class="stat-label">Rounds</div></div>
  <div class="stat"><div class="stat-value" id="stat-peak-delta">-</div><div class="stat-label">Peak ΔS</div></div>
  <div class="stat"><div class="stat-value" id="stat-final-temp">-</div><div class="stat-label">Final Temp</div></div>
  <div class="stat"><div class="stat-value" id="stat-early-stop">-</div><div class="stat-label">Early Stop</div></div>
</div>

<div class="legend">
  <div class="legend-item"><div class="legend-line" style="background:#f97316"></div>Temperature</div>
  <div class="legend-item"><div class="legend-line" style="background:#22d3ee"></div>ΔS (Concept Jump)</div>
  <div class="legend-item"><div class="legend-line" style="background:#a78bfa"></div>Energy (= ΔS × Temp)</div>
</div>

<div class="charts">
  <div class="chart"><h2>Temperature Schedule</h2><svg id="chart-temp"></svg></div>
  <div class="chart"><h2>ΔS — Concept Jump Magnitude</h2><svg id="chart-delta"></svg></div>
  <div class="chart" style="grid-column: span 2"><h2>Overlay: Temperature · ΔS · Energy</h2><svg id="chart-overlay"></svg></div>
</div>

<script>
const DATA = __DATA__;

function renderLineChart(svgId, data, yAccessor, color, yLabel) {
  const svg = d3.select('#' + svgId);
  const rect = svg.node().getBoundingClientRect();
  const W = rect.width || 600, H = 200;
  const margin = {top: 10, right: 20, bottom: 30, left: 45};
  const iw = W - margin.left - margin.right, ih = H - margin.top - margin.bottom;

  svg.attr('viewBox', '0 0 ' + W + ' ' + H);
  const g = svg.append('g').attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

  const x = d3.scaleLinear().domain([0, data.length-1]).range([0, iw]);
  const maxY = d3.max(data, function(d) { return yAccessor(d); }) || 1;
  const y = d3.scaleLinear().domain([0, maxY * 1.1]).range([ih, 0]);

  g.append('g').attr('class','grid').call(d3.axisLeft(y).tickSize(-iw).tickFormat(''));
  g.append('g').attr('class','axis').attr('transform','translate(0,' + ih + ')').call(d3.axisBottom(x).ticks(5));
  g.append('g').attr('class','axis').call(d3.axisLeft(y));
  g.append('text').attr('transform','rotate(-90)').attr('y',-40).attr('x',-ih/2).attr('text-anchor','middle').attr('fill','#8b949e').attr('font-size','11px').text(yLabel);

  const line = d3.line().x(function(d,i) { return x(i); }).y(function(d) { return y(yAccessor(d)); });
  g.append('path').datum(data).attr('class','line').attr('d',line).style('fill','none').style('stroke',color).style('stroke-width','2');
  g.selectAll('.dot').data(data.filter(function(d) { return yAccessor(d) > 0; })).enter().append('circle').attr('class','dot').attr('cx',function(d,i) { return x(i); }).attr('cy',function(d) { return y(yAccessor(d)); }).attr('r',3).style('fill',color);
}

function renderOverlay() {
  var svg = d3.select('#chart-overlay');
  var rect = svg.node().getBoundingClientRect();
  var W = rect.width || 800, H = 220;
  var margin = {top: 10, right: 60, bottom: 30, left: 45};
  var iw = W - margin.left - margin.right, ih = H - margin.top - margin.bottom;

  svg.attr('viewBox', '0 0 ' + W + ' ' + H);
  var g = svg.append('g').attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

  var allVals = DATA.map(function(d) { return d.temp; })
    .concat(DATA.map(function(d) { return d.deltaS || 0; }))
    .concat(DATA.map(function(d) { return d.energy || 0; }));
  var maxAll = d3.max(allVals) || 1;
  var yScale = d3.scaleLinear().domain([0, maxAll * 1.1]).range([ih, 0]);
  var xScale = d3.scaleLinear().domain([0, DATA.length-1]).range([0, iw]);

  g.append('g').attr('class','grid').call(d3.axisLeft(yScale).tickSize(-iw).tickFormat(''));
  g.append('g').attr('class','axis').attr('transform','translate(0,' + ih + ')').call(d3.axisBottom(xScale).ticks(8));
  g.append('g').attr('class','axis').call(d3.axisLeft(yScale));

  // Temperature
  var tLine = d3.line().x(function(d,i) { return xScale(i); }).y(function(d) { return yScale(d.temp); });
  g.append('path').datum(DATA).attr('d',tLine).style('fill','none').style('stroke','#f97316').style('stroke-width','2');

  // Delta S
  var dLine = d3.line().x(function(d,i) { return xScale(i); }).y(function(d) { return yScale(d.deltaS || 0); });
  g.append('path').datum(DATA).attr('d',dLine).style('fill','none').style('stroke','#22d3ee').style('stroke-width','2');

  // Energy
  var eLine = d3.line().x(function(d,i) { return xScale(i); }).y(function(d) { return yScale(d.energy || 0); });
  g.append('path').datum(DATA).attr('d',eLine).style('fill','none').style('stroke','#a78bfa').style('stroke-width','2');

  // Legend
  var legend = svg.append('g').attr('transform', 'translate(' + (W-margin.right+10) + ',' + margin.top + ')');
  [['#f97316','Temp'],['#22d3ee','ΔS'],['#a78bfa','Energy']].forEach(function(item, i) {
    legend.append('line').attr('x1',0).attr('y1',i*20).attr('x2',20).attr('y2',i*20).style('stroke',item[0]).style('stroke-width','2');
    legend.append('text').attr('x',25).attr('y',i*20+4).text(item[1]).attr('fill','#8b949e').attr('font-size','11px');
  });
}

DATA.forEach(function(d, i) {
  d.energy = (d.deltaS || 0) * (d.temp || 0);
});

document.getElementById('stat-rounds').textContent = DATA.length;
document.getElementById('stat-peak-delta').textContent = d3.max(DATA, function(d) { return d.deltaS || 0; }).toFixed(3);
document.getElementById('stat-final-temp').textContent = (DATA[DATA.length-1] ? DATA[DATA.length-1].temp : 0).toFixed(3);
document.getElementById('stat-early-stop').textContent = DATA.some(function(d) { return d.plateau; }) ? 'Yes' : 'No';

renderLineChart('chart-temp', DATA, function(d) { return d.temp; }, '#f97316', 'Temperature');
renderLineChart('chart-delta', DATA, function(d) { return d.deltaS || 0; }, '#22d3ee', 'ΔS');
renderOverlay();
</script>
</body>
</html>`;

const HTML_PIECE2 = ``;

async function main() {
  const args = process.argv.slice(2);
  let inputFile, outputFile, open = false;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--input' && args[i+1]) inputFile = args[++i];
    else if (args[i] === '--output' && args[i+1]) outputFile = args[++i];
    else if (args[i] === '--open') open = true;
  }

  if (!inputFile) {
    console.log('Usage: node visualize-annealing.js --input <json> --output <html> [--open]');
    process.exit(1);
  }

  const raw = fs.readFileSync(inputFile, 'utf-8');
  const data = JSON.parse(raw);

  const html = HTML_PIECE1.replace('"__DATA__"', JSON.stringify(data));

  if (outputFile) {
    fs.writeFileSync(outputFile, html);
    console.log('Written: ' + outputFile);
  } else {
    process.stdout.write(html);
  }

  if (open && outputFile) {
    const cmd = process.platform === 'win32' ? 'start' : process.platform === 'darwin' ? 'open' : 'xdg-open';
    execSync(cmd + ' "' + outputFile + '"', { stdio: 'ignore' });
  }
}

main().catch(e => { console.error(e); process.exit(1); });
