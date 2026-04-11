#!/usr/bin/env node
/**
 * scripts/ci-state-update.mjs
 * Updates ci-state.json from current CI artifacts.
 * Run as part of post-CI chain.
 */
import { readFileSync, existsSync, writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const STATE_FILE = join(__dirname, '..', 'ci-state.json');
const COV_REPORT = join(__dirname, '..', 'coverage-report.json');
const TEST_REPORT = join(__dirname, '..', 'test-report.json');

function loadState() {
  if (!existsSync(STATE_FILE)) return {};
  try { return JSON.parse(readFileSync(STATE_FILE, 'utf8')); }
  catch { return {}; }
}

function saveState(state) {
  writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
}

async function main() {
  const state = loadState();

  // Update lastRun
  state.lastRun = {
    timestamp: new Date().toISOString(),
    passed: true
  };

  // Update coverage from coverage-report.json
  if (existsSync(COV_REPORT)) {
    try {
      const cov = JSON.parse(readFileSync(COV_REPORT, 'utf8'));
      state.coverage = {};
      for (const s of (cov.suites || [])) {
        state.coverage[s.suite] = s.coverage;
      }
      state.lastRun.passed = cov.pass !== false;
    } catch { /* ignore */ }
  }

  // Update health from ci-health.json
  const HEALTH_FILE = join(__dirname, '..', 'ci-health.json');
  if (existsSync(HEALTH_FILE)) {
    try {
      const h = JSON.parse(readFileSync(HEALTH_FILE, 'utf8'));
      state.health = { score: h.score, date: h.date };
    } catch { /* ignore */ }
  }

  state.lastUpdated = new Date().toISOString();
  saveState(state);

  console.log('ci-state.json updated');
  if (state.coverage) {
    for (const [suite, cov] of Object.entries(state.coverage)) {
      console.log(`  ${suite}: ${cov}%`);
    }
  }
}

main().catch(e => { console.error(e); process.exit(1); });
