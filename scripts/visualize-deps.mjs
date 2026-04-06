/**
 * visualize-deps.mjs — Renders ASCII dependency graph from analyze-imports output
 * Run: node scripts/visualize-deps.mjs [--by-type=ts|js|py] [--json]
 */
import { execSync } from 'child_process';
import { readFileSync } from 'fs';
import { join, resolve } from 'path';

const ROOT = resolve('D:/OpenClaw/workspace/80-PROJECTS');
const JSON_MODE = process.argv.includes('--json');
const BY_TYPE = process.argv.find(a => a.startsWith('--by-type='))?.split('=')[1] || 'all';

// Load matrix
let matrix;
try {
  const raw = execSync(`node "${join(ROOT, '../scripts/analyze-imports.mjs')}" --json`, {
    encoding: 'utf8',
    cwd: ROOT,
  });
  matrix = JSON.parse(raw.trim());
} catch {
  console.error('  Failed to run analyze-imports.mjs');
  process.exit(1);
}

if (!matrix || matrix.length === 0) {
  console.log('\n  No dependencies to visualize\n');
  process.exit(0);
}

// Normalize target names (strip workspace:/@openclaw/ prefix)
for (const row of matrix) {
  row.targets = row.targets.map(t =>
    t.replace(/^(workspace:|@openclaw\/)/, '').replace(/^shared-types$/, 'shared-types')
  );
  row.targets = row.targets.filter(Boolean);
}

// Remove self-references
for (const row of matrix) {
  row.targets = row.targets.filter(t => t !== row.from);
}

if (JSON_MODE) {
  console.log(JSON.stringify(matrix, null, 2));
  process.exit(0);
}

// Build adjacency
const nodes = new Set();
nodes.add('80-PROJECTS');
for (const { from, targets } of matrix) {
  nodes.add(from);
  for (const t of targets) nodes.add(t);
}
const nodeList = [...nodes].sort();

// Find max length for box sizing
const maxLen = Math.max(...nodeList.map(n => n.length));

// Box drawing chars
const HB = '─', VB = '│', TL = '┌', TR = '┐', BL = '└', BR = '┘';
const TT = '┬', BT = '┴', CR = '┼';
const LT = '├', RT = '┤';

function box(name, w) {
  const pad = w - name.length;
  return TL + HB.repeat(name.length + 2) + TR + '\n' +
         VB + ' ' + name + ' '.repeat(Math.max(0, pad)) + VB + '\n' +
         BL + HB.repeat(name.length + 2) + BR;
}

function renderGraph(matrix) {
  // Group by target
  const byTarget = {};
  for (const { from, targets } of matrix) {
    for (const t of targets) {
      if (!byTarget[t]) byTarget[t] = new Set();
      byTarget[t].add(from);
    }
  }

  // Print: for each node, show what it depends on (top-down)
  const W = maxLen + 4;

  console.log('\n  Project Dependency Graph (80-PROJECTS)');
  console.log('  ' + HB.repeat(52));

  for (const { from, targets } of matrix) {
    if (targets.length === 0) continue;
    const header = VB + ' ' + from.padEnd(maxLen + 1) + VB;
    console.log('\n  ' + TL + HB.repeat(maxLen + 3) + TR);
    console.log('  ' + header);
    console.log('  ' + LT + HB.repeat(maxLen + 3) + RT);
    for (const t of targets.sort()) {
      console.log('  ' + VB + ' → ' + t.padEnd(maxLen) + VB);
    }
    console.log('  ' + BL + HB.repeat(maxLen + 3) + BR);
  }

  // Summary
  console.log('\n  ' + HB.repeat(52));
  const allNodes = new Set();
  const allEdges = [];
  for (const { from, targets } of matrix) {
    allNodes.add(from);
    for (const t of targets) { allNodes.add(t); allEdges.push(`${from}→${t}`); }
  }
  console.log(`  Nodes: ${allNodes.size}  |  Edges: ${allEdges.length}`);
  console.log('');
}

renderGraph(matrix);
