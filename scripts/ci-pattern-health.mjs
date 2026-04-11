#!/usr/bin/env node
/**
 * scripts/ci-pattern-health.mjs
 * Pattern health dashboard — tracks confidence trends and alerts on degradation.
 *
 * Usage:
 *   node scripts/ci-pattern-health.mjs              # show dashboard
 *   node scripts/ci-pattern-health.mjs alert        # show degraded patterns
 *   node scripts/ci-pattern-health.mjs trend <name> # show trend for one pattern
 */
import { existsSync, readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PATTERN_FILE = join(__dirname, 'ci-failure-patterns.jsonl');
const STATE_FILE = join(__dirname, '..', 'ci-state.json');

function loadPatterns() {
  if (!existsSync(PATTERN_FILE)) return [];
  try {
    const content = readFileSync(PATTERN_FILE, 'utf8');
    return content.trim().split('\n').filter(Boolean).map(l => {
      try { return JSON.parse(l); } catch { return null; }
    }).filter(Boolean);
  } catch { return []; }
}

function loadState() {
  if (!existsSync(STATE_FILE)) return {};
  try { return JSON.parse(readFileSync(STATE_FILE, 'utf8')); } catch { return {}; }
}

function getConfidence(p) {
  if (p.confirmations == null || p.rejections == null) return null;
  if (p.confirmations + p.rejections === 0) return null;
  return p.confirmations / (p.confirmations + p.rejections);
}

function getTrend(p) {
  // Use fixHistory from state to compute trend
  const state = loadState();
  const history = state.patterns?.fixHistory?.[p.name] || [];
  if (history.length < 2) return 'stable';
  // Recent confirm/reject ratio vs older ones
  const recent = history.slice(-Math.ceil(history.length / 2));
  const older = history.slice(0, Math.floor(history.length / 2));
  const recentRate = recent.filter(h => h.result === 'resolved').length / recent.length;
  const olderRate = older.filter(h => h.result === 'resolved').length / older.length;
  if (recentRate < olderRate - 0.2) return 'degrading';
  if (recentRate > olderRate + 0.2) return 'improving';
  return 'stable';
}

function sparkline(history, width = 12) {
  if (!history || history.length === 0) return '—'.repeat(width);
  const step = Math.max(1, Math.floor(history.length / width));
  let chars = '';
  for (let i = 0; i < width; i++) {
    const idx = Math.min(i * step, history.length - 1);
    const h = history[idx];
    if (h.result === 'resolved') chars += '✅';
    else if (h.result === 'failed') chars += '❌';
    else chars += '⬜';
  }
  return chars;
}

async function main() {
  const [, , cmd, ...args] = process.argv;
  const patterns = loadPatterns();

  if (cmd === 'alert') {
    console.log('\n=== Pattern Health Alerts ===\n');
    let hasAlert = false;
    for (const p of patterns) {
      const conf = getConfidence(p);
      const trend = getTrend(p);
      if (conf !== null && conf < 0.6) {
        console.log(`  🔴 ${p.name}: confidence ${(conf * 100).toFixed(0)}% (${trend})`);
        hasAlert = true;
      } else if (trend === 'degrading') {
        console.log(`  🟡 ${p.name}: trend degrading`);
        hasAlert = true;
      } else if (conf !== null && conf < 0.8) {
        console.log(`  🟡 ${p.name}: confidence ${(conf * 100).toFixed(0)}% (below 80% — auto-fix locked)`);
        hasAlert = true;
      }
    }
    if (!hasAlert) console.log('  ✅ All patterns healthy');
    console.log();
    return;
  }

  if (cmd === 'trend') {
    const name = args.join(' ');
    const p = patterns.find(p => p.name === name);
    if (!p) { console.error(`Pattern not found: ${name}`); process.exit(1); }
    const state = loadState();
    const history = state.patterns?.fixHistory?.[name] || [];
    const conf = getConfidence(p);
    console.log(`\n=== ${name} ===\n`);
    console.log(`  Severity: ${p.severity}`);
    console.log(`  Occurrences: ${p.occurrences || 0}`);
    console.log(`  Last seen: ${p.lastSeen || 'never'}`);
    console.log(`  Confirmations: ${p.confirmations || 0}`);
    console.log(`  Rejections: ${p.rejections || 0}`);
    console.log(`  Confidence: ${conf !== null ? `${(conf * 100).toFixed(1)}%` : 'N/A'}`);
    console.log(`  Trend: ${getTrend(p)}`);
    if (history.length > 0) {
      console.log(`\n  Fix history (${history.length} attempts):`);
      for (const h of history) {
        console.log(`    ${new Date(h.timestamp).toLocaleDateString()} — ${h.result}`);
      }
    } else {
      console.log('\n  No fix attempts recorded.');
    }
    console.log();
    return;
  }

  // Default: dashboard
  const state = loadState();
  console.log('\n=== Pattern Health Dashboard ===\n');
  console.log('  Pattern                    | Confidence | Trend    | History');
  console.log('  --------------------------|------------|----------|' + '—'.repeat(12));
  for (const p of patterns) {
    const conf = getConfidence(p);
    const trend = getTrend(p);
    const history = state.patterns?.fixHistory?.[p.name] || [];
    const trendIcon = trend === 'degrading' ? '📉' : trend === 'improving' ? '📈' : '➡️ ';
    const confStr = conf !== null ? `${(conf * 100).toFixed(0)}%`.padStart(6) : '   N/A';
    const nameStr = p.name.substring(0, 24).padEnd(24);
    const trendStr = trendIcon;
    const histStr = history.length > 0 ? sparkline(history) : '(no data)';
    const alert = conf !== null && conf < 0.6 ? '🔴' : conf !== null && conf < 0.8 ? '🟡' : '  ';
    console.log(`  ${alert} ${nameStr} | ${confStr} | ${trendStr}    | ${histStr}`);
  }
  console.log();

  // Summary
  const healthy = patterns.filter(p => {
    const c = getConfidence(p);
    return c === null || c >= 0.8;
  }).length;
  const degraded = patterns.filter(p => {
    const c = getConfidence(p);
    return c !== null && c < 0.8;
  }).length;
  console.log(`  Summary: ${healthy} healthy, ${degraded} need attention\n`);
  console.log('  Run: node scripts/ci-pattern-health.mjs alert  # degraded patterns');
  console.log('  Run: node scripts/ci-pattern-health.mjs trend <name>  # details\n');
}

main().catch(e => { console.error(e); process.exit(1); });
