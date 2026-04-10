#!/usr/bin/env node
// Simplify buildCausalityInfo root computation using Math.min
import { readFileSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __DIR = dirname(fileURLToPath(import.meta.url));
const TARGET = join(__DIR, '..', '80-PROJECTS', 'task-orchestrator', 'src', 'executor.mjs');
let content = readFileSync(TARGET, 'utf8');

// Find the root computation block using a regex that ignores whitespace differences
const oldPattern = /let root = i;\s+for \(const c of chain\) \{\s+if \(c < root\)\s+root = c;\s+\}/;
const newRoot = 'let root = chain.length > 0 ? Math.min(...chain) : i;';

if (!oldPattern.test(content)) {
  console.error('[patch] root computation not found');
  process.exit(1);
}

const next = content.replace(oldPattern, newRoot);
writeFileSync(TARGET, next, 'utf8');
console.log('[patch] buildCausalityInfo root now uses Math.min');
