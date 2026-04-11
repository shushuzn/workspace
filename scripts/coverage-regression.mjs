#!/usr/bin/env node
/**
 * scripts/coverage-regression.mjs
 * Analyzes coverage regression and suggests root causes.
 *
 * Usage:
 *   node scripts/coverage-regression.mjs              # analyze current coverage-report.json
 *   node scripts/coverage-regression.mjs --latest    # compare with latest history
 *
 * Compares current vs previous coverage, identifies which files/lines caused the drop.
 */
import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const COV_REPORT  = join(__dirname, '..', 'coverage-report.json');
const HISTORY_FILE = join(__dirname, '..', 'coverage-history.jsonl');

const MODE = process.argv.includes('--latest') ? 'latest' : 'current';

// ── Load history ───────────────────────────────────────────────────────────────
function loadHistory() {
  if (!existsSync(HISTORY_FILE)) return [];
  const content = readFileSync(HISTORY_FILE, 'utf8');
  return content.trim().split('\n').filter(Boolean).map(l => {
    try { return JSON.parse(l); } catch { return null; }
  }).filter(Boolean);
}

// ── Find previous coverage entry ───────────────────────────────────────────────
function getPreviousCoverage() {
  const history = loadHistory();
  if (history.length < 2) return null;
  // Last entry is current, second-to-last is previous
  return history[history.length - 2];
}

// ── Analyze regression per suite ───────────────────────────────────────────────
function analyzeRegressions(current, previous) {
  if (!previous) return [];

  const regressions = [];
  for (const curSuite of (current.suites || [])) {
    const prevSuite = (previous.suites || []).find(s => s.suite === curSuite.suite);
    if (!prevSuite) continue;

    const delta = curSuite.coverage - prevSuite.coverage;
    if (delta < 0) {
      regressions.push({
        suite: curSuite.suite,
        current: curSuite.coverage,
        previous: prevSuite.coverage,
        delta,
        threshold: curSuite.threshold,
        riskLevel: delta <= -5 ? 'P1' : delta <= -2 ? 'P2' : 'P3'
      });
    }
  }
  return regressions;
}

// ── Suggest root causes ─────────────────────────────────────────────────────────
function suggestRootCauses(regression) {
  const suggestions = [];
  const { suite, delta } = regression;

  // Suite-specific heuristics
  if (suite === 'step-parser') {
    suggestions.push({
      file: `shared/${suite}.mjs`,
      possible: [
        `new branch in stepTypeClassification() not covered (${Math.abs(delta)}% drop)`,
        `new step type pattern in READONLY_PREFIXES not tested`,
        `edge case in extractAllSteps() missing test coverage`
      ]
    });
  } else if (suite === 'run-seed') {
    suggestions.push({
      file: `shared/${suite}.mjs`,
      possible: [
        `new validation branch in approach validation not covered`,
        `error handling path in seed execution not tested`,
        `new --flag added to run-seed.mjs without corresponding test`
      ]
    });
  } else if (suite === 'add-seed') {
    suggestions.push({
      file: `shared/${suite}.mjs`,
      possible: [
        `new validation in reason/approach parsing not covered`,
        `error path in ideas.md writing not tested`,
        `new angle/tag parsing branch without test`
      ]
    });
  }

  // General heuristics
  suggestions.push({
    file: `shared/${suite}.test.mjs`,
    possible: [
      `test case for new code path missing`,
      `assertion not strict enough (covered but not asserted)`,
      `mock/fixture not updated after interface change`
    ]
  });

  return suggestions;
}

// ── Main ──────────────────────────────────────────────────────────────────────
async function main() {
  console.log('\n=== Coverage Regression Analysis ===\n');

  if (!existsSync(COV_REPORT)) {
    console.error('coverage-report.json not found. Run tests first.');
    process.exit(1);
  }

  const current = JSON.parse(readFileSync(COV_REPORT, 'utf8'));
  const previous = getPreviousCoverage();

  if (!previous) {
    console.log('No previous coverage data found. Need at least 2 history entries.');
    process.exit(0);
  }

  const regressions = analyzeRegressions(current, previous);

  if (regressions.length === 0) {
    console.log('No regressions detected. All suites are stable or improved.\n');
    return;
  }

  console.log(`Found ${regressions.length} regression(s):\n`);

  for (const r of regressions) {
    console.log(`${r.suite}:`);
    console.log(`  Current: ${r.current}% | Previous: ${r.previous}% | Δ: ${r.delta}% [${r.riskLevel}]`);
    console.log(`  Threshold: ${r.threshold}% | Distance from threshold: ${r.current - r.threshold}%`);

    const suggestions = suggestRootCauses(r);
    console.log(`  Possible root causes:`);
    for (const sg of suggestions) {
      for (const p of sg.possible) {
        console.log(`    • ${p}`);
      }
    }
    console.log();
  }

  console.log('=== Suggested Actions ===');
  for (const r of regressions) {
    if (r.riskLevel === 'P1') {
      console.log(`[P1] ${r.suite}: Add test coverage before next merge`);
    } else if (r.riskLevel === 'P2') {
      console.log(`[P2] ${r.suite}: Investigate and add missing test cases`);
    }
  }
  console.log();
}

main().catch(e => { console.error(e); process.exit(1); });
