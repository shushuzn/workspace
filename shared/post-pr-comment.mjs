#!/usr/bin/env node
/**
 * shared/post-pr-comment.mjs
 * Posts or edits test summary as PR comment (idempotent).
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

const emoji = report.total.failed > 0 ? '❌' : '✅';
const suites = report.suites.map(s => {
  const cov = coverageData ? coverageData.suites.find(c => c.suite === s.suite) : null;
  const covStr = cov ? `${cov.coverage}%` : 'N/A';
  return `${emoji} **${s.suite}**: ${s.passed}/${s.passed+s.failed} (${s.duration_ms}ms) | Cov: ${covStr}`;
}).join('\n');

const comment = `## Test Report ${emoji}

| Suite | Result | Duration | Coverage |
|-------|--------|----------|----------|
${report.suites.map(s => {
  const cov = coverageData ? coverageData.suites.find(c => c.suite === s.suite) : null;
  const covStr = cov ? `${cov.coverage}%` : 'N/A';
  return `| ${s.suite} | ${s.passed} passed, ${s.failed} failed | ${s.duration_ms}ms | ${covStr} |`;
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
