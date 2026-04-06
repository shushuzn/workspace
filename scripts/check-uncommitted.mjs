/**
 * check-uncommitted.mjs — Checks for uncommitted changes across all projects
 * Run: node scripts/check-uncommitted.mjs
 */

import { readdirSync } from 'fs';
import { resolve, join } from 'path';
import { execSync } from 'child_process';

const ROOT = resolve('D:/OpenClaw/workspace/80-PROJECTS');

const dirs = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.startsWith('.') && d.name !== 'node_modules')
  .map(d => join(ROOT, d.name));

const results = [];
for (const dir of dirs) {
  try {
    const out = execSync('git status --porcelain', { cwd: dir, encoding: 'utf8', timeout: 5000 });
    if (out.trim()) {
      results.push({ rel: dir.replace(ROOT, '').replace(/\\/g, '/').replace(/^\//, ''), changes: out.trim().split('\n').length });
    }
  } catch {}
}

if (results.length === 0) {
  console.log(`\n  All ${dirs.length} projects clean\n`);
} else {
  console.log(`\n  Uncommitted changes:`);
  for (const { rel, changes } of results) {
    console.log(`  ✗ ${rel} (${changes} file(s))`);
  }
  console.log(`\n  ${results.length} project(s) with uncommitted changes\n`);
}
