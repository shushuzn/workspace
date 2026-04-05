/**
 * check-engines.mjs
 * Flags projects missing "engines" field in package.json.
 * Run: node scripts/check-engines.mjs
 */

import { readFileSync, readdirSync } from 'fs';
import { join, resolve } from 'path';

const WORKSPACE = resolve('D:/OpenClaw/workspace/80-PROJECTS');
const dirs = readdirSync(WORKSPACE).filter(d => !d.startsWith('.'));

console.log(`\n${'Project'.padEnd(28)} ${'Node Engine'.padEnd(16)} Status`);
console.log('-'.repeat(50));

let ok = 0, missing = 0;

for (const dir of dirs) {
  const pkgPath = join(WORKSPACE, dir, 'package.json');
  try {
    const pkg = JSON.parse(readFileSync(pkgPath, 'utf8'));
    if (pkg.engines?.node) {
      console.log(`${dir.padEnd(28)} ${pkg.engines.node.padEnd(16)} OK`);
      ok++;
    } else {
      console.log(`${dir.padEnd(28)} ${'---'.padEnd(16)} MISSING`);
      missing++;
    }
  } catch {
    missing++;
  }
}

console.log(`\nhas engines: ${ok}  missing: ${missing}  total: ${dirs.length}\n`);
