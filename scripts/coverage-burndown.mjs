#!/usr/bin/env node
/**
 * scripts/coverage-burndown.mjs
 * Predicts when each suite will breach its coverage threshold.
 *
 * Usage:
 *   node scripts/coverage-burndown.mjs              # show all predictions
 *   node scripts/coverage-burndown.mjs --alert      # show only suites with < 4 weeks warning
 *
 * Uses linear regression on last 10 coverage-history.jsonl entries
 * to estimate weeks until threshold breach.
 */
import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const HISTORY_FILE = join(__dirname, '..', 'coverage-history.jsonl');

const MODE = process.argv.includes('--alert') ? 'alert' : 'full';
const HISTORY_WINDOW = 10;
const WARN_WEEKS = 4; // Alert if breach expected within this many weeks

function loadHistory() {
  if (!existsSync(HISTORY_FILE)) return [];
  const content = readFileSync(HISTORY_FILE, 'utf8');
  return content.trim().split('\n').filter(Boolean).map(l => {
    try { return JSON.parse(l); } catch { return null; }
  }).filter(Boolean);
}

function linearRegression(values) {
  const n = values.length;
  if (n < 2) return null;

  let sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0;
  for (let i = 0; i < n; i++) {
    sumX += i;
    sumY += values[i];
    sumXY += i * values[i];
    sumX2 += i * i;
  }

  const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
  const intercept = (sumY - slope * sumX) / n;

  // R-squared
  const yMean = sumY / n;
  let ssRes = 0, ssTot = 0;
  for (let i = 0; i < n; i++) {
    const yPred = intercept + slope * i;
    ssRes += Math.pow(values[i] - yPred, 2);
    ssTot += Math.pow(values[i] - yMean, 2);
  }
  const r2 = ssTot === 0 ? 0 : 1 - ssRes / ssTot;

  return { slope, intercept, r2 };
}

function predictBreach(suiteName, history) {
  const entries = history
    .filter(h => h.suites?.find(s => s.suite === suiteName))
    .slice(-HISTORY_WINDOW);

  if (entries.length < 2) return { status: 'insufficient_data' };

  const coverages = entries.map(e => e.suites.find(s => s.suite === suiteName).coverage);
  const latest = entries[entries.length - 1];
  const latestSuite = latest.suites.find(s => s.suite === suiteName);
  const threshold = latestSuite.threshold;

  const reg = linearRegression(coverages);
  if (!reg || reg.slope >= 0) {
    return {
      status: reg?.slope >= 0 ? 'stable_or_improving' : 'insufficient_data',
      current: latestSuite.coverage,
      threshold,
      trend: '→ stable or improving'
    };
  }

  const { slope, intercept, r2 } = reg;
  const currentCoverage = latestSuite.coverage;
  const weeksToThreshold = (threshold - currentCoverage) / Math.abs(slope);

  const direction = slope > 0 ? '↑' : slope < 0 ? '↓' : '→';
  const riskLevel = weeksToThreshold <= 2 ? 'P1' : weeksToThreshold <= 4 ? 'P2' : weeksToThreshold <= 8 ? 'P3' : 'P4';

  return {
    status: 'predicted_breach',
    current: currentCoverage,
    threshold,
    slope: slope.toFixed(2),
    weeksToBreach: weeksToThreshold.toFixed(1),
    r2: r2.toFixed(2),
    riskLevel,
    direction,
    trend: `${direction} ${Math.abs(slope).toFixed(1)}%/week`
  };
}

async function main() {
  const history = loadHistory();
  console.log('\n=== Coverage Burndown Predictions ===\n');
  console.log(`History: ${history.length} entries (window: ${HISTORY_WINDOW})\n`);

  const suites = ['step-parser', 'run-seed', 'add-seed'];
  const results = [];

  for (const suite of suites) {
    const result = predictBreach(suite, history);
    results.push({ suite, ...result });
  }

  const breachPredictions = results.filter(r => r.status === 'predicted_breach');
  const stable = results.filter(r => r.status !== 'predicted_breach');

  console.log('=== Predicted Breaches ===');
  if (breachPredictions.length === 0) {
    console.log('No predicted breaches in the next 8+ weeks.\n');
  } else {
    for (const r of breachPredictions) {
      const icon = r.riskLevel === 'P1' ? '🚨' : r.riskLevel === 'P2' ? '⚠️ ' : '📉';
      console.log(`${r.suite}:`);
      console.log(`  ${icon} [${r.riskLevel}] Current: ${r.current}% | Threshold: ${r.threshold}%`);
      console.log(`  Trend: ${r.trend} (R²=${r.r2})`);
      console.log(`  Predicted breach in: ${r.weeksToBreach} weeks`);
      console.log(`  Weeks from now: ~${Math.round(parseFloat(r.weeksToBreach) * 7)} days`);
      console.log();
    }
  }

  console.log('=== Stable / Improving ===');
  for (const r of stable) {
    const icon = r.status === 'stable_or_improving' ? '✅' : '⏳';
    console.log(`${icon} ${r.suite}: ${r.trend || r.status}`);
    console.log(`  Current: ${r.current}% | Threshold: ${r.threshold}%`);
    console.log();
  }

  if (MODE === 'alert') {
    const alerts = breachPredictions.filter(r => parseFloat(r.weeksToBreach) <= WARN_WEEKS);
    if (alerts.length > 0) {
      console.log('=== ALERTS ===');
      for (const a of alerts) {
        console.log(`[${a.riskLevel}] ${a.suite}: breach in ${a.weeksToBreach} weeks`);
      }
      process.exit(1); // Alert exit code for CI integration
    } else {
      console.log('No urgent alerts.');
    }
  }
}

main().catch(e => { console.error(e); process.exit(1); });
