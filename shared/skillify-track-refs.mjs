#!/usr/bin/env node
/**
 * skillify-track-refs.mjs — track skill references for Gate16 compliance
 * Records when a skill is referenced by other seeds
 * Usage: node shared/skillify-track-refs.mjs --init
 */
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const TRACK_FILE = join(__DIR, '..', '.omc', 'state', 'skillify-refs.json');

function load() {
  if (!existsSync(TRACK_FILE)) return {};
  try { return JSON.parse(readFileSync(TRACK_FILE, 'utf8')); } catch { return {}; }
}

function save(data) {
  writeFileSync(TRACK_FILE, JSON.stringify(data, null, 2), 'utf8');
}

function main() {
  const mode = process.argv.includes('--init') ? 'init' : process.argv.includes('--bump') ? 'bump' : 'show';
  const refs = load();

  if (mode === 'init') {
    save({});
    console.log('[SKILLIFY-REFS] Initialized tracking file');
    return;
  }

  if (mode === 'bump') {
    const name = process.argv[process.argv.indexOf('--bump') + 1];
    if (!name) { console.error('Usage: --bump <skill-name>'); process.exit(1); }
    refs[name] = (refs[name] || 0) + 1;
    save(refs);
    console.log(`[SKILLIFY-REFS] ${name}: ${refs[name]} refs`);
    return;
  }

  console.log('=== Skillify Refs ===');
  const entries = Object.entries(refs).sort((a, b) => b[1] - a[1]);
  for (const [name, count] of entries) {
    const status = count >= 2 ? '✓ Gate16 ready' : `(${count}/2)`;
    console.log(`  ${name}: ${count} ${status}`);
  }
  if (entries.length === 0) console.log('  (no refs tracked)');
}

main();
