/**
 * check-tsconfig-extends.mjs — Verifies TS projects extend the workspace base config
 * Run: node scripts/check-tsconfig-extends.mjs
 */

import { readdirSync, readFileSync } from 'fs';
import { resolve, join } from 'path';

const ROOT = resolve('D:/OpenClaw/workspace/80-PROJECTS');
const BASE = resolve('D:/OpenClaw/workspace/80-PROJECTS/.tsconfig/base.json');

const dirs = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.startsWith('.') && d.name !== 'node_modules')
  .map(d => join(ROOT, d.name));

const BASE_REL = '../../../.tsconfig/base.json';

const issues = [];
for (const dir of dirs) {
  const tsconfig = join(dir, 'tsconfig.json');
  try {
    const pkg = JSON.parse(readFileSync(tsconfig, 'utf8'));
    if (!pkg.extends) {
      issues.push({ rel: dir.replace(ROOT, '').replace(/\\/g, '/').replace(/^\//, ''), issue: 'no extends' });
    } else if (pkg.extends !== BASE_REL) {
      issues.push({ rel: dir.replace(ROOT, '').replace(/\\/g, '/').replace(/^\//, ''), issue: `extends=${pkg.extends}` });
    }
  } catch {
    // skip
  }
}

if (issues.length === 0) {
  console.log(`\n  All TS projects extend workspace base\n`);
} else {
  console.log(`\n  Projects not extending workspace base:`);
  for (const { rel, issue } of issues) {
    console.log(`  ✗ ${rel}: ${issue}`);
  }
  console.log(`\n  ${issues.length} project(s)\n`);
}
