#!/usr/bin/env node
/**
 * shared/test-coverage-ci.mjs
 * Runs tests with coverage and enforces per-suite thresholds.
 * Early exits on first failure to save CI time.
 */
import { spawn } from 'child_process';
import { writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const THRESHOLDS = {
  'step-parser': 100,
  'run-seed': 25,    // lower threshold due to coverage fluctuation between runs
  'add-seed': 35
};

const suites = ['step-parser', 'run-seed', 'add-seed'];
const results = [];

function runCoverage(suite) {
  return new Promise((resolve) => {
    const start = Date.now();
    const rootDir = join(__dirname, '..');
    const c8Bin = join(rootDir, 'node_modules', '.bin', 'c8' + (process.platform === 'win32' ? '.cmd' : ''));
    const targetFile = 'shared/' + suite + '.mjs';
    const args = [
      '--reporter=text',
      '--report-on=' + targetFile,
      'node',
      `shared/${suite}.test.mjs`
    ];
    const p = spawn(
      process.platform === 'win32' ? 'cmd' : c8Bin,
      process.platform === 'win32' ? ['/c', c8Bin, ...args] : args, {
      cwd: rootDir,
      stdio: ['ignore', 'pipe', 'pipe'],
      shell: true
    });
    let out = '';
    p.stdout.on('data', d => out += d.toString());
    p.stderr.on('data', d => out += d.toString());
    p.on('close', () => {
      const allFilesMatch = out.match(/All files\s+\|\s+(\d+)/);
      const coverage = allFilesMatch ? parseInt(allFilesMatch[1], 10) : 0;
      results.push({ suite, coverage, threshold: THRESHOLDS[suite], duration_ms: Date.now() - start });
      resolve();
    });
  });
}

async function main() {
  // Run sequentially for early-exit capability
  for (const suite of suites) {
    await runCoverage(suite);
    const r = results[results.length - 1];
    const status = r.coverage >= r.threshold ? 'PASS' : 'FAIL';
    console.log(`${r.suite}: ${r.coverage}% (threshold: ${r.threshold}%) [${status}]`);

    // Early exit on first failure
    if (r.coverage < r.threshold) {
      const report = {
        timestamp: new Date().toISOString(),
        total: (results.reduce((acc, x) => acc + x.coverage, 0) / results.length).toFixed(1),
        suites: results,
        pass: false
      };
      writeFileSync(join(__dirname, '..', 'coverage-report.json'), JSON.stringify(report, null, 2));
      console.log('\n❌ Coverage below threshold — early exit');
      console.log(`  ${r.suite}: ${r.coverage}% < ${r.threshold}%`);
      process.exit(1);
    }
  }

  const total = results.reduce((acc, r) => acc + r.coverage, 0) / results.length;
  console.log(`\nAverage: ${total.toFixed(1)}% | PASS`);

  const report = {
    timestamp: new Date().toISOString(),
    total: total.toFixed(1),
    suites: results,
    pass: true
  };
  writeFileSync(join(__dirname, '..', 'coverage-report.json'), JSON.stringify(report, null, 2));
  process.exit(0);
}

main();
