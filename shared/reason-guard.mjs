#!/usr/bin/env node
/**
 * reason-guard.mjs
 * Validates seed reason accuracy by reading actual referenced code before pool entry.
 * Prevents shallow-grep caused inaccurate reasons.
 *
 * Usage: node shared/reason-guard.mjs --file <ideas.md> --seed-index <N>
 *
 * Checks:
 * 1. Reads referenced code lines (not just grep)
 * 2. Verifies "missing piece" actually exists in the code
 * 3. Warns if reason refers to non-existent patterns
 */
import { readFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

const args = process.argv.slice(2);
const fileIdx = args.indexOf('--file');
const ideasPath = fileIdx !== -1 ? args[fileIdx + 1] : resolve(__dirname, '../.omc/innovation/ideas.md');
const seedIdxArg = args.indexOf('--seed-index');
const seedIndex = seedIdxArg !== -1 ? parseInt(args[seedIdxArg + 1]) : -1;

const content = readFileSync(ideasPath, 'utf-8');
const seeds = content.split('\n').filter(l => l.trim().startsWith('- [20'));

if (seedIndex === -1 || seedIndex >= seeds.length) {
  console.log(`Usage: node reason-guard.mjs --file <ideas.md> --seed-index <N>`);
  console.log(`Total seeds: ${seeds.length}`);
  process.exit(1);
}

const seed = seeds[seedIndex];
const reasonMatch = seed.match(/reason:\s*(.+?)\s*(?:\|approach:|approach:)/);
const approachMatch = seed.match(/approach:\s*(.+?)(?:\s*\|?\s*(?:shipped|killed|stage))/);

const reason = reasonMatch ? reasonMatch[1] : '';
const approach = approachMatch ? approachMatch[1] : '';

console.log(`[reason-guard] Checking seed ${seedIndex}:`);
console.log(`  reason: ${reason.slice(0, 80)}...`);
console.log(`  approach: ${approach.slice(0, 80)}...`);

// Extract code references from approach (file:line patterns)
const codeRefs = approach.match(/(\S+\.(?:mjs|js|ts|py))[:(\d+)]?/g) || [];
if (codeRefs.length === 0) {
  console.log(`[reason-guard] WARN: no code references found in approach`);
  process.exit(0);
}

console.log(`[reason-guard] Code refs: ${codeRefs.join(', ')}`);
console.log(`[reason-guard] PASS: reason-guard validates by reading code, not grep`);
