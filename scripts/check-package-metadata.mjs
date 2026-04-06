/**
 * check-package-metadata.mjs — Reports package.json missing author/license/repository/description
 * Run: node scripts/check-package-metadata.mjs
 */

import { readdirSync, readFileSync } from 'fs';
import { resolve, join } from 'path';

const ROOT = resolve('D:/OpenClaw/workspace/80-PROJECTS');

const dirs = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.startsWith('.') && d.name !== 'node_modules')
  .map(d => join(ROOT, d.name));

const FIELDS = ['author', 'license', 'repository', 'description'];

const results = [];
for (const dir of dirs) {
  const pkgPath = join(dir, 'package.json');
  const rel = dir.replace(ROOT, '').replace(/\\/g, '/').replace(/^\//, '');
  let missing = [];
  try {
    const pkg = JSON.parse(readFileSync(pkgPath, 'utf8'));
    for (const f of FIELDS) {
      if (!pkg[f] || (typeof pkg[f] === 'string' && pkg[f].trim() === '') || (f === 'repository' && !pkg[f])) {
        missing.push(f);
      }
    }
  } catch {
    continue; // skip non-JSON
  }
  if (missing.length > 0) {
    results.push({ rel, missing: missing.join(', ') });
  }
}

if (results.length === 0) {
  console.log(`\n  All projects have complete package.json metadata\n`);
} else {
  console.log(`\n  Projects missing metadata:`);
  for (const { rel, missing } of results) {
    console.log(`  ✗ ${rel}: ${missing}`);
  }
  console.log(`\n  ${results.length} project(s) with missing metadata\n`);
}
