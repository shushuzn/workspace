/**
 * check-readme-tables.mjs — Checks markdown tables in README.md are column-aligned
 * Run: node scripts/check-readme-tables.mjs
 */

import { readdirSync, readFileSync } from 'fs';
import { resolve, join } from 'path';

const ROOT = resolve('D:/OpenClaw/workspace/80-PROJECTS');

const dirs = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.startsWith('.') && d.name !== 'node_modules')
  .map(d => join(ROOT, d.name));

const issues = [];
for (const dir of dirs) {
  const readmePath = join(dir, 'README.md');
  const rel = dir.replace(ROOT, '').replace(/\\/g, '/').replace(/^\//, '');
  try {
    const content = readFileSync(readmePath, 'utf8');
    const lines = content.split('\n');
    let inTable = false;
    let tableLines = [];
    let headerLine = -1;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (line.startsWith('|') && line.endsWith('|')) {
        if (!inTable) { inTable = true; headerLine = i; tableLines = []; }
        tableLines.push({ n: i + 1, cols: (line.match(/\|/g) || []).length, text: line });
      } else if (inTable) {
        // End of table - check column consistency
        const headerCols = tableLines[0]?.cols;
        for (const t of tableLines) {
          if (t.cols !== headerCols) {
            issues.push({ rel, line: t.n, expected: headerCols, actual: t.cols });
            break;
          }
        }
        inTable = false;
        tableLines = [];
      }
    }
  } catch {}
}

if (issues.length === 0) {
  console.log(`\n  All README tables are properly aligned\n`);
} else {
  console.log(`\n  README tables with column mismatches:`);
  for (const { rel, line, expected, actual } of issues) {
    console.log(`  ✗ ${rel}: line ${line} has ${actual} cols, expected ${expected}`);
  }
  console.log(`\n  ${issues.length} table issue(s)\n`);
}
