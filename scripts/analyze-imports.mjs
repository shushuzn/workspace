/**
 * analyze-imports.mjs — Analyzes inter-project imports
 * Run: node scripts/analyze-imports.mjs [--json] [--mermaid]
 */

import { readdirSync, readFileSync } from 'fs';
import { resolve, join, relative } from 'path';

const ROOT = resolve('D:/OpenClaw/workspace/80-PROJECTS');
const IMPORT_RE = /import\s+[\s\S]*?from\s+['"]([^'"]+)['"]/g;
const JSON_MODE = process.argv.includes('--json');
const MERMAID_MODE = process.argv.includes('--mermaid');

const ALL_DIRS = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.startsWith('.') && d.name !== 'node_modules')
  .filter(d => !d.name.startsWith('10-'))
  .map(d => ({ name: d.name, path: join(ROOT, d.name) }));

const PROJECT_NAMES = new Set(ALL_DIRS.map(d => d.name));
const KNOWN_SHARED = new Set(['shared', 'shared-types', 'shared-constants', 'shared-test-fixtures']);
const deps = {};

for (const { name, path } of ALL_DIRS) {
  deps[name] = new Set();
  try {
    function scan(dir) {
      for (const entry of readdirSync(dir, { withFileTypes: true })) {
        if (entry.name === 'node_modules' || entry.name === '.git') continue;
        const full = join(dir, entry.name);
        if (entry.isDirectory()) { scan(full); continue; }
        if (!entry.name.endsWith('.ts') && !entry.name.endsWith('.tsx') && !entry.name.endsWith('.js') && !entry.name.endsWith('.mjs')) continue;
        const content = readFileSync(full, 'utf8');
        let m;
        while ((m = IMPORT_RE.exec(content)) !== null) {
          const imp = m[1];
          if (imp.startsWith('.') || imp.startsWith('@/')) {
            // Resolve relative cross-project imports: ../../multi-agent-hub/src/...
            const absImport = resolve(dir, imp);
            const rel = relative(ROOT, absImport).replace(/\\/g, '/');
            const parts = rel.split('/');
            if (parts[0] && PROJECT_NAMES.has(parts[0]) && parts[0] !== name) {
              deps[name].add(parts[0]);
            }
            continue;
          }
          if (imp.startsWith('workspace:') || imp.startsWith('@openclaw/')) {
            deps[name].add(imp);
          }
          if (KNOWN_SHARED.has(imp)) {
            deps[name].add(imp);
          }
        }
      }
    }
    scan(path);
  } catch {}
}

const matrix = [];
for (const [from, targets] of Object.entries(deps)) {
  if (targets.size === 0) continue;
  matrix.push({ from, targets: [...targets].sort() });
}

if (JSON_MODE) {
  console.log(JSON.stringify(matrix, null, 2));
} else if (MERMAID_MODE) {
  const allNodes = new Set();
  for (const { from, targets } of matrix) {
    allNodes.add(from);
    for (const t of targets) allNodes.add(t);
  }
  if (allNodes.size === 0) {
    console.log('```mermaid\ngraph TD\n    note((No cross-project deps found))\n```');
  } else {
    console.log('```mermaid');
    console.log('graph TD');
    console.log('    subgraph cluster_workspace[Workspace]');
    for (const node of [...allNodes].sort()) {
      const isShared = KNOWN_SHARED.has(node);
      const shape = isShared ? `[${node}]` : `(${node})`;
      console.log(`    ${node}${shape}`);
    }
    console.log('    end');
    for (const { from, targets } of matrix.sort((a,b) => a.from.localeCompare(b.from))) {
      for (const t of targets) {
        console.log(`    ${from} --> ${t}`);
      }
    }
    console.log('```');
  }
} else if (matrix.length === 0) {
  console.log('\n  No inter-project imports found\n');
} else {
  console.log('\n  Inter-project imports:\n');
  for (const { from, targets } of matrix) {
    console.log(`  ${from} →`);
    for (const t of targets) console.log(`    ${t}`);
  }
  console.log('');
}
