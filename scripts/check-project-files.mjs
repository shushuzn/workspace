/**
 * check-project-files.mjs — Detects orphaned files (not directories) in 80-PROJECTS/
 * Run: node scripts/check-project-files.mjs
 */

import { readdirSync } from 'fs';
import { resolve } from 'path';

const ROOT = resolve('D:/OpenClaw/workspace/80-PROJECTS');

const entries = readdirSync(ROOT, { withFileTypes: true });
const orphans = entries.filter(e => !e.isDirectory() && !e.name.startsWith('.') && !e.name.startsWith('README'));

if (orphans.length === 0) {
  console.log(`\n  No orphaned files in 80-PROJECTS/ root\n`);
} else {
  console.log(`\n  Orphaned files (not dirs, not README):`);
  for (const f of orphans) {
    console.log(`  ${f.name}`);
  }
  console.log(`\n  ${orphans.length} file(s) need cleanup\n`);
}
