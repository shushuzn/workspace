/**
 * check-package-json-valid.mjs — Reports package.json files with invalid JSON
 * Run: node scripts/check-package-json-valid.mjs
 */

import { readdirSync, readFileSync } from 'fs';
import { resolve, join } from 'path';

const ROOT = resolve('D:/OpenClaw/workspace/80-PROJECTS');

const dirs = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.startsWith('.') && d.name !== 'node_modules')
  .map(d => join(ROOT, d.name));

const invalid = [];
const missing = [];
for (const dir of dirs) {
  const pkgPath = join(dir, 'package.json');
  const rel = dir.replace(ROOT, '').replace(/\\/g, '/').replace(/^\//, '');
  try {
    readFileSync(pkgPath, 'utf8');
    try {
      JSON.parse(readFileSync(pkgPath, 'utf8'));
    } catch (e) {
      invalid.push({ rel, error: e.message.slice(0, 80) });
    }
  } catch (e) {
    if (e.code === 'ENOENT') missing.push(rel);
    else invalid.push({ rel, error: e.message.slice(0, 80) });
  }
}

if (invalid.length === 0 && missing.length === 0) {
  console.log(`\n  All ${dirs.length} package.json files are valid JSON\n`);
} else {
  if (invalid.length > 0) {
    console.log(`\n  Invalid JSON:`);
    for (const { rel, error } of invalid) console.log(`  ✗ ${rel}: ${error}`);
  }
  if (missing.length > 0) {
    console.log(`\n  Missing package.json (${missing.length}): ${missing.join(', ')}`);
  }
  console.log('');
}
