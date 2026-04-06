/**
 * check-node-consistency.mjs — Checks .nvmrc vs engines.node consistency
 * Run: node scripts/check-node-consistency.mjs
 */

import { readdirSync, readFileSync, existsSync } from 'fs';
import { resolve, join } from 'path';

const ROOT = resolve('D:/OpenClaw/workspace/80-PROJECTS');
const NVMRC = resolve('D:/OpenClaw/workspace/.nvmrc');

let nvmrcVersion = '22';
try { nvmrcVersion = readFileSync(NVMRC, 'utf8').trim(); } catch {}

const dirs = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.startsWith('.') && d.name !== 'node_modules')
  .map(d => join(ROOT, d.name));

const issues = [];
for (const dir of dirs) {
  const pkgPath = join(dir, 'package.json');
  const nvmrcPath = join(dir, '.nvmrc');
  const rel = dir.replace(ROOT, '').replace(/\\/g, '/').replace(/^\//, '');
  try {
    const pkg = JSON.parse(readFileSync(pkgPath, 'utf8'));
    const engines = pkg.engines?.node || null;
    const hasNvmrc = existsSync(nvmrcPath);
    if (engines && engines !== nvmrcVersion) {
      issues.push({ rel, engines, nvmrc: nvmrcVersion, hasNvmrc });
    }
  } catch {}
}

if (issues.length === 0) {
  console.log(`\n  All ${dirs.length} projects consistent with .nvmrc (${nvmrcVersion})\n`);
} else {
  console.log(`\n  Projects with engines.node ≠ .nvmrc (${nvmrcVersion}):`);
  for (const { rel, engines, hasNvmrc } of issues) {
    console.log(`  ✗ ${rel}: engines="${engines}" nvmrc="${nvmrcVersion}" hasNvmrc=${hasNvmrc}`);
  }
  console.log(`\n  ${issues.length} project(s) inconsistent\n`);
}
