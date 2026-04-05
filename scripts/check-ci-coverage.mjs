/**
 * check-ci-coverage.mjs
 * Reports which projects have GitHub Actions CI and which don't.
 * Run: node scripts/check-ci-coverage.mjs
 */

import { readdirSync, existsSync } from 'fs';
import { join, resolve } from 'path';

const WORKSPACE = resolve('D:/OpenClaw/workspace/80-PROJECTS');
const dirs = readdirSync(WORKSPACE).filter(d => !d.startsWith('.'));

console.log(`\n${'Project'.padEnd(28)} ${'CI'.padEnd(6)} Workflows`);
console.log('-'.repeat(50));

let hasCi = 0, noCi = 0;

for (const dir of dirs) {
  const wfPath = join(WORKSPACE, dir, '.github', 'workflows');
  const has = existsSync(wfPath);
  if (has) {
    let files = [];
    try { files = readdirSync(wfPath).filter(f => f.endsWith('.yml') || f.endsWith('.yaml')); } catch {}
    console.log(`${dir.padEnd(28)} ${'YES'.padEnd(6)} ${files.join(', ') || '(empty)'}`);
    hasCi++;
  } else {
    console.log(`${dir.padEnd(28)} ${'NO'.padEnd(6)} ---`);
    noCi++;
  }
}

console.log(`\nhas CI: ${hasCi}  no CI: ${noCi}  total: ${dirs.length}\n`);
