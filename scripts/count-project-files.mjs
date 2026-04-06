/**
 * count-project-files.mjs — Counts source files per project
 * Run: node scripts/count-project-files.mjs
 */

import { readdirSync, statSync } from 'fs';
import { resolve, join } from 'path';

const ROOT = resolve('D:/OpenClaw/workspace/80-PROJECTS');
const EXTS = new Set(['.ts', '.tsx', '.js', '.jsx', '.py']);

function countFiles(dir) {
  let count = 0;
  try {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      if (entry.name === 'node_modules' || entry.name === '.git') continue;
      if (entry.isDirectory()) {
        count += countFiles(join(dir, entry.name));
      } else {
        const ext = entry.name.lastIndexOf('.');
        if (ext > 0 && EXTS.has(entry.name.slice(ext))) count++;
      }
    }
  } catch {}
  return count;
}

const dirs = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.startsWith('.') && d.name !== 'node_modules')
  .map(d => join(ROOT, d.name));

const projects = dirs.map(d => ({
  name: d.replace(ROOT, '').replace(/\\/g, '/').replace(/^\//, ''),
  count: countFiles(d)
}));

projects.sort((a, b) => b.count - a.count);
const max = projects[0].count;

console.log('\n  Source file count per project:\n');
for (const { name, count } of projects) {
  const bar = '█'.repeat(Math.round((count / max) * 30));
  console.log(`    ${String(count).padStart(4)}  ${bar.padEnd(30)}  ${name}`);
}
console.log(`\n  ${projects.length} projects\n`);
