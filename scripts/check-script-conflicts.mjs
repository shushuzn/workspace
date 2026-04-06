/**
 * check-script-conflicts.mjs — Detects conflicting script names (e.g. pre/post hooks)
 * Run: node scripts/check-script-conflicts.mjs
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
    const scripts = pkg.scripts || {};
    const names = Object.keys(scripts);
    // Check for pre/post conflicts: prebuild + build, postbuild + build, etc.
    const prefixes = ['pre', 'post'];
    const conflicts = [];
    for (const name of names) {
      for (const pre of prefixes) {
        if (name.startsWith(pre)) {
          const base = name.slice(pre.length);
          if (names.includes(base)) {
            conflicts.push(`${pre}${base} + ${base}`);
          }
        }
      }
    }
    if (conflicts.length > 0) {
      issues.push({ rel, conflicts });
    }
  } catch {}
}

if (issues.length === 0) {
  console.log(`\n  No script conflicts found\n`);
} else {
  console.log(`\n  Projects with script conflicts:`);
  for (const { rel, conflicts } of issues) {
    console.log(`  ✗ ${rel}: ${conflicts.join(', ')}`);
  }
  console.log(`\n  ${issues.length} project(s) with conflicts\n`);
}
