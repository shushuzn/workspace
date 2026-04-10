#!/usr/bin/env node
// Simplify buildCausalityInfo root computation using Math.min
import { readFileSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __DIR = dirname(fileURLToPath(import.meta.url));
const TARGET = join(__DIR, '..', '80-PROJECTS', 'task-orchestrator', 'src', 'executor.mjs');
let content = readFileSync(TARGET, 'utf8');

// Detect "already patched" state: Math.min(...chain) in buildCausalityInfo
const patchedPattern = /let root = chain\.length\s*>\s*0\s*\?\s*Math\.min\s*\(\s*\.\.\.\s*chain\s*\)\s*:\s*i/;
if (patchedPattern.test(content)) {
  console.log('[patch] ALREADY APPLIED');
  process.exit(0);
}

// Find the old root computation block (handles various indentation)
const oldPattern = /let root = i;\s+for \(const c of chain\)\s*\{[\s\S]+?if \(c < root\)\s*[\s\S]+?root = c;[\s\S]+?\}/;
const newRoot = 'let root = chain.length > 0 ? Math.min(...chain) : i;';

if (!oldPattern.test(content)) {
  console.error('[patch] root computation not found');
  process.exit(1);
}

const next = content.replace(oldPattern, newRoot);
writeFileSync(TARGET, next, 'utf8');
console.log('[patch] buildCausalityInfo root now uses Math.min');
