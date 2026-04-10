#!/usr/bin/env node
/**
 * seed-preflight.mjs — pre-flight check for seed approach scripts
 * Validates all referenced script paths exist before run-seed executes
 * Usage: node shared/seed-preflight.mjs --check
 */
import { existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));

// Direct approach check mode: node seed-preflight.mjs "1. node shared/script.mjs --flag"
const approach = process.argv.slice(2).join(' ');
if (approach) {
  const scriptRefs = [...approach.matchAll(/(?:node|python|bash)\s+([^\s'"]+)/g)];
  let issues = 0;
  for (const ref of scriptRefs) {
    const raw = ref[1];
    // Strip trailing Chinese chars, URL params, etc. — only keep path with extension
    const path = raw.replace(/[^\w\/\.-].*$/, '').replace(/\/$/, '');
    if (!path) continue;
    let fullPath;
    if (path.startsWith('/') || path.match(/^[a-zA-Z]:\\/)) {
      fullPath = path;
    } else {
      fullPath = join(__DIR, '..', path);
    }
    if (!existsSync(fullPath)) {
      console.error(`[PREFLIGHT] MISSING: ${path}`);
      issues++;
    } else {
      console.log(`[PREFLIGHT] OK: ${path}`);
    }
  }
  process.exit(issues > 0 ? 1 : 0);
}

// --check mode: scan all shipped seeds in ideas.md
const { readFileSync } = await import('fs');
const content = readFileSync(join(__DIR, '..', '.omc', 'innovation', 'ideas.md'), 'utf8');
const lines = content.split('\n');
let issues = 0;

for (const line of lines) {
  if (!line.includes('| approach:')) continue;
  const match = line.match(/\| approach:\s*(.+?)(?:\s*\| shipped:|$)/s);
  if (!match) continue;
  const approachText = match[1];
  const scriptRefs = [...approachText.matchAll(/(?:node|python|bash)\s+([^\s'"]+)/g)];
  for (const ref of scriptRefs) {
    const raw = ref[1];
    const path = raw.replace(/[^\w\/\.-].*$/, '').replace(/\/$/, '');
    if (!path || !path.match(/\.(mjs|js|py|sh)$/)) continue;
    let fullPath;
    if (path.startsWith('/') || path.match(/^[a-zA-Z]:\\/)) {
      fullPath = path;
    } else {
      fullPath = join(__DIR, '..', path);
    }
    if (!existsSync(fullPath)) {
      console.error(`[PREFLIGHT] MISSING: ${path}`);
      issues++;
    }
  }
}

if (issues === 0) {
  console.log('[PREFLIGHT] OK: All referenced scripts exist');
  process.exit(0);
} else {
  console.error(`[PREFLIGHT] FAIL: ${issues} missing script(s)`);
  process.exit(1);
}
