#!/usr/bin/env node
// Detect duplicate TOP-LEVEL const declarations in .mjs files
// Only module-scope duplicates (same file, depth=0) cause SyntaxError
import { readdirSync, readFileSync } from 'fs';
import { join } from 'path';

const TARGET = process.argv[2] || '80-PROJECTS/task-orchestrator/src';
const MODULE_INDENT = 8; // module-level lines start with exactly 8 spaces

function getModuleConsts(content) {
  const consts = [];
  const lines = content.split('\n');
  for (const line of lines) {
    // Only top-level lines (exactly 8 spaces indent, not more, not less)
    const indent = line.match(/^(\s*)/)[1].length;
    if (indent !== MODULE_INDENT) continue;
    const trimmed = line.trim();
    if (!trimmed.startsWith('const ')) continue;
    // Skip import/export
    if (/^(import|export)/.test(trimmed)) continue;
    // Extract variable name
    const m = trimmed.match(/^const\s+(\w+)/);
    if (m) consts.push(m[1]);
  }
  return consts;
}

const args = process.argv.slice(3);
const files = args.length > 0 ? args.map(f => ({ name: f, isFile: true })) :
  readdirSync(TARGET, { withFileTypes: true }).filter(f => f.name.endsWith('.mjs'));

let totalDupes = 0;
for (const file of files) {
  const content = readFileSync(join(TARGET, file.name), 'utf8');
  const consts = getModuleConsts(content);
  const seen = new Set();
  for (const c of consts) {
    if (seen.has(c)) {
      console.log(`${file.name}: ${c}`);
      totalDupes++;
    }
    seen.add(c);
  }
}

if (totalDupes === 0) {
  if (files.length === 1) {
    console.log(`[OK] No module-level duplicate const in ${files[0].name}`);
  } else {
    console.log('[OK] No module-level duplicate const declarations found');
  }
}
process.exit(totalDupes > 0 ? 1 : 0);
