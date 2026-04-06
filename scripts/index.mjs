/**
 * index.mjs
 * Lists all scripts in scripts/ with their descriptions.
 * Run: node scripts/index.mjs [--search <term>] [--sort name|date]
 */

import { readdirSync, readFileSync, statSync } from 'fs';
import { join, resolve } from 'path';

const SCRIPTS_DIR = resolve('D:/OpenClaw/workspace/scripts');

// Parse CLI args
const args = process.argv.slice(2);
let searchTerm = '';
let sortBy = 'name';
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--search' && args[i + 1]) searchTerm = args[++i].toLowerCase();
  else if (args[i] === '--sort' && args[i + 1]) sortBy = args[++i];
}

const files = readdirSync(SCRIPTS_DIR).filter(f => (f.endsWith('.mjs') || f.endsWith('.js')));

console.log(`\n${'Script'.padEnd(28)} ${'Description'}`);
console.log('-'.repeat(70));

// Filter by search term
const filtered = files.filter(f => f.toLowerCase().includes(searchTerm));

// Sort
const sorted = filtered.sort((a, b) => {
  if (sortBy === 'date') {
    return statSync(join(SCRIPTS_DIR, b)).mtimeMs - statSync(join(SCRIPTS_DIR, a)).mtimeMs;
  }
  return a.localeCompare(b);
});

for (const file of sorted) {
  const path = join(SCRIPTS_DIR, file);
  const content = readFileSync(path, 'utf8').slice(0, 400);
  const lines = content.split('\n');
  // Description: the first non-filename comment line that contains meaningful text
  // Skip line 0 (/**) and line 1 (filename line with possible em-dash description)
  // Look for the first line that has description text (not the filename, not "Run:")
  let desc = '(no description)';
  // Extract from filename line which may contain "filename — description"
  const filenameLine = lines[1] || '';
  const emIdx = filenameLine.indexOf('\u2014'); // em-dash
  if (emIdx > 0) {
    desc = filenameLine.slice(emIdx + 1).trim();
  } else {
    // Fallback: first non-filename, non-Run comment line
    for (let i = 2; i < lines.length; i++) {
      const t = lines[i].replace(/^ \*( \*)?/, '').trim();
      if (t.length > 3 && !t.startsWith('Run:') && !t.match(/^(import|export|const|let|var|function|class|interface|type)\b/)) {
        desc = t;
        break;
      }
    }
  }
  console.log(`${file.padEnd(28)} ${desc}`);
}

console.log(`\n${filtered.length} of ${files.length} script(s)\n`);
