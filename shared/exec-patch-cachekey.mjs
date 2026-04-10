#!/usr/bin/env node
// Patch executor.mjs cacheKey to include workingDir
import { readFileSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __DIR = dirname(fileURLToPath(import.meta.url));
const TARGET = join(__DIR, '..', '80-PROJECTS', 'task-orchestrator', 'src', 'executor.mjs');

const content = readFileSync(TARGET, 'utf8');
const old = "return `${step.adapterId}:${step.command}:${step.args.join(',')}`;";
const replacement = "return `${step.adapterId}:${step.command}:${step.args.join(',')}:${step.workingDir||''}`;";

if (!content.includes(old)) {
  console.error('[patch] cacheKey pattern not found — already patched?');
  process.exit(1);
}

const next = content.replace(old, replacement);
writeFileSync(TARGET, next, 'utf8');
console.log('[patch] cacheKey now includes workingDir');
