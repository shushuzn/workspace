#!/usr/bin/env node
/**
 * shared/create-check-run.mjs
 * Generates GitHub Check Run payload from test-report.json + coverage-report.json
 */
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const report = JSON.parse(readFileSync(join(__dirname, '..', 'test-report.json'), 'utf8'));

// Load coverage data if available
let coverageData = null;
try {
  const covPath = join(__dirname, '..', 'coverage-report.json');
  if (existsSync(covPath)) {
    coverageData = JSON.parse(readFileSync(covPath, 'utf8'));
  }
} catch (e) { /* ignore */ }

const failedTests = report.suites.flatMap(s =>
  (s.results || []).filter(r => r.status === 'fail').map(r => '* ' + r.name + ': ' + (r.error || 'failed'))
);

// Build summary with coverage
const summaryParts = report.suites.map(s => {
  const cov = coverageData ? coverageData.suites.find(c => c.suite === s.suite) : null;
  const covStr = cov ? ` (cov: ${cov.coverage}%)` : '';
  return `${s.suite}: ${s.passed}/${s.passed+s.failed} in ${s.duration_ms}ms${covStr}`;
});
if (coverageData) summaryParts.push(`Average coverage: ${coverageData.total}%`);

const output = {
  title: `${report.total.passed} passed, ${report.total.failed} failed${coverageData && !coverageData.pass ? ' — COVERAGE FAIL' : ''}`,
  summary: summaryParts.join('\n')
};
if (failedTests.length > 0) {
  output.text = 'Failed Tests:\n' + failedTests.join('\n');
} else if (coverageData && !coverageData.pass) {
  const failing = coverageData.suites.filter(s => s.coverage < s.threshold);
  output.text = 'Coverage below threshold:\n' + failing.map(s => `* ${s.suite}: ${s.coverage}% < ${s.threshold}%`).join('\n');
}

// Conclusion: failure if tests fail OR coverage fails
const testFailed = report.total.failed > 0;
const covFailed = coverageData && !coverageData.pass;
const conclusion = (testFailed || covFailed) ? 'failure' : 'success';

const check = { conclusion, output };
writeFileSync('check-run.json', JSON.stringify(check));
console.log('Check run: ' + check.conclusion + (covFailed ? ' (coverage failed)' : ''));
