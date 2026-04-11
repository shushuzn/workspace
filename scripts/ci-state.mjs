#!/usr/bin/env node
/**
 * scripts/ci-state.mjs
 * Centralized CI state store — single source of truth for all CI tools.
 *
 * Usage:
 *   node scripts/ci-state.mjs init               # initialize empty state
 *   node scripts/ci-state.mjs set <key> <value> # set a value
 *   node scripts/ci-state.mjs get <key>           # get a value
 *   node scripts/ci-state.mjs merge <json>      # merge partial update
 *   node scripts/ci-state.mjs dump               # show full state
 *
 * All CI tools should read from this instead of multiple jsonl files.
 */
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const STATE_FILE = join(__dirname, '..', 'ci-state.json');

const MODE = process.argv[2];
const args = process.argv.slice(3);

function loadState() {
  if (!existsSync(STATE_FILE)) return {};
  try {
    return JSON.parse(readFileSync(STATE_FILE, 'utf8'));
  } catch { return {}; }
}

function saveState(state) {
  writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
}

async function main() {
  const state = loadState();

  if (MODE === 'init') {
    const initial = {
      version: 1,
      lastUpdated: new Date().toISOString(),
      lastRun: null,
      coverage: null,
      health: null,
      patterns: { matched: [], newOccurrences: {} },
      chronicle: { entries: 0 }
    };
    saveState(initial);
    console.log('Initialized ci-state.json');
    return;
  }

  if (MODE === 'get') {
    const key = args[0];
    if (!key) { console.log(JSON.stringify(state, null, 2)); return; }
    const val = key.split('.').reduce((s, k) => s && s[k], state);
    console.log(val !== undefined ? JSON.stringify(val) : '');
    return;
  }

  if (MODE === 'set') {
    const [keyPath, ...valueParts] = args;
    const value = valueParts.join(' ');
    if (!keyPath) { console.error('Usage: set <key> <value>'); process.exit(1); }

    const keys = keyPath.split('.');
    let obj = state;
    for (let i = 0; i < keys.length - 1; i++) {
      if (!(keys[i] in obj)) obj[keys[i]] = {};
      obj = obj[keys[i]];
    }

    try { obj[keys[keys.length - 1]] = JSON.parse(value); }
    catch { obj[keys[keys.length - 1]] = value; }

    state.lastUpdated = new Date().toISOString();
    saveState(state);
    console.log(`Set ${keyPath} = ${obj[keys[keys.length - 1]]}`);
    return;
  }

  if (MODE === 'merge') {
    const patch = args[0] ? JSON.parse(args.join(' ')) : {};
    const merged = { ...state, ...patch, lastUpdated: new Date().toISOString() };
    saveState(merged);
    console.log('Merged state');
    return;
  }

  if (MODE === 'dump') {
    console.log(JSON.stringify(state, null, 2));
    return;
  }

  // Default: show state
  console.log('\n=== CI State ===\n');
  console.log(`Last updated: ${state.lastUpdated || 'never'}`);
  console.log(`Last run: ${state.lastRun ? JSON.stringify(state.lastRun, null, 2) : 'none'}`);
  console.log(`Coverage: ${state.coverage ? JSON.stringify(state.coverage) : 'none'}`);
  console.log(`Health: ${state.health ? JSON.stringify(state.health) : 'none'}`);
  console.log();
}

main().catch(e => { console.error(e); process.exit(1); });
