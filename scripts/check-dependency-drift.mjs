/**
 * check-dependency-drift.mjs — Detect dependency drift in 80-PROJECTS
 *
 * Finds:
 *   - Installed but not declared (undeclared deps — bloat risk)
 *   - Declared but not imported (dead weight — unnecessary install)
 *
 * Run: node scripts/check-dependency-drift.mjs [--csv [path]]
 */

import { readdirSync, readFileSync, existsSync } from 'fs';
import { resolve, join } from 'path';

const ROOT = resolve('D:/OpenClaw/workspace/80-PROJECTS');
const CSV = process.argv.includes('--csv');
const CSV_PATH = (() => {
  const i = process.argv.indexOf('--csv');
  return i >= 0 && process.argv[i + 1] && !process.argv[i + 1].startsWith('--')
    ? process.argv[i + 1]
    : 'dependency-drift.csv';
})();

// Scan a single project for JS/TS imports
function scanImports(dir) {
  const imports = new Set();
  try {
    const entries = readdirSync(dir, { withFileTypes: true });
    for (const e of entries) {
      if (e.isDirectory() && !['node_modules', '.git', 'dist', 'build', '.venv', '__pycache__'].includes(e.name)) {
        scanImports(join(dir, e.name)).forEach(x => imports.add(x));
      } else if (e.isFile() && /\.(js|ts|mjs|jsx|tsx)$/.test(e.name)) {
        try {
          const content = readFileSync(join(dir, e.name), 'utf8');
          // Named imports: import { x } from 'pkg' or import x from 'pkg'
          const re = /import\s+.*?from\s+['"]([^'"]+)['"]/g;
          let m;
          while ((m = re.exec(content)) !== null) {
            const p = m[1];
            if (!p.startsWith('.') && !p.startsWith('@') && !p.startsWith('/')) imports.add(p.split('/')[0]);
          }
          // require('pkg')
          const re2 = /require\s*\(\s*['"]([^'"]+)['"]\s*\)/g;
          while ((m = re2.exec(content)) !== null) {
            const p = m[1];
            if (!p.startsWith('.') && !p.startsWith('@') && !p.startsWith('/')) imports.add(p.split('/')[0]);
          }
        } catch {}
      }
    }
  } catch {}
  return imports;
}

function getDeclaredDeps(pkgPath) {
  try {
    const pkg = JSON.parse(readFileSync(pkgPath, 'utf8'));
    const all = { ...pkg.dependencies, ...pkg.devDependencies };
    return new Set(Object.keys(all));
  } catch {
    return new Set();
  }
}

const dirs = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.startsWith('.') && !['node_modules'].includes(d.name))
  .map(d => join(ROOT, d.name));

console.log('\n  Dependency Drift Report\n  ' + '-'.repeat(72));
console.log('  Project                    Undeclared          Unused          Score');
console.log('  ' + '-'.repeat(72));

const rows = [];
let totalUndeclared = 0, totalUnused = 0;

for (const dir of dirs) {
  const name = dir.replace(ROOT, '').replace(/\\/g, '/').replace(/^\//, '');
  const pkgPath = join(dir, 'package.json');
  if (!existsSync(pkgPath)) continue;

  const declared = getDeclaredDeps(pkgPath);
  const imported = scanImports(dir);

  const undeclared = [...imported].filter(i => !declared.has(i) && !i.includes('/'));
  const unused = [...declared].filter(d => !imported.has(d) && !d.startsWith('@'));

  totalUndeclared += undeclared.length;
  totalUnused += unused.length;

  const score = Math.max(0, 100 - undeclared.length * 5 - unused.length * 2);
  const grade = score >= 80 ? 'A' : score >= 60 ? 'B' : score >= 40 ? 'C' : score >= 20 ? 'D' : 'F';

  const nameOut = name.length > 26 ? name.slice(0, 23) + '...' : name.padEnd(26);
  const udOut = undeclared.length === 0 ? '—'.padEnd(20) : undeclared.slice(0, 3).join(', ').padEnd(20);
  const udWarn = undeclared.length > 0 ? `+${undeclared.length}` : '';
  const unOut = unused.length === 0 ? '—'.padEnd(19) : unused.slice(0, 3).join(', ').padEnd(19);
  const unWarn = unused.length > 0 ? `+${unused.length}` : '';

  console.log(`  ${nameOut} ${udOut}${udWarn}  ${unOut}${unWarn}  [${grade}] ${score}`);

  if (undeclared.length || unused.length) {
    rows.push({ name, undeclared: undeclared.slice(0, 10), unused: unused.slice(0, 10), score });
  }
}

console.log('  ' + '-'.repeat(72));
console.log(`\n  ${totalUndeclared} undeclared deps, ${totalUnused} unused deps total`);

// CSV export
if (CSV) {
  const header = 'project,undeclared_count,undeclared_deps,unused_count,unused_deps,score';
  const lines = rows.map(r =>
    `${r.name},${r.undeclared.length},"${r.undeclared.join('|')}","${r.undeclared.length}","${r.unused.join('|')}",${r.score}`
  );
  const csv = [header, ...lines].join('\n');
  require('fs').writeFileSync(CSV_PATH, csv, 'utf8');
  console.log(`  CSV: ${CSV_PATH}`);
}
