/**
 * workspace-health-api.mjs — REST API server for workspace health monitoring.
 *
 * Extends workspace-health.mjs logic into a FastAPI server with
 * /health, /history, /projects, and webhook subscription endpoints.
 *
 * Usage:
 *   node scripts/workspace-health-api.mjs [--port 3000]
 */

import { readFileSync, existsSync, readdirSync, statSync } from 'fs';
import { join, resolve } from 'path';
import { fileURLToPath } from 'url';
import http from 'http';
import { parseArgs } from 'util';

const __dirname = resolve(dirname(fileURLToPath(import.meta.url)));
const WORKSPACE = join(__dirname, '..');
const MEMORY_PATH = 'C:/Users/adm/.claude/projects/D--OpenClaw-workspace/memory/MEMORY.md';
const PORT = parseArgs({ args: process.argv.slice(2), options: { port: { type: 'string', default: '3000' } } }).values.port || 3000;

// ─── Health Logic (from workspace-health.mjs) ─────────────────

function execGit(cmd, dir) {
  try {
    const { execSync } = require('child_process');
    return execSync(cmd, { cwd: dir, encoding: 'utf8', timeout: 5000 }).trim();
  } catch { return '?'; }
}

function scanProjects() {
  const memory = readFileSync(MEMORY_PATH, 'utf8');
  const lines = memory.split('\n');

  let headerIdx = lines.findIndex(l => l.startsWith('| Project |'));
  if (headerIdx === -1) return [];

  let sepIdx = headerIdx;
  while (sepIdx < lines.length && !lines[sepIdx].match(/\|[-]+\|/)) sepIdx++;

  const nextTableIdx = lines.slice(sepIdx + 1).findIndex(l => l.startsWith('| Archive |'));
  const rows = lines.slice(sepIdx + 1, nextTableIdx > 0 ? sepIdx + 1 + nextTableIdx : undefined)
    .filter(l => l.startsWith('| '));

  const projects = [];
  for (const row of rows) {
    const cols = row.split('|').map(c => c.trim());
    if (cols.length < 6) continue;
    const name = cols[1], path = cols[2], tech = cols[3], lastActive = cols[4];
    if (!name || !path) continue;
    const fullPath = join(WORKSPACE, path);

    let branch = '?', status = 'unknown', ahead = 0, behind = 0;
    try {
      branch = execGit('git branch --show-current', fullPath) || execGit('git rev-parse --short HEAD', fullPath);
      const tracking = execGit('git rev-list --left-right --count @{u}...HEAD', fullPath);
      if (tracking && tracking !== '?' && tracking.includes('\t')) {
        [behind, ahead] = tracking.split('\t').map(n => parseInt(n) || 0);
        status = (!ahead && !behind) ? 'synced' : `${ahead > 0 ? '+' + ahead : ''}${behind > 0 ? '-' + behind : ''}`;
      } else { status = 'synced'; }
    } catch { branch = 'n/a'; status = 'n/a'; }

    // Additional checks
    const pkgPath = join(fullPath, 'package.json');
    const hasPkg = existsSync(pkgPath);
    const nodeModules = join(fullPath, 'node_modules');
    const hasNodeModules = existsSync(nodeModules);
    const readmePath = join(fullPath, 'README.md');
    const hasReadme = existsSync(readmePath);
    const srcPath = join(fullPath, 'src');
    const hasSrc = existsSync(srcPath);

    // Score: higher = healthier
    let score = 70; // base
    if (hasPkg) score += 10;
    if (hasReadme) score += 5;
    if (hasSrc) score += 10;
    if (hasNodeModules) score += 5;
    if (status === 'synced') score += 5;
    else if (status !== 'n/a') score -= (ahead + behind) * 2;

    // Days since active
    const daysSince = lastActive ? Math.floor((Date.now() - new Date(lastActive).getTime()) / 86400000) : 999;
    if (daysSince > 30) score -= 20;
    else if (daysSince > 14) score -= 10;
    else if (daysSince <= 3) score += 5;

    projects.push({
      name, path, tech, lastActive, branch, status,
      health: Math.max(0, Math.min(100, score)),
      daysSinceActive: daysSince,
      flags: { hasPkg, hasReadme, hasSrc, hasNodeModules },
    });
  }
  return projects;
}

// ─── Webhook Subscriptions ──────────────────────────────────────

const subscribers = new Map(); // url → { lastSent, intervalSec }

function sendWebhook(url, payload) {
  return new Promise((resolve) => {
    try {
      const u = new URL(url);
      const req = http.request({ hostname: u.hostname, port: u.port || 80, path: u.pathname, method: 'POST', headers: { 'Content-Type': 'application/json' } }, (res) => {
        res.resume(); resolve(res.statusCode);
      });
      req.on('error', resolve);
      req.write(JSON.stringify(payload));
      req.end();
    } catch { resolve(0); }
  });
}

async function notifySubscribers() {
  const health = getHealthReport();
  for (const [url] of subscribers) {
    await sendWebhook(url, health);
    subscribers.get(url).lastSent = Date.now();
  }
}

// ─── Health Report ─────────────────────────────────────────────

let cachedHealth = null;
let cacheTime = 0;
const CACHE_TTL = 60000; // 1 min

function getHealthReport() {
  const now = Date.now();
  if (cachedHealth && now - cacheTime < CACHE_TTL) return cachedHealth;
  const projects = scanProjects();
  const avgHealth = projects.length ? Math.round(projects.reduce((s, p) => s + p.health, 0) / projects.length) : 0;
  const syncedCount = projects.filter(p => p.status === 'synced').length;
  const staleCount = projects.filter(p => p.daysSinceActive > 14).length;
  const grade = avgHealth >= 80 ? 'A' : avgHealth >= 60 ? 'B' : avgHealth >= 40 ? 'C' : 'D';
  cachedHealth = {
    timestamp: new Date().toISOString(),
    score: avgHealth,
    grade,
    projectCount: projects.length,
    syncedCount,
    staleCount,
    projects,
    summary: {
      overall: `${grade} (${avgHealth}/100)`,
      synced: `${syncedCount}/${projects.length} projects synced`,
      stale: `${staleCount} projects inactive >14 days`,
    },
  };
  cacheTime = now;
  return cachedHealth;
}

// ─── HTTP Router ──────────────────────────────────────────────

function sendJSON(res, status, data) {
  res.writeHead(status, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' });
  res.end(JSON.stringify(data, null, 2));
}

function sendText(res, status, text) {
  res.writeHead(status, { 'Content-Type': 'text/plain', 'Access-Control-Allow-Origin': '*' });
  res.end(text);
}

const history = []; // last 100 health snapshots

async function handleRequest(req, res) {
  const url = new URL(req.url, `http://localhost:${PORT}`);
  const path = url.pathname;

  if (path === '/health' && req.method === 'GET') {
    const report = getHealthReport();
    // Snapshot to history
    if (history.length >= 100) history.shift();
    history.push({ timestamp: report.timestamp, score: report.score, grade: report.grade, projectCount: report.projectCount });
    return sendJSON(res, 200, report);
  }

  if (path === '/history' && req.method === 'GET') {
    return sendJSON(res, 200, { snapshots: history });
  }

  if (path === '/projects' && req.method === 'GET') {
    const projects = scanProjects();
    return sendJSON(res, 200, { count: projects.length, projects });
  }

  if (path === '/webhook' && req.method === 'POST') {
    let body = '';
    req.on('data', c => body += c);
    req.on('end', () => {
      try {
        const { url: webhookUrl, intervalSec = 3600 } = JSON.parse(body);
        if (!webhookUrl) return sendJSON(res, 400, { error: 'url required' });
        subscribers.set(webhookUrl, { lastSent: 0, intervalSec: parseInt(intervalSec) || 3600 });
        sendJSON(res, 200, { ok: true, subscribers: subscribers.size });
      } catch { sendJSON(res, 400, { error: 'invalid JSON' }); }
    });
    return;
  }

  if (path === '/webhook' && req.method === 'DELETE') {
    let body = '';
    req.on('data', c => body += c);
    req.on('end', () => {
      try {
        const { url: webhookUrl } = JSON.parse(body);
        subscribers.delete(webhookUrl);
        sendJSON(res, 200, { ok: true, subscribers: subscribers.size });
      } catch { sendJSON(res, 400, { error: 'invalid JSON' }); }
    });
    return;
  }

  if (path === '/webhook' && req.method === 'GET') {
    return sendJSON(res, 200, {
      subscribers: [...subscribers.entries()].map(([url, s]) => ({ url, lastSent: new Date(s.lastSent).toISOString(), intervalSec: s.intervalSec }))
    });
  }

  if (path === '/dashboard' && req.method === 'GET') {
    const report = getHealthReport();
    return sendHTML(res, 200, generateDashboard(report, history));
  }

  if (path === '/') {
    return sendText(res, 200, [
      'Workspace Health API — v1.0',
      'GET  /health      — current health report',
      'GET  /history     — score history (last 100)',
      'GET  /projects    — per-project details',
      'POST /webhook     — subscribe (body: {url, intervalSec})',
      'DELETE /webhook   — unsubscribe (body: {url})',
      'GET  /webhook     — list subscribers',
      'GET  /dashboard   — HTML dashboard',
    ].join('\n'));
  }

  sendJSON(res, 404, { error: 'Not found' });
}

// ─── Dashboard HTML ──────────────────────────────────────────────

function gradeColor(g) {
  return g === 'A' ? '#3fb950' : g === 'B' ? '#58a6ff' : g === 'C' ? '#f0883e' : '#f85149';
}

function generateDashboard(report, history) {
  const historyJson = JSON.stringify(history.slice(-20));
  const projectsJson = JSON.stringify(report.projects.sort((a,b) => b.health - a.health));
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<title>Workspace Health — ${report.score}/100 (${report.grade})</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: system-ui, sans-serif; background: #0d1117; color: #e6edf3; padding: 1.5rem; }
  .header { display: flex; align-items: center; gap: 1.5rem; margin-bottom: 2rem; }
  .grade { font-size: 4rem; font-weight: 900; color: ${gradeColor(report.grade)}; line-height: 1; }
  .grade-label { font-size: 0.9rem; color: #8b949e; }
  .meta { font-size: 1.1rem; }
  .meta strong { color: ${gradeColor(report.grade)}; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem; }
  .card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 1rem; }
  .card-name { font-weight: 600; margin-bottom: 0.4rem; font-size: 0.9rem; }
  .card-meta { font-size: 0.75rem; color: #8b949e; }
  .health-bar { height: 4px; background: #21262d; border-radius: 2px; margin-top: 0.5rem; }
  .health-fill { height: 4px; border-radius: 2px; background: ${gradeColor(report.grade)}; transition: width 0.3s; }
  .stale { color: #f0883e; }
  .history-chart { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 1rem; margin-bottom: 1.5rem; }
  canvas { width: 100%; height: 80px; }
</style>
</head>
<body>
<div class="header">
  <div class="grade">${report.grade}</div>
  <div>
    <div class="meta"><strong>${report.score}</strong> / 100</div>
    <div class="grade-label">${report.summary.synced} · ${report.summary.stale}</div>
    <div class="grade-label">Updated: ${report.timestamp}</div>
  </div>
</div>
<div class="history-chart">
  <canvas id="chart"></canvas>
</div>
<div class="grid">
${report.projects.sort((a,b) => b.health - a.health).map(p => `
  <div class="card">
    <div class="card-name">${p.name}</div>
    <div class="card-meta">${p.tech || ''} · ${p.lastActive || 'unknown'}</div>
    <div class="card-meta">${p.branch} · ${p.status} · ${p.daysSinceActive}d ago</div>
    <div class="health-bar"><div class="health-fill" style="width:${p.health}%;background:${p.health >= 70 ? '#3fb950' : p.health >= 40 ? '#f0883e' : '#f85149'}"></div></div>
    <div class="card-meta" style="margin-top:0.3rem">Health: ${p.health}/100</div>
  </div>`).join('')}
</div>
<script>
const h = ${historyJson};
const c = document.getElementById('chart');
const ctx = c.getContext('2d');
c.width = c.parentElement.clientWidth;
const max = Math.max(...h.map(s => s.score), 1);
ctx.strokeStyle = '#58a6ff';
ctx.lineWidth = 2;
ctx.beginPath();
h.forEach((s, i) => {
  const x = (i / (h.length - 1 || 1)) * c.width;
  const y = c.height - (s.score / 100) * c.height;
  i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
});
ctx.stroke();
</script>
</body>
</html>`;
}

function sendHTML(res, status, html) {
  res.writeHead(status, { 'Content-Type': 'text/html', 'Access-Control-Allow-Origin': '*' });
  res.end(html);
}

// ─── Webhook Polling Loop ─────────────────────────────────────

setInterval(async () => {
  for (const [url, sub] of subscribers) {
    const elapsed = (Date.now() - sub.lastSent) / 1000;
    if (elapsed >= sub.intervalSec) {
      await notifySubscribers();
    }
  }
}, 60000);

// ─── Start Server ──────────────────────────────────────────────

const server = http.createServer(handleRequest);
server.listen(PORT, () => {
  console.log(`🏥 Workspace Health API running on http://localhost:${PORT}`);
  console.log(`   GET  /health      — health report + score`);
  console.log(`   GET  /history     — score history`);
  console.log(`   GET  /projects    — per-project details`);
  console.log(`   POST /webhook     — subscribe (body: {url, intervalSec})`);
  console.log(`   GET  /dashboard   — HTML dashboard`);
});
