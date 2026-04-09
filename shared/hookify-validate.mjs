#!/usr/bin/env node
/** Validate hookify rule regex patterns */
import { readdirSync, readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const CLAUDE_DIR = join(__DIR, '..', '.claude');

let files = [];
try {
  for (const f of readdirSync(CLAUDE_DIR)) {
    if (f.startsWith('hookify.') && f.endsWith('.local.md')) files.push(f);
  }
} catch {}

let bad = 0;
for (const fn of files) {
  const c = readFileSync(join(CLAUDE_DIR, fn), 'utf8');
  const m = c.match(/pattern:\s*(.+)/);
  if (m) {
    try { new RegExp(m[1]); }
    catch { console.log('BAD regex in', fn, ':', m[1].slice(0, 50)); bad++; }
  }
}
console.log('Valid:', files.length - bad, '/', files.length, 'hookify rules');
if (bad > 0) process.exit(1);
