#!/usr/bin/env node
/**
 * scripts/ci-health.mjs
 * Computes CI health score from multiple metrics.
 *
 * Usage:
 *   node scripts/ci-health.mjs              # compute and output JSON
 *   node scripts/ci-health.mjs --badge       # generate SVG badge
 *   node scripts/ci-health.mjs --summary     # human-readable summary
 *
 * Health score formula:
 *   health = 0.35×pass_rate + 0.30×avg_coverage + 0.20×(1/mttr_normalized) + 0.15×pattern_confidence
 *
 * Output: ci-health.json (for badge generation)
 */
import { readFileSync, existsSync, writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const HISTORY_FILE    = join(__dirname, '..', 'coverage-history.jsonl');
const CHRONICLE_FILE  = join(__dirname, '..', 'ci-debug-chronicle.jsonl');
const PATTERN_FILE    = join(__dirname, '..', 'scripts', 'ci-failure-patterns.jsonl');
const OUTPUT_FILE     = join(__dirname, '..', 'ci-health.json');
const BADGE_FILE      = join(__dirname, '..', 'ci-health-badge.svg');

const MODE = process.argv.includes('--badge') ? 'badge'
  : process.argv.includes('--summary') ? 'summary'
  : 'json';

function loadHistory() {
  if (!existsSync(HISTORY_FILE)) return [];
  const content = readFileSync(HISTORY_FILE, 'utf8');
  return content.trim().split('\n').filter(Boolean).map(l => {
    try { return JSON.parse(l); } catch { return null; }
  }).filter(Boolean);
}

function loadChronicle() {
  if (!existsSync(CHRONICLE_FILE)) return [];
  const content = readFileSync(CHRONICLE_FILE, 'utf8');
  return content.trim().split('\n').filter(Boolean).map(l => {
    try { return JSON.parse(l); } catch { return null; }
  }).filter(Boolean);
}

function loadPatterns() {
  if (!existsSync(PATTERN_FILE)) return [];
  const content = readFileSync(PATTERN_FILE, 'utf8');
  return content.trim().split('\n').filter(Boolean).map(l => {
    try { return JSON.parse(l); } catch { return null; }
  }).filter(Boolean);
}

function calcPassRate(history, days = 30) {
  if (history.length === 0) return null;
  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - days);
  const recent = history.filter(h => new Date(h.timestamp) >= cutoff);
  if (!recent.length) return null;
  const passed = recent.filter(h => h.pass !== false).length;
  return passed / recent.length;
}

function calcAvgCoverage(history, days = 30) {
  if (history.length === 0) return null;
  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - days);
  const recent = history.filter(h => new Date(h.timestamp) >= cutoff);
  if (!recent.length) return null;
  const total = recent.reduce((sum, h) => sum + (parseFloat(h.total) || 0), 0);
  return total / recent.length;
}

function calcMTTR(chronicle) {
  const withResolution = chronicle.filter(e => e.resolved && e.resolved_at);
  if (withResolution.length === 0) return null;
  const totalMinutes = withResolution.reduce((sum, e) => {
    const start = new Date(e.timestamp);
    const end = new Date(e.resolved_at);
    return sum + (end - start) / 60000;
  }, 0);
  return totalMinutes / withResolution.length;
}

function calcPatternConfidence(patterns) {
  if (!patterns || patterns.length === 0) return 0;
  let totalConf = 0;
  let count = 0;
  for (const p of patterns) {
    const occ = p.occurrences || 0;
    const conf = p.confirmations || 0;
    if (occ > 0) {
      totalConf += Math.min(1, conf / occ);
      count++;
    }
  }
  return count > 0 ? totalConf / count : 0;
}

function scoreColor(score) {
  if (score >= 80) return '#2ea44f';
  if (score >= 60) return '#f0ad4e';
  return '#cb2431';
}

function generateBadge(score) {
  const color = scoreColor(score);
  const label = 'CI Health';
  return `<svg xmlns="http://www.w3.org/2000/svg" width="110" height="20" viewBox="0 0 110 20">
  <rect width="110" height="20" fill="#6a737d" rx="3"/>
  <rect x="55" width="55" height="20" fill="${color}" rx="0 3 3 0"/>
  <text x="27" y="14" font-family="sans-serif" font-size="11" font-weight="bold" fill="#fff" text-anchor="middle">${label}</text>
  <text x="82" y="14" font-family="sans-serif" font-size="11" font-weight="bold" fill="#fff" text-anchor="middle">${score}</text>
</svg>`;
}

async function main() {
  const history   = loadHistory();
  const chronicle = loadChronicle();
  const patterns = loadPatterns();

  const passRate    = calcPassRate(history) ?? null;
  const avgCoverage = calcAvgCoverage(history) ?? null;
  const mttr        = calcMTTR(chronicle);
  const mttrScore   = mttr ? Math.max(0, 1 - mttr / 120) : 1.0; // 120min = 0, 0min = 1
  const patternConf = calcPatternConfidence(patterns);

  // Use 0 for missing metrics in score calculation
  const pr = passRate ?? 0;
  const ac = avgCoverage ?? 0;

  const healthScore = Math.round(
    0.35 * pr +
    0.30 * ac +
    0.20 * mttrScore +
    0.15 * patternConf
  );

  const output = {
    score: healthScore,
    pass_rate_30d: passRate ? (passRate * 100).toFixed(1) : 'N/A',
    avg_coverage_30d: avgCoverage ? (avgCoverage * 100).toFixed(1) : 'N/A',
    mttr_minutes: mttr ? Math.round(mttr) : 'N/A',
    pattern_confidence: (patternConf * 100).toFixed(0),
    components: { passRate, avgCoverage, mttrScore, patternConf },
    date: new Date().toISOString().split('T')[0]
  };

  if (MODE === 'badge') {
    const badge = generateBadge(healthScore);
    writeFileSync(BADGE_FILE, badge);
    console.log(`Generated ${BADGE_FILE} — Score: ${healthScore}`);
    return;
  }

  if (MODE === 'summary') {
    console.log(`\n=== CI Health: ${healthScore}/100 ===`);
    console.log(`Pass Rate (30d):  ${output.pass_rate_30d}%`);
    console.log(`Avg Coverage:    ${output.avg_coverage_30d}%`);
    console.log(`MTTR:           ${output.mttr_minutes} minutes`);
    console.log(`Pattern Conf:    ${output.pattern_confidence}%`);
    console.log(`  └─ Pass Rate:  ${(passRate * 100).toFixed(1)}% × 0.35 = ${(passRate * 0.35 * 100).toFixed(1)}`);
    console.log(`  └─ Coverage:   ${(avgCoverage * 100).toFixed(1)}% × 0.30 = ${(avgCoverage * 0.30 * 100).toFixed(1)}`);
    console.log(`  └─ MTTR:      ${mttr ? Math.round(mttr) + 'min' : 'N/A'} × 0.20 = ${(mttrScore * 0.20 * 100).toFixed(1)}`);
    console.log(`  └─ Pattern:    ${(patternConf * 100).toFixed(0)}% × 0.15 = ${(patternConf * 0.15 * 100).toFixed(1)}`);
    console.log();
    return;
  }

  writeFileSync(OUTPUT_FILE, JSON.stringify(output, null, 2));
  console.log(JSON.stringify(output, null, 2));
}

main().catch(e => { console.error(e); process.exit(1); });
