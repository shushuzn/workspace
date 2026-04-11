#!/usr/bin/env node
/**
 * scripts/ci-fix-effectiveness-dashboard.mjs
 * Visualizes fix confidence trends over time using ci-state.json fixHistory.
 * Generates an HTML dashboard — can be deployed to GitHub Pages.
 *
 * Usage:
 *   node scripts/ci-fix-effectiveness-dashboard.mjs              # stdout
 *   node scripts/ci-fix-effectiveness-dashboard.mjs --output <path>
 */
import { existsSync, readFileSync, writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const STATE_FILE = join(__dirname, '..', 'ci-state.json');
const PATTERNS_FILE = join(__dirname, 'ci-failure-patterns.jsonl');
const OUTPUT = process.argv.includes('--output')
  ? process.argv[process.argv.indexOf('--output') + 1]
  : null;

function loadState() {
  if (!existsSync(STATE_FILE)) return {};
  try { return JSON.parse(readFileSync(STATE_FILE, 'utf8')); } catch { return {}; }
}

function loadPatterns() {
  if (!existsSync(PATTERNS_FILE)) return [];
  try {
    const content = readFileSync(PATTERNS_FILE, 'utf8');
    return content.trim().split('\n').filter(Boolean).map(l => {
      try { return JSON.parse(l); } catch { return null; }
    }).filter(Boolean);
  } catch { return []; }
}

function sparklinePath(values, width = 120, height = 28) {
  if (values.length < 2) return { path: '', min: values[0] || 0, max: values[0] || 0 };
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  const step = width / (values.length - 1);
  const points = values.map((v, i) => {
    const x = i * step;
    const y = height - ((v - min) / range) * height;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  });
  return { path: `M ${points.join(' L ')}`, min, max };
}

function confColor(conf) {
  if (conf >= 0.8) return '#22c55e';
  if (conf >= 0.6) return '#eab308';
  return '#ef4444';
}

function confLabel(conf) {
  if (conf === null) return 'N/A';
  return `${(conf * 100).toFixed(0)}%`;
}

function generateHTML(state, patterns) {
  const fixHistory = state?.patterns?.fixHistory || {};
  const lastFixAttempt = state?.patterns?.lastFixAttempt || {};
  const patternNames = Object.keys(fixHistory);

  // Build per-pattern trend data
  const patternData = patternNames.map(name => {
    const events = (fixHistory[name] || []).slice().reverse(); // oldest first for sparkline
    const current = patterns.find(p => p.name === name);
    const last = lastFixAttempt[name];

    // Confidence series: confirmed=1.0, rejected=0.0, applied=0.5
    const confSeries = events.map(ev => {
      if (ev.result === 'confirmed') return 1.0;
      if (ev.result === 'rejected') return 0.0;
      if (ev.result === 'applied') return 0.5;
      return null;
    }).filter(v => v !== null);

    const spark = sparklinePath(confSeries, 120, 28);
    const currentConf = current
      ? (current.confirmations != null && (current.confirmations + current.rejections) > 0
          ? current.confirmations / (current.confirmations + current.rejections)
          : null)
      : null;

    return {
      name,
      events,
      confSeries,
      spark,
      currentConf,
      current,
      last,
      severity: current?.severity || 'P2',
      fix: current?.fix || '—',
      eventCount: events.length,
    };
  }).sort((a, b) => (b.currentConf ?? -1) - (a.currentConf ?? -1));

  // Summary stats
  const totalPatterns = patternData.length;
  const healthyCount = patternData.filter(p => p.currentConf !== null && p.currentConf >= 0.8).length;
  const warnCount = patternData.filter(p => p.currentConf !== null && p.currentConf >= 0.6 && p.currentConf < 0.8).length;
  const badCount = patternData.filter(p => p.currentConf !== null && p.currentConf < 0.6).length;
  const neverUsedCount = patternData.filter(p => p.eventCount === 0).length;

  const recentEvents = Object.entries(fixHistory).flatMap(([name, evs]) =>
    (evs || []).map(ev => ({ name, ...ev }))
  ).sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)).slice(0, 10);

  const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Fix Effectiveness Dashboard</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; padding: 2rem; }
  .container { max-width: 1100px; margin: 0 auto; }
  h1 { font-size: 1.5rem; font-weight: 600; margin-bottom: 1.5rem; color: #f8fafc; }
  h2 { font-size: 0.8rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.06em; color: #64748b; margin-bottom: 0.75rem; }
  h3 { font-size: 0.9rem; font-weight: 500; color: #cbd5e1; margin-bottom: 0.5rem; }

  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 0.75rem; margin-bottom: 2rem; }
  .card { background: #1e293b; border-radius: 10px; padding: 1rem; }
  .card-label { font-size: 0.7rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.3rem; }
  .card-value { font-size: 2rem; font-weight: 700; line-height: 1; }
  .card-sub { font-size: 0.7rem; color: #475569; margin-top: 0.25rem; }

  .pattern-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
  .pattern-card { background: #1e293b; border-radius: 12px; padding: 1.25rem; }
  .pattern-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem; }
  .pattern-name { font-size: 0.85rem; font-weight: 600; color: #f1f5f9; word-break: break-word; }
  .pattern-fix { font-size: 0.7rem; color: #475569; margin-top: 0.25rem; }
  .sev { display: inline-block; padding: 0.1rem 0.4rem; border-radius: 4px; font-size: 0.65rem; font-weight: 600; margin-left: 0.5rem; }
  .sev-P0 { background: #7f1d1d; color: #fca5a5; }
  .sev-P1 { background: #713f12; color: #fde047; }
  .sev-P2 { background: #1e3a5f; color: #93c5fd; }

  .conf-big { font-size: 1.8rem; font-weight: 700; }
  .conf-bar { height: 4px; background: #334155; border-radius: 2px; margin-top: 0.5rem; overflow: hidden; }
  .conf-bar-fill { height: 100%; border-radius: 2px; transition: width 0.3s ease; }

  .sparkline-wrap { margin-top: 0.75rem; }
  .sparkline-wrap svg { width: 100%; overflow: visible; }

  .stats-row { display: flex; gap: 1.5rem; margin-top: 0.5rem; font-size: 0.72rem; color: #64748b; }
  .stat { display: flex; align-items: center; gap: 0.3rem; }
  .stat-dot { width: 6px; height: 6px; border-radius: 50%; display: inline-block; }

  .last-event { font-size: 0.68rem; color: #475569; margin-top: 0.5rem; }
  .last-event .result-confirmed { color: #22c55e; }
  .last-event .result-rejected { color: #ef4444; }
  .last-event .result-applied { color: #3b82f6; }

  .table-card { background: #1e293b; border-radius: 12px; padding: 1.5rem; margin-bottom: 2rem; }
  table { width: 100%; border-collapse: collapse; }
  th, td { text-align: left; padding: 0.5rem 0.75rem; font-size: 0.75rem; }
  th { color: #475569; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid #334155; }
  tr:hover td { background: #263548; }
  td { border-bottom: 1px solid #1e293b; color: #cbd5e1; }
  .badge { display: inline-block; padding: 0.1rem 0.5rem; border-radius: 9999px; font-size: 0.65rem; font-weight: 600; }
  .badge-healthy { background: #14532d; color: #86efac; }
  .badge-warn { background: #713f12; color: #fde047; }
  .badge-bad { background: #7f1d1d; color: #fca5a5; }
  .badge-none { background: #1e293b; color: #64748b; }

  .footer { text-align: center; color: #475569; font-size: 0.7rem; margin-top: 2rem; }

  .empty { text-align: center; padding: 3rem; color: #475569; }
  .empty-icon { font-size: 2rem; margin-bottom: 0.5rem; }
</style>
</head>
<body>
<div class="container">

  <h1>Fix Effectiveness Dashboard</h1>

  <div class="grid">
    <div class="card">
      <div class="card-label">Total Patterns</div>
      <div class="card-value">${totalPatterns}</div>
      <div class="card-sub">with fix history</div>
    </div>
    <div class="card">
      <div class="card-label">Healthy</div>
      <div class="card-value" style="color:#22c55e">${healthyCount}</div>
      <div class="card-sub">≥80% confidence</div>
    </div>
    <div class="card">
      <div class="card-label">Warning</div>
      <div class="card-value" style="color:#eab308">${warnCount}</div>
      <div class="card-sub">60–79% confidence</div>
    </div>
    <div class="card">
      <div class="card-label">Critical</div>
      <div class="card-value" style="color:#ef4444">${badCount}</div>
      <div class="card-sub"><60% confidence</div>
    </div>
    <div class="card">
      <div class="card-label">Never Applied</div>
      <div class="card-value">${neverUsedCount}</div>
      <div class="card-sub">no events recorded</div>
    </div>
  </div>

  ${totalPatterns === 0 ? `
  <div class="empty">
    <div class="empty-icon">🔧</div>
    <div>No fix events recorded yet.</div>
    <div style="font-size:0.75rem;margin-top:0.5rem">Run a fix and it will appear here.</div>
  </div>` : `
  <h2>Pattern Trends</h2>
  <div class="pattern-grid">
  ${patternData.map(p => {
    const conf = p.currentConf;
    const confStr = confLabel(conf);
    const color = confColor(conf);
    const confPct = conf !== null ? `${(conf * 100).toFixed(0)}%` : '0%';
    const lastEv = p.events[p.events.length - 1];
    const lastResultClass = lastEv ? `result-${lastEv.result}` : '';
    const lastDate = lastEv ? new Date(lastEv.timestamp).toLocaleDateString() : 'never';
    const neverUsed = p.eventCount === 0;
    const badgeClass = conf === null ? 'badge-none' : conf >= 0.8 ? 'badge-healthy' : conf >= 0.6 ? 'badge-warn' : 'badge-bad';
    const badgeText = conf === null ? 'N/A' : conf >= 0.8 ? 'Healthy' : conf >= 0.6 ? 'Warning' : 'Critical';

    return `
    <div class="pattern-card">
      <div class="pattern-header">
        <div>
          <div class="pattern-name">${p.name}<span class="sev sev-${p.severity}">${p.severity}</span></div>
          <div class="pattern-fix">${p.fix}</div>
        </div>
      </div>
      <div class="conf-big" style="color:${neverUsed ? '#475569' : color}">${confStr}</div>
      <div class="conf-bar">
        <div class="conf-bar-fill" style="width:${neverUsed ? '0' : confPct}; background:${neverUsed ? '#475569' : color}"></div>
      </div>
      <div class="sparkline-wrap">
        <svg viewBox="0 0 120 30" preserveAspectRatio="none">
          ${!neverUsed && p.confSeries.length >= 2 ? `
          <path d="${p.spark.path}" fill="none" stroke="${color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          ` : `<text x="60" y="18" text-anchor="middle" font-size="8" fill="#475569">no history</text>`}
        </svg>
      </div>
      <div class="stats-row">
        <div class="stat"><span class="stat-dot" style="background:#22c55e"></span>${p.current?.confirmations || 0} confirms</div>
        <div class="stat"><span class="stat-dot" style="background:#ef4444"></span>${p.current?.rejections || 0} rejects</div>
        <div class="stat">${p.eventCount} events</div>
      </div>
      <div class="last-event">
        Last: <span class="${lastResultClass}">${lastEv?.result || 'never'}</span> · ${lastDate}
      </div>
    </div>`;
  }).join('')}
  </div>
  `}

  <div class="table-card">
    <h2>Recent Fix Events</h2>
    <table>
      <thead>
        <tr>
          <th>Pattern</th>
          <th>Result</th>
          <th>Smoke</th>
          <th>Date</th>
          <th>Severity</th>
          <th>Confidence</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
      ${recentEvents.length === 0 ? `
        <tr><td colspan="7" style="text-align:center;color:#475569;padding:2rem">No events recorded yet</td></tr>` : recentEvents.map(ev => {
        const p = patternData.find(x => x.name === ev.name);
        const conf = p?.currentConf;
        const badgeClass = conf === null ? 'badge-none' : conf >= 0.8 ? 'badge-healthy' : conf >= 0.6 ? 'badge-warn' : 'badge-bad';
        const badgeText = conf === null ? 'N/A' : conf >= 0.8 ? 'Healthy' : conf >= 0.6 ? 'Warning' : 'Critical';
        const resultColor = ev.result === 'confirmed' ? '#22c55e' : ev.result === 'rejected' ? '#ef4444' : '#3b82f6';
        const smokeLabel = ev.smokeTest === true ? 'PASS' : ev.smokeTest === false ? 'FAIL' : '—';
        const smokeColor = ev.smokeTest === true ? '#22c55e' : ev.smokeTest === false ? '#ef4444' : '#475569';
        return `
        <tr>
          <td style="font-weight:500;color:#f1f5f9">${ev.name}</td>
          <td style="color:${resultColor};font-weight:600;text-transform:capitalize">${ev.result}</td>
          <td style="color:${smokeColor}">${smokeLabel}</td>
          <td>${new Date(ev.timestamp).toLocaleDateString()}</td>
          <td><span class="sev sev-${p?.severity || 'P2'}">${p?.severity || 'P2'}</span></td>
          <td>${conf !== null ? `${(conf * 100).toFixed(0)}%` : 'N/A'}</td>
          <td><span class="badge ${badgeClass}">${badgeText}</span></td>
        </tr>`;
      }).join('')}
      </tbody>
    </table>
  </div>

  <div class="footer">
    Generated by Fix Effectiveness Dashboard · ${new Date().toISOString()} · Data: ci-state.json + ci-failure-patterns.jsonl
  </div>
</div>
</body>
</html>`;
  return html;
}

async function main() {
  const state = loadState();
  const patterns = loadPatterns();
  const html = generateHTML(state, patterns);
  if (OUTPUT) {
    writeFileSync(OUTPUT, html);
    console.log(`Dashboard written to ${OUTPUT}`);
  } else {
    console.log(html);
  }
}

main().catch(e => { console.error(e); process.exit(1); });
