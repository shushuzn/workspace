/**
 * count-readme-badges.mjs — Counts badge images in README.md files
 * Run: node scripts/count-readme-badges.mjs
 */

import { readdirSync, readFileSync } from 'fs';
import { resolve, join } from 'path';

const ROOT = resolve('D:/OpenClaw/workspace/80-PROJECTS');
const BADGE_RE = /!\[.+\]\(.+\)/g;

const dirs = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.startsWith('.') && d.name !== 'node_modules')
  .map(d => join(ROOT, d.name));

const results = [];
for (const dir of dirs) {
  const readmePath = join(dir, 'README.md');
  const rel = dir.replace(ROOT, '').replace(/\\/g, '/').replace(/^\//, '');
  try {
    const content = readFileSync(readmePath, 'utf8');
    const matches = content.match(BADGE_RE) || [];
    results.push({ rel, count: matches.length });
  } catch {
    results.push({ rel, count: -1 });
  }
}

results.sort((a, b) => a.count - b.count);
console.log('\n  README badge counts:\n');
for (const { rel, count } of results) {
  if (count === -1) {
    console.log(`    N/A   (no README)  ${rel}`);
  } else {
    console.log(`    ${String(count).padStart(3)} badges  ${rel}`);
  }
}
const zeroBadge = results.filter(r => r.count === 0).length;
console.log(`\n  ${zeroBadge} project(s) with 0 badges\n`);
