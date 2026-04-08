#!/usr/bin/env node
/**
 * OMC Learning Dashboard
 * Reads audit log, patterns, trajectories → generates markdown dashboard.
 *
 * Usage:
 *   node hook-dashboard.mjs           Show markdown dashboard
 *   node hook-dashboard.mjs --html    Output HTML dashboard
 *   node hook-dashboard.mjs --watch   Auto-refresh every 30s
 */
import { existsSync, readFileSync, writeFileSync, readdirSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const STATE_DIR = resolve(__dirname, '../state');
const AUDIT_LOG = resolve(STATE_DIR, 'hook-audit.jsonl');
const PATTERNS = resolve(STATE_DIR, 'agentdb-patterns.jsonl');
const TRAJ_DIR = resolve(__dirname, '../trajectories');
const OUTPUT = resolve(STATE_DIR, 'dashboard.md');

// ── Read audit log ───────────────────────────────────────────────────────────
function readAudit() {
  if (!existsSync(AUDIT_LOG)) return [];
  return readFileSync(AUDIT_LOG, 'utf-8')
    .split('\n').filter(Boolean)
    .map(l => { try { return JSON.parse(l); } catch { return null; } })
    .filter(Boolean);
}

// ── Read patterns ────────────────────────────────────────────────────────────
function readPatterns() {
  if (!existsSync(PATTERNS)) return [];
  return readFileSync(PATTERNS, 'utf-8')
    .split('\n').filter(Boolean)
    .map(l => { try { return JSON.parse(l); } catch { return null; } })
    .filter(Boolean);
}

// ── Read recent trajectories ─────────────────────────────────────────────────
function readTrajectories() {
  if (!existsSync(TRAJ_DIR)) return [];
  const files = readdirSync(TRAJ_DIR).filter(f => f.endsWith('.md')).sort().slice(-5);
  return files.map(f => ({
    name: f,
    content: readFileSync(resolve(TRAJ_DIR, f), 'utf-8'),
  }));
}

// ── Stats ─────────────────────────────────────────────────────────────────
function computeStats(audit) {
  const today = new Date().toISOString().split('T')[0];
  const todayEntries = audit.filter(e => e.timestamp?.startsWith(today));
  const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0];
  const yesterdayEntries = audit.filter(e => e.timestamp?.startsWith(yesterday));

  const toolCounts = {};
  const errorCmds = [];
  const todayErrors = [];

  for (const e of audit) {
    toolCounts[e.tool] = (toolCounts[e.tool] || 0) + 1;
    if ((e.exitCode !== null && e.exitCode !== 0) || e.error) {
      errorCmds.push(e);
      if (e.timestamp?.startsWith(today)) todayErrors.push(e);
    }
  }

  const topTools = Object.entries(toolCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8)
    .map(([t, c]) => ({ tool: t, count: c }));

  const totalSessions = new Set(audit.map(e => e.sessionId).filter(Boolean)).size;

  return {
    total: audit.length,
    today: todayEntries.length,
    yesterday: yesterdayEntries.length,
    errorCount: errorCmds.length,
    todayErrors: todayErrors.length,
    topTools,
    totalSessions,
    toolCount: Object.keys(toolCounts).length,
  };
}

function computePatternStats(patterns) {
  const byType = {};
  for (const p of patterns) {
    byType[p.patternType] = (byType[p.patternType] || 0) + 1;
  }
  return { total: patterns.length, byType };
}

// ── Markdown dashboard ──────────────────────────────────────────────────────
function renderMarkdown(stats, patternStats, trajectories, errors) {
  const now = new Date().toISOString();
  let md = `# OMC Learning Dashboard

*Generated: ${now}*

## Activity Overview

| Metric | Value |
|--------|-------|
| Total tool calls logged | ${stats.total.toLocaleString()} |
| Sessions tracked | ${stats.totalSessions} |
| Unique tools used | ${stats.toolCount} |
| Today's tool calls | ${stats.today} |
| Yesterday's tool calls | ${stats.yesterday} |
| Delta (today vs yesterday) | ${stats.today >= stats.yesterday ? '+' : ''}${stats.today - stats.yesterday} |
| Errors (all time) | ${stats.errorCount} |
| Errors (today) | ${stats.todayErrors} |
| Error rate | ${stats.total > 0 ? ((stats.errorCount / stats.total) * 100).toFixed(1) : '0'}% |

## Top Tools

${stats.topTools.length > 0
  ? stats.topTools.map(t => `| \`${t.tool}\` | ${t.count} |`).join('\n')
  : '| _none yet_ |'}

## Top Tools (chart)

${stats.topTools.slice(0, 8).map(t => {
  const bar = '█'.repeat(Math.round(t.count / Math.max(...stats.topTools.map(x => x.count)) * 20));
  return `\`${t.tool.padEnd(20)}\` ${bar} ${t.count}`;
}).join('\n')}

## Patterns Learned

| Type | Count |
|------|-------|
${Object.entries(patternStats.byType)
  .sort((a, b) => b[1] - a[1])
  .map(([type, count]) => `| ${type} | ${count} |`)
  .join('\n')}
${patternStats.total === 0 ? '| _none yet_ |' : ''}

## Recent Errors

${errors.length > 0
  ? errors.slice(-5).reverse().map(e =>
    `- \`${(e.tool_input_preview || e.tool || '?').slice(0, 60)}\` → ${e.error || `exit ${e.exitCode}`} (\`${e.timestamp?.split('T')[0]}\`)`
  ).join('\n')
  : '_none yet_'}

## Recent Trajectories

${trajectories.length > 0
  ? trajectories.map(t => `### ${t.name}\n\n${t.content.split('\n').slice(0, 20).join('\n')}${t.content.split('\n').length > 20 ? '\n\n_(truncated)_' : ''}`).join('\n\n---\n\n')
  : '_no trajectories yet — run hook-session-end-drain.mjs_'}

## Quick Links

| Action | Command |
|--------|---------|
| Force drain + trajectory | \`node .omc/scripts/hook-session-end-drain.mjs\` |
| Process MCP queue | \`node .omc/scripts/hook-mcp-consumer.mjs\` |
| Refresh dashboard | \`node .omc/scripts/hook-dashboard.mjs\` |
| Audit log | \`.omc/state/hook-audit.jsonl\` |
| Pattern store | \`.omc/state/agentdb-patterns.jsonl\` |
`;

  return md;
}

// ── HTML dashboard ──────────────────────────────────────────────────────────
function renderHTML(stats, patternStats, trajectories, errors) {
  const bars = stats.topTools.slice(0, 8).map(t => {
    const pct = stats.topTools.length > 0 ? (t.count / Math.max(...stats.topTools.map(x => x.count)) * 100) : 0;
    return `<div class="bar-row"><span class="bar-label">${t.tool}</span><div class="bar"><div class="bar-fill" style="width:${pct}%"></div></div><span class="bar-count">${t.count}</span></div>`;
  }).join('\n');

  const patternRows = Object.entries(patternStats.byType)
    .sort((a, b) => b[1] - a[1])
    .map(([type, count]) => `<tr><td>${type}</td><td>${count}</td></tr>`).join('');

  const errorRows = errors.slice(-10).reverse().map(e =>
    `<tr><td>${(e.timestamp || '').split('T')[0]}</td><td><code>${(e.tool_input_preview || e.tool || '?').slice(0, 50)}</code></td><td>${e.error || `exit ${e.exitCode}`}</td></tr>`
  ).join('');

  return `<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<title>OMC Learning Dashboard</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Segoe UI', system-ui, sans-serif; background: #0f1117; color: #e2e8f0; padding: 24px; }
  h1 { color: #60a5fa; margin-bottom: 4px; }
  .subtitle { color: #64748b; font-size: 13px; margin-bottom: 24px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }
  .card { background: #1e293b; border-radius: 10px; padding: 18px; border: 1px solid #334155; }
  .card-label { font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: .05em; margin-bottom: 6px; }
  .card-value { font-size: 28px; font-weight: 700; color: #f1f5f9; }
  .card-value.warn { color: #fbbf24; }
  .card-value.error { color: #f87171; }
  .card-value.good { color: #4ade80; }
  .section { background: #1e293b; border-radius: 10px; padding: 20px; border: 1px solid #334155; margin-bottom: 20px; }
  h2 { color: #94a3b8; font-size: 13px; text-transform: uppercase; letter-spacing: .05em; margin-bottom: 16px; border-bottom: 1px solid #334155; padding-bottom: 8px; }
  .bar-row { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; font-size: 13px; font-family: monospace; }
  .bar-label { width: 140px; color: #94a3b8; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .bar { flex: 1; height: 16px; background: #334155; border-radius: 3px; overflow: hidden; }
  .bar-fill { height: 100%; background: linear-gradient(90deg, #3b82f6, #60a5fa); border-radius: 3px; transition: width .3s; }
  .bar-count { width: 40px; text-align: right; color: #e2e8f0; }
  table { width: 100%; border-collapse: collapse; font-size: 13px; }
  th { color: #64748b; text-align: left; padding: 8px 12px; border-bottom: 1px solid #334155; }
  td { padding: 8px 12px; border-bottom: 1px solid #1e293b; }
  tr:last-child td { border-bottom: none; }
  code { background: #334155; padding: 2px 6px; border-radius: 4px; font-size: 12px; }
  .delta-pos { color: #4ade80; }
  .delta-neg { color: #f87171; }
  .refresh { color: #64748b; font-size: 12px; }
</style></head><body>
<h1>OMC Learning Dashboard</h1>
<p class="subtitle">Generated: ${new Date().toLocaleString()} &nbsp;|&nbsp; <span class="refresh">Auto-refresh: 30s</span></p>

<div class="grid">
  <div class="card"><div class="card-label">Total Tool Calls</div><div class="card-value">${stats.total.toLocaleString()}</div></div>
  <div class="card"><div class="card-label">Sessions</div><div class="card-value">${stats.totalSessions}</div></div>
  <div class="card"><div class="card-label">Today</div><div class="card-value">${stats.today}</div></div>
  <div class="card"><div class="card-label">Yesterday</div><div class="card-value">${stats.yesterday}</div></div>
  <div class="card"><div class="card-label">Delta</div><div class="card-value ${stats.today >= stats.yesterday ? 'good' : 'error'}">${stats.today >= stats.yesterday ? '+' : ''}${stats.today - stats.yesterday}</div></div>
  <div class="card"><div class="card-label">Errors (all time)</div><div class="card-value ${stats.errorCount > 0 ? 'warn' : 'good'}">${stats.errorCount}</div></div>
  <div class="card"><div class="card-label">Errors (today)</div><div class="card-value ${stats.todayErrors > 0 ? 'error' : 'good'}">${stats.todayErrors}</div></div>
  <div class="card"><div class="card-label">Patterns Learned</div><div class="card-value">${patternStats.total}</div></div>
</div>

<div class="grid">
  <div class="section">
    <h2>Top Tools</h2>
    ${bars}
  </div>
  <div class="section">
    <h2>Patterns by Type</h2>
    <table><thead><tr><th>Type</th><th>Count</th></tr></thead><tbody>
    ${patternRows || '<tr><td colspan="2" style="color:#64748b">none yet</td></tr>'}
    </tbody></table>
  </div>
</div>

<div class="section">
  <h2>Recent Errors</h2>
  ${errorRows ? `<table><thead><tr><th>Date</th><th>Command</th><th>Error</th></tr></thead><tbody>${errorRows}</tbody></table>` : '<p style="color:#64748b">none yet</p>'}
</div>

<script>
  setTimeout(() => location.reload(), 30000);
</script>
</body></html>`;
}

// ── Main ─────────────────────────────────────────────────────────────────────
function main() {
  const args = {};
  for (let i = 0; i < process.argv.length; i++) {
    if (process.argv[i].startsWith('--')) {
      const k = process.argv[i].slice(2);
      args[k] = process.argv[i + 1] && !process.argv[i + 1].startsWith('--') ? process.argv[++i] : true;
    }
  }

  const audit = readAudit();
  const patterns = readPatterns();
  const trajectories = readTrajectories();
  const errors = audit.filter(e => (e.exitCode !== null && e.exitCode !== 0) || e.error);

  const stats = computeStats(audit);
  const patternStats = computePatternStats(patterns);

  if (args.html) {
    const html = renderHTML(stats, patternStats, trajectories, errors);
    const out = args.html === true ? resolve(STATE_DIR, 'dashboard.html') : args.html;
    writeFileSync(out, html, 'utf-8');
    console.log(`[dashboard] HTML → ${out}`);
  } else {
    const md = renderMarkdown(stats, patternStats, trajectories, errors);
    const out = args.output || OUTPUT;
    writeFileSync(out, md, 'utf-8');
    console.log(`[dashboard] Markdown → ${out}`);
    console.log(md);
  }
}

main();
