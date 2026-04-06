/**
 * check-readme-content.mjs — Checks if README.md has substantial content
 * Run: node scripts/check-readme-content.mjs
 */

import { readdirSync, readFileSync } from 'fs';
import { resolve, join } from 'path';

const ROOT = resolve('D:/OpenClaw/workspace/80-PROJECTS');

const dirs = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.startsWith('.') && d.name !== 'node_modules')
  .map(d => join(ROOT, d.name));

const THRESHOLD = 500; // bytes minimum

const issues = [];
for (const dir of dirs) {
  const rel = dir.replace(ROOT, '').replace(/\\/g, '/').replace(/^\//, '');
  const readmePath = join(dir, 'README.md');
  try {
    const content = readFileSync(readmePath, 'utf8');
    if (content.length < THRESHOLD) {
      issues.push({ rel, size: content.length });
    }
  } catch {}
}

if (issues.length === 0) {
  console.log(`\n  All ${dirs.length} projects have adequate README\n`);
} else {
  console.log(`\n  Small/Tiny READMEs (<${THRESHOLD} bytes):`);
  for (const { rel, size } of issues) {
    console.log(`  ✗ ${rel}: ${size} bytes`);
  }
  console.log(`\n  ${issues.length} project(s)\n`);
}
