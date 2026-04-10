#!/usr/bin/env node
// Patch executor.mjs cacheKey to include workingDir
import { readFileSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __DIR = dirname(fileURLToPath(import.meta.url));
const TARGET = join(__DIR, '..', '80-PROJECTS', 'task-orchestrator', 'src', 'executor.mjs');
const content = readFileSync(TARGET, 'utf8');

// Detect "already patched" state: cacheKey return includes workingDir
// Look for the workingDir||'' part in the cacheKey return statement
const patchedPattern = /return\s+`\$\{step\.adapterId\}:\$\{step\.command\}:\$\{step\.args\.join\([^)]*\)\}:\$\{step\.workingDir\s*\|\|/;
if (patchedPattern.test(content)) {
  console.log('[patch] ALREADY APPLIED');
  process.exit(0);
}

// Find the cacheKey return and patch it
// The un-patched version ends with: ...:\$\{step.args.join(',')}`
const oldPattern = /return\s+`\$\{step\.adapterId\}:\$\{step\.command\}:\$\{step\.args\.join\([^)]*\)\}`;?\s*$/m;
const replacement = "`return \\\`\${step.adapterId}:\${step.command}:\${step.args.join(',')}:\${step.workingDir||''}\\\`;`;";

if (!oldPattern.test(content)) {
  console.error('[patch] cacheKey pattern not found — executor.mjs may have already been patched differently');
  process.exit(1);
}

const next = content.replace(oldPattern, replacement);
writeFileSync(TARGET, next, 'utf8');
console.log('[patch] cacheKey now includes workingDir');
