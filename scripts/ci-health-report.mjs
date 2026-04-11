#!/usr/bin/env node
/**
 * scripts/ci-health-report.mjs
 * Generates CI health HTML dashboard from ci-health-history.jsonl.
 * Static file — can be deployed to GitHub Pages.
 *
 * Usage:
 *   node scripts/ci-health-report.mjs              # generate to stdout
 *   node scripts/ci-health-report.mjs --output <path>  # write to file
 */
import { existsSync, readFileSync, writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const HISTORY_FILE = join(__dirname, '..', 'ci-health-history.jsonl');
const OUTPUT = process.argv.includes('--output')
  ? process.argv[process.argv.indexOf('--output') + 1]
  : null;

function loadHistory() {
  if (!existsSync(HISTORY_FILE)) return [];
  try {
    const content = readFileSync(HISTORY_FILE, 'utf8');
    return content.trim().split('\n').filter(Boolean).map(l => {
      try { return JSON.parse(l); } catch { return null; }
    }).filter(Boolean);
  } catch { return []; }
}

function sparkline(values, width = 60, height = 20) {
  if (values.length < 2) return { path: '', labels: [] };
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  const step = width / (values.length - 1);
  const points = values.map((v, i) => {
    const x = i * step;
    const y = height - ((v - min) / range) * height;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  });
  return {
    path: `M ${points.join(' L ')}`,
    min, max,
    labels: [min, max]
  };
}

function scoreColor(score) {
  if (score >= 80) return '#22c55e';
  if (score >= 60) return '#eab308';
  return '#ef4444';
}

function generateHTML(history) {
  const latest = history[history.length - 1];
  const scores = history.map(h => h.score);
  const avgScore = scores.length ? (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1) : 'N/A';

  // Last 30 entries for chart
  const chartData = history.slice(-30);
  const chartScores = chartData.map(h => h.score);
  const spark = sparkline(chartScores, 120, 30);

  // Time-series for SVG chart (wider)
  const tsScores = history.slice(-90).map(h => h.score);
  const tsSpark = sparkline(tsScores, 600, 80);

  const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CI Health Dashboard</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; padding: 2rem; }
  .container { max-width: 1100px; margin: 0 auto; }
  h1 { font-size: 1.5rem; font-weight: 600; margin-bottom: 1.5rem; color: #f8fafc; }
  h2 { font-size: 0.85rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b; margin-bottom: 0.75rem; }

  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
  .card { background: #1e293b; border-radius: 12px; padding: 1.25rem; }
  .card-label { font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem; }
  .card-value { font-size: 2.5rem; font-weight: 700; line-height: 1; }
  .card-sub { font-size: 0.75rem; color: #64748b; margin-top: 0.25rem; }

  .chart-card { grid-column: 1 / -1; background: #1e293b; border-radius: 12px; padding: 1.5rem; }
  .chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
  .chart-svg { width: 100%; overflow: visible; }

  .score-bar { height: 6px; background: #334155; border-radius: 3px; margin-top: 0.75rem; overflow: hidden; }
  .score-bar-fill { height: 100%; border-radius: 3px; transition: width 0.3s ease; }

  table { width: 100%; border-collapse: collapse; }
  th, td { text-align: left; padding: 0.5rem 0.75rem; font-size: 0.8rem; }
  th { color: #64748b; font-weight: 500; text-transform: uppercase; letter-spacing: 0.04em; border-bottom: 1px solid #334155; }
  tr:hover td { background: #1e293b; }
  td { border-bottom: 1px solid #1e293b; }
  .score-cell { font-weight: 600; }
  .badge { display: inline-block; padding: 0.1rem 0.5rem; border-radius: 9999px; font-size: 0.7rem; font-weight: 500; }
  .badge-good { background: #166534; color: #86efac; }
  .badge-warn { background: #854d0e; color: #fde047; }
  .badge-bad { background: #991b1b; color: #fca5a5; }

  .trend-good { color: #22c55e; }
  .trend-warn { color: #eab308; }
  .trend-bad { color: #ef4444; }

  .footer { text-align: center; color: #475569; font-size: 0.7rem; margin-top: 2rem; }
</style>
</head>
<body>
<div class="container">

  <h1>CI Health Dashboard</h1>

  <div class="grid">
    <div class="card">
      <div class="card-label">Latest Score</div>
      <div class="card-value" style="color: ${scoreColor(latest?.score || 0)}">${latest?.score ?? '—'}</div>
      <div class="card-sub">${latest ? new Date(latest.timestamp).toLocaleDateString() : 'No data'}</div>
      <div class="score-bar">
        <div class="score-bar-fill" style="width:${latest?.score || 0}%; background:${scoreColor(latest?.score || 0)}"></div>
      </div>
    </div>
    <div class="card">
      <div class="card-label">Average (all time)</div>
      <div class="card-value" style="color: ${scoreColor(Number(avgScore) || 0)}">${avgScore}</div>
      <div class="card-sub">${history.length} runs recorded</div>
    </div>
    <div class="card">
      <div class="card-label">Best</div>
      <div class="card-value" style="color: #22c55e">${scores.length ? Math.max(...scores) : '—'}</div>
      <div class="card-sub">${history.length ? new Date(history.find(h => h.score === Math.max(...scores))?.timestamp).toLocaleDateString() : 'N/A'}</div>
    </div>
    <div class="card">
      <div class="card-label">Worst</div>
      <div class="card-value" style="color: #ef4444">${scores.length ? Math.min(...scores) : '—'}</div>
      <div class="card-sub">${history.length ? new Date(history.find(h => h.score === Math.min(...scores))?.timestamp).toLocaleDateString() : 'N/A'}</div>
    </div>
  </div>

  <div class="chart-card">
    <div class="chart-header">
      <h2>Score Trend (last 90 runs)</h2>
      <span style="color: #64748b; font-size: 0.75rem">Min ${spark.min?.toFixed(0)} — Max ${spark.max?.toFixed(0)}</span>
    </div>
    <svg class="chart-svg" viewBox="0 0 600 90" preserveAspectRatio="none">
      <!-- Grid lines -->
      <line x1="0" y1="45" x2="600" y2="45" stroke="#334155" stroke-width="0.5" stroke-dasharray="4,4"/>
      <!-- Score line -->
      <path d="${tsSpark.path}" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      <!-- Area fill -->
      <path d="${tsSpark.path} L 600,80 L 0,80 Z" fill="url(#scoreGradient)" opacity="0.3"/>
      <defs>
        <linearGradient id="scoreGradient" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#3b82f6"/>
          <stop offset="100%" stop-color="#3b82f6" stop-opacity="0"/>
        </linearGradient>
      </defs>
    </svg>
  </div>

  <div class="chart-card">
    <h2>Recent Runs</h2>
    <table>
      <thead>
        <tr>
          <th>Date</th>
          <th>Score</th>
          <th>Pass Rate</th>
          <th>Coverage</th>
          <th>MTTR</th>
          <th>Pattern Conf</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
${history.slice(-20).reverse().map(h => {
  const badge = h.score >= 80 ? 'badge-good' : h.score >= 60 ? 'badge-warn' : 'badge-bad';
  const badgeText = h.score >= 80 ? 'Healthy' : h.score >= 60 ? 'Attention' : 'Critical';
  return `        <tr>
  <td>${new Date(h.timestamp).toLocaleDateString()}</td>
  <td class="score-cell" style="color: ${scoreColor(h.score)}">${h.score}</td>
  <td>${h.passRate != null ? `${(h.passRate * 100).toFixed(0)}%` : '—'}</td>
  <td>${h.avgCoverage != null ? `${h.avgCoverage.toFixed(1)}%` : '—'}</td>
  <td>${h.mttr != null ? `${h.mttr.toFixed(0)}h` : '—'}</td>
  <td>${h.patternConfidence != null ? `${(h.patternConfidence * 100).toFixed(0)}%` : '—'}</td>
  <td><span class="badge ${badge}">${badgeText}</span></td>
</tr>`;
}).join('\n')}
      </tbody>
    </table>
  </div>

  <div class="footer">
    Generated by CI Health Report · ${new Date().toISOString()} · Data source: ci-health-history.jsonl
  </div>
</div>
</body>
</html>`;
  return html;
}

async function main() {
  const history = loadHistory();
  const html = generateHTML(history);
  if (OUTPUT) {
    writeFileSync(OUTPUT, html);
    console.log(`Dashboard written to ${OUTPUT}`);
  } else {
    console.log(html);
  }
}

main().catch(e => { console.error(e); process.exit(1); });
