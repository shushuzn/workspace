/**
 * check-npmrc.mjs — Checks .npmrc consistency with workspace baseline
 * Run: node scripts/check-npmrc.mjs
 */

import { readdirSync, readFileSync, existsSync } from 'fs';
import { resolve, join } from 'path';

const ROOT = resolve('D:/OpenClaw/workspace/80-PROJECTS');
const BASELINE = resolve('D:/OpenClaw/workspace/.npmrc');

const baseline = (() => {
  try { return readFileSync(BASELINE, 'utf8').trim(); } catch { return ''; }
})();

const dirs = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.startsWith('.') && d.name !== 'node_modules')
  .map(d => join(ROOT, d.name));

const issues = [];
for (const dir of dirs) {
  const npmrcPath = join(dir, '.npmrc');
  const rel = dir.replace(ROOT, '').replace(/\\/g, '/').replace(/^\//, '');
  if (existsSync(npmrcPath)) {
    const content = readFileSync(npmrcPath, 'utf8').trim();
    if (content !== baseline) {
      issues.push({ rel, local: content.slice(0, 60) });
    }
  }
}

if (issues.length === 0) {
  console.log(`\n  All .npmrc files match workspace baseline\n`);
} else {
  console.log(`\n  Projects with .npmrc different from workspace baseline:`);
  for (const { rel, local } of issues) {
    console.log(`  ✗ ${rel}: "${local}"`);
  }
  console.log(`\n  ${issues.length} project(s) with divergent .npmrc\n`);
}
