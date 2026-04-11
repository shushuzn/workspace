#!/usr/bin/env node
/**
 * scripts/coverage-trend.mjs
 * Tracks coverage history and generates trend badge.
 *
 * Usage:
 *   node scripts/coverage-trend.mjs              # append current coverage-report.json
 *   node scripts/coverage-trend.mjs --badge      # generate SVG trend badge
 *   node scripts/coverage-trend.mjs --report     # show trend summary
 *
 * History file: coverage-history.jsonl (one JSON per line)
 */
import { readFileSync, existsSync, appendFileSync, writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const HISTORY_FILE = join(__dirname, '..', 'coverage-history.jsonl');
const COV_REPORT = join(__dirname, '..', 'coverage-report.json');

const MODE = process.argv.includes('--badge') ? 'badge'
  : process.argv.includes('--report') ? 'report'
  : 'append';

// ── Load history ───────────────────────────────────────────────────────────────
function loadHistory() {
  if (!existsSync(HISTORY_FILE)) return [];
  const content = readFileSync(HISTORY_FILE, 'utf8');
  return content.trim().split('\n').filter(Boolean).map(l => {
    try { return JSON.parse(l); } catch { return null; }
  }).filter(Boolean);
}

function saveEntry(entry) {
  appendFileSync(HISTORY_FILE, JSON.stringify(entry) + '\n');
}

// ── Calculate trend ────────────────────────────────────────────────────────────
function calcTrend(suite, history) {
  const entries = history.filter(h => h.suites && h.suites.find(s => s.suite === suite));
  if (entries.length < 2) return { direction: '→', delta: 0 };

  // Get last two entries for this suite
  const last = entries[entries.length - 1];
  const prev = entries[entries.length - 2];

  const lastSuite = last.suites?.find(s => s.suite === suite);
  const prevSuite = prev.suites?.find(s => s.suite === suite);

  if (!lastSuite || !prevSuite) return { direction: '→', delta: 0 };

  const delta = lastSuite.coverage - prevSuite.coverage;
  if (delta > 0) return { direction: '↑', delta };
  if (delta < 0) return { direction: '↓', delta };
  return { direction: '→', delta: 0 };
}

// ── Generate SVG badge ─────────────────────────────────────────────────────────
function generateBadge(totalCov, trend) {
  const color = trend.direction === '↑' ? '#2ea44f' : trend.direction === '↓' ? '#cb2431' : '#6a737d';
  const text = `${totalCov}% ${trend.direction}`;

  return `<svg xmlns="http://www.w3.org/2000/svg" width="100" height="20" viewBox="0 0 100 20">
  <rect width="100" height="20" fill="${color}" rx="3"/>
  <text x="50" y="14" font-family="sans-serif" font-size="11" font-weight="bold" fill="#fff" text-anchor="middle">${text}</text>
</svg>`;
}

// ── Main modes ─────────────────────────────────────────────────────────────────
async function mainAppend() {
  if (!existsSync(COV_REPORT)) {
    console.error('coverage-report.json not found. Run tests first.');
    process.exit(1);
  }

  const cov = JSON.parse(readFileSync(COV_REPORT, 'utf8'));
  const entry = {
    timestamp: new Date().toISOString(),
    total: parseFloat(cov.total),
    suites: cov.suites.map(s => ({
      suite: s.suite,
      coverage: s.coverage,
      threshold: s.threshold,
      pass: s.coverage >= s.threshold
    })),
    pass: cov.pass
  };

  saveEntry(entry);
  console.log(`Appended to ${HISTORY_FILE}`);
  console.log(`Total: ${entry.total}% | Suites: ${entry.suites.length} | Pass: ${entry.pass}`);

  // Auto-generate badge
  const history = loadHistory();
  const trend = calcTrend('step-parser', history); // Use step-parser as proxy for overall
  const badge = generateBadge(entry.total, trend);
  writeFileSync(join(__dirname, '..', 'coverage-trend.svg'), badge);
  console.log('Generated coverage-trend.svg');
}

async function mainBadge() {
  const history = loadHistory();
  if (history.length === 0) {
    console.log('No history yet. Run with no args first.');
    return;
  }

  const latest = history[history.length - 1];
  const trend = calcTrend('step-parser', history);
  const badge = generateBadge(latest.total, trend);
  writeFileSync(join(__dirname, '..', 'coverage-trend.svg'), badge);
  console.log('Generated coverage-trend.svg');
  console.log(`Coverage: ${latest.total}% ${trend.direction} (delta: ${trend.delta >= 0 ? '+' : ''}${trend.delta}%)`);
}

async function mainReport() {
  const history = loadHistory();
  if (history.length === 0) {
    console.log('No history yet.');
    return;
  }

  console.log(`\n=== Coverage Trend Report ===`);
  console.log(`History entries: ${history.length}\n`);

  const suites = ['step-parser', 'run-seed', 'add-seed'];
  for (const suite of suites) {
    const entries = history.filter(h => h.suites?.find(s => s.suite === suite));
    if (entries.length === 0) continue;

    const trend = calcTrend(suite, history);
    const latest = entries[entries.length - 1];
    const latestSuite = latest.suites?.find(s => s.suite === suite);

    console.log(`${suite}:`);
    console.log(`  Latest: ${latestSuite?.coverage}% | Threshold: ${latestSuite?.threshold}%`);
    console.log(`  Trend: ${trend.direction} (${trend.delta >= 0 ? '+' : ''}${trend.delta}%)`);
    console.log(`  History: ${entries.map(e => e.suites?.find(s => s.suite === suite)?.coverage + '%').join(' → ')}`);
    console.log();
  }
}

const main = MODE === 'badge' ? mainBadge
  : MODE === 'report' ? mainReport
  : mainAppend;

main().catch(e => { console.error(e); process.exit(1); });
