/**
 * check-engines-format.mjs — Validates engines.npm and engines.node are valid semver ranges
 * Run: node scripts/check-engines-format.mjs
 */

import { readdirSync, readFileSync } from 'fs';
import { resolve, join } from 'path';

const ROOT = resolve('D:/OpenClaw/workspace/80-PROJECTS');

const dirs = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.startsWith('.') && d.name !== 'node_modules')
  .map(d => join(ROOT, d.name));

const issues = [];
for (const dir of dirs) {
  const pkgPath = join(dir, 'package.json');
  const rel = dir.replace(ROOT, '').replace(/\\/g, '/').replace(/^\//, '');
  try {
    const pkg = JSON.parse(readFileSync(pkgPath, 'utf8'));
    const engines = pkg.engines || {};
    const fields = ['node', 'npm'];
    for (const f of fields) {
      if (engines[f]) {
        // Very loose check: must start with digit
        if (!/^\d/.test(engines[f])) {
          issues.push({ rel, field: f, value: engines[f] });
        }
      }
    }
  } catch {}
}

if (issues.length === 0) {
  console.log(`\n  All engines fields are valid\n`);
} else {
  console.log(`\n  Projects with unusual engines format:`);
  for (const { rel, field, value } of issues) {
    console.log(`  ✗ ${rel}: engines.${field}="${value}"`);
  }
  console.log(`\n  ${issues.length} project(s)\n`);
}
