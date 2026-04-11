#!/usr/bin/env node
/**
 * shared/post-pr-comment.mjs
 * Posts or edits test summary as PR comment (idempotent).
 * Includes Coverage Delta column (current vs base branch coverage).
 */
import { readFileSync, existsSync, writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const report = JSON.parse(readFileSync(join(__dirname, '..', 'test-report.json'), 'utf8'));

// Load coverage report if available
let coverageData = null;
try {
  const covPath = join(__dirname, '..', 'coverage-report.json');
  if (existsSync(covPath)) {
    coverageData = JSON.parse(readFileSync(covPath, 'utf8'));
  }
} catch (e) { /* ignore */ }

// Load base coverage from history (last entry = base, current = most recent)
const HISTORY_FILE = join(__dirname, '..', 'coverage-history.jsonl');
let baseCoverage = {};
try {
  if (existsSync(HISTORY_FILE)) {
    const content = readFileSync(HISTORY_FILE, 'utf8').trim();
    const lines = content.split('\n').filter(Boolean).map(l => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);
    if (lines.length >= 2) {
      // Second-to-last = base (since last was just appended by coverage-trend.mjs)
      const base = lines[lines.length - 2];
      for (const s of (base.suites || [])) {
        baseCoverage[s.suite] = s.coverage;
      }
    }
  }
} catch (e) { /* ignore */ }

const emoji = report.total.failed > 0 ? '❌' : '✅';

// Delta helper
function deltaIcon(current, base) {
  if (base === undefined || base === null) return '';
  const diff = current - base;
  if (diff > 0) return `+${diff}% 🔺`;
  if (diff < 0) return `${diff}% 🔻`;
  return '—';
}

const comment = `## Test Report ${emoji}

| Suite | Result | Duration | Coverage | Δ from base |
|-------|--------|----------|----------|-------------|
${report.suites.map(s => {
  const cov = coverageData ? coverageData.suites.find(c => c.suite === s.suite) : null;
  const covStr = cov ? `${cov.coverage}%` : 'N/A';
  const base = baseCoverage[s.suite];
  const deltaStr = cov && base !== undefined ? deltaIcon(cov.coverage, base) : 'N/A';
  return `| ${s.suite} | ${s.passed} passed, ${s.failed} failed | ${s.duration_ms}ms | ${covStr} | ${deltaStr} |`;
}).join('\n')}

**Total: ${report.total.passed} passed, ${report.total.failed} failed**

${coverageData ? `**Average Coverage: ${coverageData.total}%**` : ''}

<details>
<summary>JSON Report</summary>

\`\`\`json
${JSON.stringify({ timestamp: report.timestamp, total: report.total }, null, 2)}
\`\`\`
</details>
`;

writeFileSync('pr-comment.json', JSON.stringify({ body: comment }));
console.log('PR comment body prepared');
