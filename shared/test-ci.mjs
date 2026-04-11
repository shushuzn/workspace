#!/usr/bin/env node
/**
 * shared/test-ci.mjs
 * Unified test runner for CI - outputs single JSON report.
 */
import { spawn } from 'child_process';
import { writeFileSync, mkdirSync } from 'fs';
import { join } from 'path';

const suites = ['step-parser', 'run-seed', 'add-seed'];
const results = [];

function run(suite) {
  return new Promise((resolve) => {
    const start = Date.now();
    const p = spawn('node', [`shared/${suite}.test.mjs`, '--json'], {
      stdio: ['ignore', 'pipe', 'pipe']
    });
    let out = '';
    p.stdout.on('data', d => out += d.toString());
    p.stderr.on('data', d => out += d.toString());
    p.on('close', () => {
      try {
        const json = JSON.parse(out.trim());
        results.push({ ...json, duration_ms: Date.now() - start });
      } catch (e) {
        results.push({ suite, error: out, duration_ms: Date.now() - start });
      }
      resolve();
    });
  });
}

async function main() {
  await Promise.all(suites.map(run));

  const total = results.reduce((acc, r) => ({
    passed: acc.passed + (r.passed || 0),
    failed: acc.failed + (r.failed || 0)
  }), { passed: 0, failed: 0 });

  const report = {
    timestamp: new Date().toISOString(),
    total,
    suites: results
  };

  console.log(JSON.stringify(report));

  // Write to artifact path if set
  if (process.env.GITHUB_STEP_SUMMARY) {
    writeFileSync(join(process.env.GITHUB_STEP_SUMMARY), JSON.stringify(report, null, 2));
  }

  process.exit(total.failed > 0 ? 1 : 0);
}

main();
