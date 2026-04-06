/**
 * check-tsconfig-present.mjs — Reports TypeScript projects missing tsconfig.json
 * Run: node scripts/check-tsconfig-present.mjs
 */

import { readdirSync, readFileSync } from 'fs';
import { resolve, join } from 'path';

const ROOT = resolve('D:/OpenClaw/workspace/80-PROJECTS');

const dirs = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.startsWith('.') && d.name !== 'node_modules')
  .map(d => join(ROOT, d.name));

const missing = [];
const has = [];
for (const dir of dirs) {
  const pkgPath = join(dir, 'package.json');
  const rel = dir.replace(ROOT, '').replace(/\\/g, '/').replace(/^\//, '');
  try {
    const pkg = JSON.parse(readFileSync(pkgPath, 'utf8'));
    if (!pkg.language || !pkg.language.startsWith('TypeScript')) continue;
    // Check for .ts/.tsx files
    const srcPath = join(dir, 'src');
    let hasTS = false;
    try {
      for (const f of readdirSync(srcPath)) {
        if (f.endsWith('.ts') || f.endsWith('.tsx')) { hasTS = true; break; }
      }
    } catch {}
    if (hasTS) {
      const tcPath = join(dir, 'tsconfig.json');
      let hasTC = false;
      try { readFileSync(tcPath); hasTC = true; } catch {}
      if (!hasTC) missing.push(rel);
      else has.push(rel);
    }
  } catch {}
}

if (missing.length === 0) {
  console.log(`\n  All TS projects have tsconfig.json\n`);
} else {
  console.log(`\n  TS projects missing tsconfig.json (${missing.length}):`);
  missing.forEach(p => console.log(`  ✗ ${p}`));
  console.log('');
}
