/**
 * check-semver.mjs — Checks package.json version fields for semver compliance
 * Run: node scripts/check-semver.mjs
 */

import { readdirSync, readFileSync } from 'fs';
import { resolve, join } from 'path';

const ROOT = resolve('D:/OpenClaw/workspace/80-PROJECTS');
const SEMVER = /^\d+\.\d+\.\d+(?:-[\w.]+)?(?:\+[\w.]+)?$/;

const dirs = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.startsWith('.') && d.name !== 'node_modules')
  .map(d => join(ROOT, d.name));

const issues = [];
for (const dir of dirs) {
  const pkgPath = join(dir, 'package.json');
  const rel = dir.replace(ROOT, '').replace(/\\/g, '/').replace(/^\//, '');
  try {
    const pkg = JSON.parse(readFileSync(pkgPath, 'utf8'));
    if (pkg.version && !SEMVER.test(pkg.version)) {
      issues.push({ rel, version: pkg.version });
    }
  } catch {}
}

if (issues.length === 0) {
  console.log(`\n  All ${dirs.length} projects have valid semver\n`);
} else {
  console.log(`\n  Projects with invalid semver (${issues.length}):`);
  for (const { rel, version } of issues) {
    console.log(`  ✗ ${rel}: "${version}"`);
  }
  console.log(`\n  ${issues.length} project(s) with invalid semver\n`);
}
