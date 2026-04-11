#!/usr/bin/env node
/**
 * scripts/coverage-autobaseline.mjs
 * Auto-updates coverage thresholds based on historical averages.
 *
 * Usage:
 *   node scripts/coverage-autobaseline.mjs          # show current vs recommended
 *   node scripts/coverage-autobaseline.mjs --update # write recommended thresholds to test-coverage-ci.mjs
 *
 * Algorithm: mean(last 10 runs) * 0.95 (5% safety margin)
 * If coverage-report.json exists, uses it as the new data point.
 */
import { readFileSync, existsSync, writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const HISTORY_FILE = join(__dirname, '..', 'coverage-history.jsonl');
const COV_REPORT  = join(__dirname, '..', 'coverage-report.json');
const TEST_COV    = join(__dirname, '..', 'shared', 'test-coverage-ci.mjs');

const MODE = process.argv.includes('--update') ? 'update' : 'report';
const MIN_RUNS = 3;
const SAFETY_MARGIN = 0.95; // 5% below average
const HISTORY_WINDOW = 10;

// ── Load history ───────────────────────────────────────────────────────────────
function loadHistory() {
  if (!existsSync(HISTORY_FILE)) return [];
  const content = readFileSync(HISTORY_FILE, 'utf8');
  return content.trim().split('\n').filter(Boolean).map(l => {
    try { return JSON.parse(l); } catch { return null; }
  }).filter(Boolean);
}

// ── Calculate per-suite stats ───────────────────────────────────────────────────
function calcSuiteStats(history) {
  const suites = ['step-parser', 'run-seed', 'add-seed'];
  const stats = {};

  for (const suite of suites) {
    const entries = history
      .filter(h => h.suites?.find(s => s.suite === suite))
      .slice(-HISTORY_WINDOW);

    if (entries.length < MIN_RUNS) {
      stats[suite] = { n: entries.length, recommended: null, avg: null, std: null };
      continue;
    }

    const coverages = entries.map(e => e.suites?.find(s => s.suite === suite)?.coverage || 0);
    const avg = coverages.reduce((a, b) => a + b, 0) / coverages.length;
    const variance = coverages.reduce((sum, c) => sum + Math.pow(c - avg, 2), 0) / coverages.length;
    const std = Math.sqrt(variance);
    const recommended = Math.floor(avg * SAFETY_MARGIN);

    stats[suite] = { n: entries.length, avg: avg.toFixed(1), std: std.toFixed(1), recommended };
  }

  return stats;
}

// ── Read current thresholds ────────────────────────────────────────────────────
function readCurrentThresholds() {
  if (!existsSync(TEST_COV)) return {};
  const content = readFileSync(TEST_COV, 'utf8');
  const match = content.match(/THRESHOLDS\s*=\s*\{([^}]+)\}/s);
  if (!match) return {};
  const result = {};
  for (const line of match[1].split('\n')) {
    const m = line.match(/['"](\w+)['"]\s*:\s*(\d+)/);
    if (m) result[m[1]] = parseInt(m[2], 10);
  }
  return result;
}

// ── Update test-coverage-ci.mjs ───────────────────────────────────────────────
function updateThresholds(stats) {
  const content = readFileSync(TEST_COV, 'utf8');
  const newLines = [];
  for (const [suite, data] of Object.entries(stats)) {
    if (data.recommended === null) continue;
    newLines.push(`  '${suite}': ${data.recommended},`);
  }
  if (newLines.length === 0) {
    console.log('No sufficient data to update thresholds.');
    return;
  }

  const newBlock = `const THRESHOLDS = {\n${newLines.join('\n')}\n};`;
  const updated = content.replace(/const THRESHOLDS\s*=\s*\{[^}]+\}/s, newBlock);
  writeFileSync(TEST_COV, updated, 'utf8');
}

// ── Main ──────────────────────────────────────────────────────────────────────
async function main() {
  // If --update, first append current coverage-report.json to history
  if (MODE === 'update') {
    if (existsSync(COV_REPORT)) {
      const { spawn } = await import('child_process');
      const p = spawn('node', [join(__dirname, '..', 'scripts', 'coverage-trend.mjs')], {
        stdio: ['ignore', 'pipe', 'pipe'],
        shell: true
      });
      let out = '';
      p.stdout.on('data', d => out += d.toString());
      p.on('close', () => {
        console.log(out.trim());
        performUpdate();
      });
    } else {
      performUpdate();
    }
    return;
  }

  performUpdate();

  function performUpdate() {
    const history = loadHistory();
    const stats = calcSuiteStats(history);
    const current = readCurrentThresholds();

    console.log('\n=== Coverage Auto-Baseline ===\n');
    console.log(`History: ${history.length} entries (window: ${HISTORY_WINDOW}, min: ${MIN_RUNS})\n`);

    let allGood = true;
    for (const [suite, data] of Object.entries(stats)) {
      const cur = current[suite] || '?';
      const icon = data.recommended === null ? '⏳'
        : (data.recommended <= cur) ? '✅' : '⚠️ ';
      console.log(`${suite}:`);
      console.log(`  Current threshold: ${cur}%`);
      if (data.recommended !== null) {
        console.log(`  Recommended: ${data.recommended}% (avg: ${data.avg}%, σ: ${data.std}%)`);
        console.log(`  ${icon} ${data.recommended <= cur ? 'OK (safe)' : 'LOW (increase needed)'}`);
        if (data.recommended > cur) allGood = false;
      } else {
        console.log(`  ${icon} Not enough data (${data.n}/${MIN_RUNS} runs)`);
      }
      console.log();
    }

    if (MODE === 'update' && allGood) {
      console.log('All thresholds are safe — no update needed.');
    }
  }
}

main().catch(e => { console.error(e); process.exit(1); });
