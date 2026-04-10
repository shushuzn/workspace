#!/usr/bin/env node
// Detect duplicate TOP-LEVEL const declarations in .mjs files
// Only module-scope duplicates (same file, same scope) cause SyntaxError
import { readFileSync } from 'fs';

const MODULE_INDENT = 8; // module-level lines start with exactly 8 spaces

function getModuleConstsByScope(content) {
  // Track scope depth and collect consts per scope level
  const lines = content.split('\n');
  let braceDepth = 0; // { } depth
  let parenDepth = 0; // ( ) depth - for arrow functions
  let scopeId = 0; // unique scope identifier
  const scopeMap = new Map(); // scopeId -> Set of const names

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) continue;

    // Update brace depth BEFORE processing the line
    for (const ch of line) {
      if (ch === '{') braceDepth++;
      if (ch === '}') braceDepth--;
    }

    // Skip if inside braces (function/class body)
    if (braceDepth > 0) continue;

    // At module level (braceDepth === 0)
    const indent = line.match(/^(\s*)/)[1].length;
    if (indent !== MODULE_INDENT) continue;

    // Skip import/export/decorator
    if (/^(import|export|class |function |@)/.test(trimmed)) continue;

    // Skip lines that are just braces or control structures
    if (/^[{}]$/.test(trimmed)) continue;
    if (/^(if|for|while|switch|try|catch|return|throw|break|continue)\b/.test(trimmed)) continue;

    if (trimmed.startsWith('const ')) {
      const m = trimmed.match(/^const\s+(\w+)/);
      if (m) {
        if (!scopeMap.has(scopeId)) scopeMap.set(scopeId, new Set());
        scopeMap.get(scopeId).add(m[1]);
      }
    }
  }
  return scopeMap;
}

const args = process.argv.slice(2);
if (args.length === 0) {
  console.log('Usage: node exec-detect-duplicate-const.mjs <file1.mjs> [file2.mjs ...]');
  process.exit(1);
}

let totalDupes = 0;
for (const filePath of args) {
  const content = readFileSync(filePath, 'utf8');
  const scopeMap = getModuleConstsByScope(content);

  const dupes = [];
  for (const [, consts] of scopeMap) {
    const seen = new Set();
    for (const c of consts) {
      if (seen.has(c)) dupes.push(c);
      seen.add(c);
    }
  }

  if (dupes.length > 0) {
    const fileName = filePath.split('/').pop();
    console.log(`${fileName}: ${dupes.join(', ')}`);
    totalDupes += dupes.length;
  } else {
    const fileName = filePath.split('/').pop();
    console.log(`[OK] ${fileName}`);
  }
}

if (totalDupes > 0) {
  console.log(`\nTotal: ${totalDupes} duplicate(s)`);
  process.exit(1);
} else {
  console.log('\nNo duplicate const declarations found');
  process.exit(0);
}
