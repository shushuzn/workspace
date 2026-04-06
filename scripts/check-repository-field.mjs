/**
 * check-repository-field.mjs — Validates repository.url is standard GitHub format
 * Run: node scripts/check-repository-field.mjs
 */

import { readdirSync, readFileSync } from 'fs';
import { resolve, join } from 'path';

const ROOT = resolve('D:/OpenClaw/workspace/80-PROJECTS');
const URL_RE = /^https:\/\/github\.com\/[a-zA-Z0-9_.-]+\/[a-zA-Z0-9_.-]+$/;

const dirs = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.startsWith('.') && d.name !== 'node_modules')
  .map(d => join(ROOT, d.name));

const issues = [];
for (const dir of dirs) {
  const pkgPath = join(dir, 'package.json');
  const rel = dir.replace(ROOT, '').replace(/\\/g, '/').replace(/^\//, '');
  try {
    const pkg = JSON.parse(readFileSync(pkgPath, 'utf8'));
    const repo = pkg.repository;
    const url = typeof repo === 'string' ? repo : repo?.url;
    if (url && !URL_RE.test(url)) {
      issues.push({ rel, url });
    }
  } catch {}
}

if (issues.length === 0) {
  console.log(`\n  All ${dirs.length} projects have valid repository URLs\n`);
} else {
  console.log(`\n  Projects with non-standard repository URL:`);
  for (const { rel, url } of issues) {
    console.log(`  ✗ ${rel}: "${url}"`);
  }
  console.log(`\n  ${issues.length} project(s) with invalid URL\n`);
}
