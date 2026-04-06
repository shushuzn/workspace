/**
 * check-package-type.mjs — Checks package.json type field consistency
 * Run: node scripts/check-package-type.mjs
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
    const type = pkg.type;
    if (!type) {
      issues.push({ rel, type: '(missing)' });
    } else if (type !== 'module' && type !== 'commonjs') {
      issues.push({ rel, type: `"${type}"` });
    }
  } catch {}
}

if (issues.length === 0) {
  console.log(`\n  All ${dirs.length} projects have valid type field\n`);
} else {
  console.log(`\n  Projects with invalid type field:`);
  for (const { rel, type } of issues) {
    console.log(`  ✗ ${rel}: type=${type}`);
  }
  console.log(`\n  ${issues.length} project(s) with issues\n`);
}
