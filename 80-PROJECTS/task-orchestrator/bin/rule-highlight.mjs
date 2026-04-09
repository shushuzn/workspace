#!/usr/bin/env node
/** Highlight matching rule keywords in input text */
import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const PLANNER = join(__DIR, '..', 'src', 'planner.mjs');

console.log('=== Rule Keyword Highlighter ===');

// Extract keywords from planner
let keywords = [];
if (existsSync(PLANNER)) {
  const content = readFileSync(PLANNER, 'utf8');
  const match = content.match(/keywords:\s*\[([^\]]+)\]/);
  if (match) {
    // Parse keyword arrays
    const blocks = match[1].match(/'([^']+)'/g) || [];
    keywords = blocks.map(b => b.slice(1, -1));
  }
}

console.log('Rules loaded:', keywords.length);
console.log('\nUsage:');
console.log('  echo "open wiki page" | node rule-highlight.mjs');
console.log('  node rule-highlight.mjs "录屏并导出"');
console.log('\n[PROTOTYPE] Highlight matching keywords with ANSI colors');
