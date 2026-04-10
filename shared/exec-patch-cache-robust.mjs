#!/usr/bin/env node
// Protect loadCache JSON.parse in try-catch
import { readFileSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __DIR = dirname(fileURLToPath(import.meta.url));
const TARGET = join(__DIR, '..', '80-PROJECTS', 'task-orchestrator', 'src', 'executor.mjs');
let content = readFileSync(TARGET, 'utf8');

// Detect "already patched" state: outer catch (e) at loadCache level
const patchedPattern = /        \} catch \(e\) \{\s*\n\s*console\.warn\(`\[cache\] failed to parse/;
if (patchedPattern.test(content)) {
  console.log('[patch] ALREADY APPLIED');
  process.exit(0);
}

// The un-patched loadCache has bare "catch {}" at the outer try level
const outerTryEnd = /(\n        try \{\n[\s\S]+?\n        \}) catch \{\}/;
if (!outerTryEnd.test(content)) {
  console.error('[patch] loadCache try-catch block not found — may already be patched differently');
  process.exit(1);
}

const next = content.replace(outerTryEnd, '$1 catch (e) {\n            console.warn(`[cache] failed to parse cache file: ${e.message}`);\n        }');
writeFileSync(TARGET, next, 'utf8');
console.log('[patch] loadCache JSON.parse now protected by try-catch');
