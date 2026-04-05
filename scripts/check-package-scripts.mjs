/**
 * check-package-scripts.mjs
 * Reports projects missing standard dev/build/test scripts.
 * Run: node scripts/check-package-scripts.mjs
 */

import { readFileSync, readdirSync } from 'fs';
import { join, resolve } from 'path';

const WORKSPACE = resolve('D:/OpenClaw/workspace/80-PROJECTS');
const NEED = ['dev', 'build', 'test'];
const dirs = readdirSync(WORKSPACE).filter(d => !d.startsWith('.'));

console.log(`\n${'Project'.padEnd(28)} ${'Missing Scripts'.padEnd(30)} Status`);
console.log('-'.repeat(65));

let ok = 0, missing = 0;

for (const dir of dirs) {
  const pkgPath = join(WORKSPACE, dir, 'package.json');
  let scripts = [];
  try {
    const pkg = JSON.parse(readFileSync(pkgPath, 'utf8'));
    scripts = Object.keys(pkg.scripts || {});
  } catch {
    console.log(`${dir.padEnd(28)} ${'---'.padEnd(30)} NO PKG`);
    missing++;
    continue;
  }
  const missing_ = NEED.filter(s => !scripts.includes(s));
  if (missing_.length === 0) {
    ok++;
  } else {
    console.log(`${dir.padEnd(28)} ${missing_.join(', ').padEnd(30)} MISSING`);
    missing++;
  }
}

console.log(`\nok: ${ok}  missing scripts: ${missing}  total: ${dirs.length}\n`);
