#!/usr/bin/env node
/**
 * exec-history-viz.mjs
 * Visualize adapter execution history as ASCII trend chart
 * Usage: node shared/exec-history-viz.mjs [days] [taskType]
 */
import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const HISTORY_FILE = join(__DIR, '..', '80-PROJECTS', 'task-orchestrator', 'exec-history.jsonl');

function parseHistory() {
  if (!existsSync(HISTORY_FILE)) return {};
  const lines = readFileSync(HISTORY_FILE, 'utf8').split('\n').filter(Boolean);
  const entries = [];
  for (const l of lines) {
    try { entries.push(JSON.parse(l)); } catch {}
  }
  return entries;
}

function buildTrend(entries, days = 7, taskType = null) {
  const now = Date.now();
  const cutoff = now - days * 24 * 60 * 60 * 1000;
  const arr = Array.isArray(entries) ? entries : Object.values(entries).flat();
  const filtered = arr.filter(e => e.timestamp > cutoff && (!taskType || e.taskType === taskType));

  // Group by date
  const byDate = {};
  for (const e of filtered) {
    const d = new Date(e.timestamp).toISOString().slice(0, 10);
    if (!byDate[d]) byDate[d] = { success: 0, total: 0 };
    byDate[d].total++;
    if (e.success) byDate[d].success++;
  }

  // Sort dates
  const dates = Object.keys(byDate).sort();
  if (dates.length === 0) {
    console.log('No data for the specified period.');
    return;
  }

  // Print header
  console.log('╔══════════════════════════════════════════════════════════════╗');
  console.log('║  Adapter Execution Trend                            ║');
  console.log('╚══════════════════════════════════════════════════════════════╝\n');
  if (taskType) console.log(`  Task type: ${taskType}  |  Period: ${days} days\n`);
  else console.log(`  All task types  |  Period: ${days} days\n`);

  // ASCII bar chart
  console.log('  Success Rate by Date');
  console.log('  ─────────────────────────────────────────────────────────');
  for (const d of dates) {
    const rate = byDate[d].success / byDate[d].total;
    const barLen = Math.round(rate * 40);
    const bar = '█'.repeat(barLen) + '░'.repeat(40 - barLen);
    const pct = (rate * 100).toFixed(0);
    console.log(`  ${d}  ${bar}  ${pct}%  (${byDate[d].success}/${byDate[d].total})`);
  }

  // Per-adapter summary
  console.log('\n  ─────────────────────────────────────────────────────────');
  console.log('  Per-Adapter Summary (last', days, 'days)');
  console.log('  ─────────────────────────────────────────────────────────');
  const byAdapter = {};
  for (const e of filtered) {
    if (!byAdapter[e.adapterId]) byAdapter[e.adapterId] = { success: 0, total: 0, totalDuration: 0 };
    byAdapter[e.adapterId].total++;
    if (e.success) byAdapter[e.adapterId].success++;
    byAdapter[e.adapterId].totalDuration += e.durationMs || 0;
  }
  const sorted = Object.entries(byAdapter).sort((a, b) => b[1].total - a[1].total);
  for (const [adapterId, s] of sorted) {
    const rate = s.success / s.total;
    const avgDur = Math.round(s.totalDuration / s.total);
    const stars = rate >= 0.9 ? '🟢' : rate >= 0.7 ? '🟡' : '🔴';
    console.log(`  ${stars} ${adapterId.padEnd(20)} ${(rate * 100).toFixed(0).padStart(3)}%  avg:${avgDur}ms  runs:${s.total}`);
  }
  console.log('');
}

const days = parseInt(process.argv[2]) || 7;
const taskType = process.argv[3] || null;
const entries = parseHistory();
buildTrend(entries, days, taskType);
