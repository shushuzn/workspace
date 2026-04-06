/**
 * check-keywords.mjs — Reports projects with missing or empty keywords field
 * Run: node scripts/check-keywords.mjs
 */

import { readdirSync, readFileSync } from 'fs';
import { resolve, join } from 'path';

const ROOT = resolve('D:/OpenClaw/workspace/80-PROJECTS');

const dirs = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.startsWith('.') && d.name !== 'node_modules')
  .map(d => join(ROOT, d.name));

const issues = [];
for (const dir of dirs) {
  const pkgPath = join(dir, 'package.json');
  const rel = dir.replace(ROOT, '').replace(/\\/g, '/').replace(/^\//, '');
  try {
    const pkg = JSON.parse(readFileSync(pkgPath, 'utf8'));
    if (!pkg.keywords || !Array.isArray(pkg.keywords) || pkg.keywords.length === 0) {
      issues.push({ rel, hasField: !!pkg.keywords, isArray: Array.isArray(pkg.keywords) });
    }
  } catch {}
}

if (issues.length === 0) {
  console.log(`\n  All ${dirs.length} projects have keywords\n`);
} else {
  console.log(`\n  Projects with missing/empty keywords (${issues.length}):`);
  for (const { rel, hasField, isArray } of issues) {
    const reason = !hasField ? 'field missing' : 'empty array';
    console.log(`  ✗ ${rel}: ${reason}`);
  }
  console.log(`\n  ${issues.length} project(s) need keywords\n`);
}
