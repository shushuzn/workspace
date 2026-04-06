/**
 * check-github-dir.mjs — Checks .github directory completeness per project
 * Run: node scripts/check-github-dir.mjs
 */

import { readdirSync, existsSync } from 'fs';
import { resolve, join } from 'path';

const ROOT = resolve('D:/OpenClaw/workspace/80-PROJECTS');

const dirs = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.startsWith('.') && d.name !== 'node_modules')
  .map(d => join(ROOT, d.name));

const issues = [];
for (const dir of dirs) {
  const ghDir = join(dir, '.github');
  const rel = dir.replace(ROOT, '').replace(/\\/g, '/').replace(/^\//, '');
  const hasGh = existsSync(ghDir);
  if (!hasGh) {
    issues.push({ rel, missing: ['.github dir'] });
    continue;
  }
  const missing = [];
  if (!existsSync(join(ghDir, 'workflows'))) missing.push('workflows/');
  if (!existsSync(join(ghDir, 'ISSUE_TEMPLATE'))) missing.push('ISSUE_TEMPLATE/');
  if (!existsSync(join(ghDir, 'PULL_REQUEST_TEMPLATE.md'))) missing.push('PULL_REQUEST_TEMPLATE.md');
  if (missing.length > 0) issues.push({ rel, missing });
}

if (issues.length === 0) {
  console.log(`\n  All projects have complete .github directories\n`);
} else {
  console.log(`\n  Projects with incomplete .github directories:`);
  for (const { rel, missing } of issues) {
    console.log(`  ✗ ${rel}: missing ${missing.join(', ')}`);
  }
  console.log(`\n  ${issues.length} project(s) incomplete\n`);
}
