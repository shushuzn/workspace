/**
 * check-empty-projects.mjs — Detects empty directories with no package.json or README
 * Run: node scripts/check-empty-projects.mjs
 */

import { readdirSync, existsSync } from 'fs';
import { resolve, join } from 'path';

const ROOT = resolve('D:/OpenClaw/workspace/80-PROJECTS');

const dirs = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.startsWith('.') && d.name !== 'node_modules')
  .map(d => join(ROOT, d.name));

const issues = [];
for (const dir of dirs) {
  const rel = dir.replace(ROOT, '').replace(/\\/g, '/').replace(/^\//, '');
  const hasPkg = existsSync(join(dir, 'package.json'));
  const hasReadme = existsSync(join(dir, 'README.md'));
  if (!hasPkg && !hasReadme) {
    issues.push(rel);
  }
}

if (issues.length === 0) {
  console.log(`\n  All ${dirs.length} projects have package.json or README\n`);
} else {
  console.log(`\n  Empty projects (no package.json, no README):`);
  for (const rel of issues) {
    console.log(`  ✗ ${rel}`);
  }
  console.log(`\n  ${issues.length} empty project(s)\n`);
}
