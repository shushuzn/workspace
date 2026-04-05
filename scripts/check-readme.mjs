/**
 * check-readme.mjs
 * Reports projects in 80-PROJECTS/ with missing or tiny README.md files.
 * Run: node scripts/check-readme.mjs
 */

import { readFileSync, readdirSync, statSync } from 'fs';
import { join, resolve } from 'path';

const WORKSPACE = resolve('D:/OpenClaw/workspace/80-PROJECTS');
const THRESHOLD = 500; // bytes

const dirs = readdirSync(WORKSPACE).filter(d => !d.startsWith('.'));

console.log(`\n${'Project'.padEnd(28)} ${'README Size'.padEnd(12)} Status`);
console.log('-'.repeat(55));

let missing = 0, tiny = 0, ok = 0;

for (const dir of dirs) {
  const readmePath = join(WORKSPACE, dir, 'README.md');
  try {
    const stat = statSync(readmePath);
    if (stat.size < THRESHOLD) {
      console.log(`${dir.padEnd(28)} ${stat.size + ' B'.padEnd(12)} TINY`);
      tiny++;
    } else {
      ok++;
    }
  } catch {
    console.log(`${dir.padEnd(28)} ${'---'.padEnd(12)} MISSING`);
    missing++;
  }
}

console.log(`\nmissing: ${missing}  tiny: ${tiny}  ok: ${ok}  total: ${dirs.length}\n`);
