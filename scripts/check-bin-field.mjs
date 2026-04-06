/**
 * check-bin-field.mjs — Checks package.json bin field points to existing files
 * Run: node scripts/check-bin-field.mjs
 */

import { readdirSync, readFileSync, statSync } from 'fs';
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
    const bin = pkg.bin;
    if (!bin) continue;
    const entries = typeof bin === 'string' ? { [pkg.name]: bin } : bin;
    for (const [name, filePath] of Object.entries(entries)) {
      const absPath = resolve(dir, filePath);
      try { statSync(absPath); } catch {
        issues.push({ rel, bin: name, path: filePath });
      }
    }
  } catch {}
}

if (issues.length === 0) {
  console.log(`\n  All bin fields point to existing files\n`);
} else {
  console.log(`\n  Projects with broken bin entries:`);
  for (const { rel, bin, path } of issues) {
    console.log(`  ✗ ${rel}: bin "${bin}" → "${path}" (not found)`);
  }
  console.log(`\n  ${issues.length} broken bin entry/entries\n`);
}
