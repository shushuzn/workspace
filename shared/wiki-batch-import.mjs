#!/usr/bin/env node
/**
 * wiki-batch-import.mjs
 * Batch import arXiv papers from a list of IDs
 * Usage: node shared/wiki-batch-import.mjs <id-list-file>
 *   id-list-file: one arXiv ID or URL per line
 */
import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';

const __DIR = dirname(fileURLToPath(import.meta.url));
const WIKI_DIR = join(__DIR, '..', 'knowledge', 'wikipedia');

const inputFile = process.argv[2];
if (!inputFile) {
  console.error('Usage: node wiki-batch-import.mjs <id-list-file>');
  process.exit(1);
}
if (!existsSync(inputFile)) {
  console.error('File not found:', inputFile);
  process.exit(1);
}

const lines = readFileSync(inputFile, 'utf8').split('\n').filter(Boolean);
console.log(`[wiki-batch] Importing ${lines.length} papers...`);

let ok = 0, fail = 0;
for (const line of lines) {
  const trimmed = line.trim();
  if (!trimmed || trimmed.startsWith('#')) continue;

  // Extract ID from URL or bare ID
  const idMatch = trimmed.match(/(\d+\.\d+)/);
  if (!idMatch) {
    console.log(`  [SKIP] Cannot parse ID from: ${trimmed}`);
    fail++;
    continue;
  }
  const id = idMatch[1];
  const url = trimmed.includes('arxiv.org') ? trimmed : `https://arxiv.org/abs/${id}`;

  console.log(`  [ingest] ${id}...`);
  try {
    execSync(`node wiki.mjs ingest "${url}"`, { cwd: WIKI_DIR, stdio: 'pipe', timeout: 60000 });
    ok++;
  } catch (e) {
    console.log(`  [FAIL] ${id}: ${e.status || 'error'}`);
    fail++;
  }
}

console.log(`\n[wiki-batch] Done: ${ok} imported, ${fail} failed`);
process.exit(fail > 0 ? 1 : 0);
