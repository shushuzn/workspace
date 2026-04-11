#!/usr/bin/env node
/**
 * scripts/ci-health-history.mjs
 * Records CI health scores to history and shows trend.
 *
 * Usage:
 *   node scripts/ci-health-history.mjs append  # append current ci-health.json
 *   node scripts/ci-health-history.mjs trend   # show score trend
 *   node scripts/ci-health-history.mjs alert   # exit 1 if score dropped > threshold
 */
import { readFileSync, existsSync, appendFileSync, writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const HEALTH_FILE     = join(__dirname, '..', 'ci-health.json');
const HISTORY_FILE    = join(__dirname, '..', 'ci-health-history.jsonl');
const ALERT_THRESHOLD = 60; // Alert if score drops below this

const MODE = process.argv[2];

function loadHistory() {
  if (!existsSync(HISTORY_FILE)) return [];
  const content = readFileSync(HISTORY_FILE, 'utf8');
  return content.trim().split('\n').filter(Boolean).map(l => {
    try { return JSON.parse(l); } catch { return null; }
  }).filter(Boolean);
}

function trend(history) {
  if (history.length < 2) {
    console.log('Not enough history for trend analysis.');
    return;
  }

  const recent = history.slice(-10);
  const first = recent[0];
  const last = recent[recent.length - 1];
  const delta = last.score - first.score;

  console.log('\n=== CI Health Trend ===\n');
  console.log(`Period: ${first.date} → ${last.date}`);
  console.log(`Entries: ${recent.length}`);
  console.log(`Score: ${first.score} → ${last.score} (${delta >= 0 ? '+' : ''}${delta})`);
  console.log();

  // Sparkline
  const min = Math.min(...recent.map(h => h.score));
  const max = Math.max(...recent.map(h => h.score));
  const range = max - min || 1;

  const sparkline = recent.map(h => {
    const pos = Math.round((h.score - min) / range * 3);
    return ['▁', '▂', '▃', '▄'][Math.min(3, pos)];
  }).join('');

  console.log(`Sparkline: ${sparkline}`);
  console.log();

  // Check for drops
  for (let i = 1; i < recent.length; i++) {
    const drop = recent[i - 1].score - recent[i].score;
    if (drop >= 10) {
      console.log(`⚠️  ${recent[i].date}: dropped ${drop} points (${recent[i-1].score} → ${recent[i].score})`);
    }
  }
  console.log();
}

function alert(history) {
  const last = history[history.length - 1];
  if (!last) return false;

  if (last.score < ALERT_THRESHOLD) {
    console.log(`🚨 ALERT: CI health score ${last.score} below threshold ${ALERT_THRESHOLD}`);
    return true;
  }

  if (history.length >= 2) {
    const prev = history[history.length - 2];
    const drop = prev.score - last.score;
    if (drop >= 15) {
      console.log(`🚨 ALERT: CI health dropped ${drop} points in last update (${prev.score} → ${last.score})`);
      return true;
    }
  }

  console.log(`✅ CI health score OK: ${last.score}`);
  return false;
}

async function main() {
  if (MODE === 'append') {
    if (!existsSync(HEALTH_FILE)) {
      console.error('ci-health.json not found. Run: node scripts/ci-health.mjs first.');
      process.exit(1);
    }
    const health = JSON.parse(readFileSync(HEALTH_FILE, 'utf8'));
    appendFileSync(HISTORY_FILE, JSON.stringify(health) + '\n');
    console.log(`Appended: score=${health.score} date=${health.date}`);
    return;
  }

  const history = loadHistory();

  if (MODE === 'trend') {
    trend(history);
    return;
  }

  if (MODE === 'alert') {
    const triggered = alert(history);
    process.exit(triggered ? 1 : 0);
    return;
  }

  // Default: show recent
  console.log('\n=== CI Health History ===\n');
  const recent = history.slice(-10).reverse();
  if (recent.length === 0) {
    console.log('No history. Run: node scripts/ci-health-history.mjs append');
    return;
  }
  for (const h of recent) {
    const icon = h.score >= 80 ? '🟢' : h.score >= 60 ? '🟡' : '🔴';
    console.log(`${icon} ${h.date} | Score: ${h.score} | Pass: ${h.pass_rate_30d}% | MTTR: ${h.mttr_minutes}m`);
  }
  console.log();
}

main().catch(e => { console.error(e); process.exit(1); });
