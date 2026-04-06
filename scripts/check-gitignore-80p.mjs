/**
 * check-gitignore-80p.mjs — Checks which projects lack .gitignore
 * Run: node scripts/check-gitignore-80p.mjs
 */

import { readdirSync, accessSync } from 'fs';
import { resolve, join } from 'path';

const ROOT = resolve('D:/OpenClaw/workspace/80-PROJECTS');

const dirs = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.startsWith('.') && d.name !== 'node_modules')
  .map(d => join(ROOT, d.name));

const missing = [];
for (const dir of dirs) {
  const rel = dir.replace(ROOT, '').replace(/\\/g, '/').replace(/^\//, '');
  try {
    accessSync(join(dir, '.gitignore'));
  } catch {
    missing.push(rel);
  }
}

if (missing.length === 0) {
  console.log(`\n  All ${dirs.length} projects have .gitignore\n`);
} else {
  console.log(`\n  Projects missing .gitignore (${missing.length}):`);
  missing.forEach(p => console.log(`  - ${p}`));
  console.log('');
}
