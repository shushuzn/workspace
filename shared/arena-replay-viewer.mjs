#!/usr/bin/env node
/**
 * arena-replay-viewer.mjs
 * View agent-arena battle replays
 */
import { readdirSync, readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const REPLAYS_DIR = join(__DIR, '..', '80-PROJECTS', 'agent-arena', 'replays');

const args = process.argv.slice(2);

if (args.includes('--list') || args.length === 0) {
  let files = [];
  try {
    files = readdirSync(REPLAYS_DIR).filter(f => f.endsWith('.json')).sort().reverse();
  } catch {
    console.log('No replays directory yet. Run battles to create replays.');
    process.exit(0);
  }

  if (files.length === 0) {
    console.log('No replays found. Run battles to create replays.');
    process.exit(0);
  }

  console.log('Available replays:');
  for (const f of files.slice(0, 20)) {
    const ts = f.replace('.json', '');
    console.log(`  ${ts}  ${f}`);
  }
  if (files.length > 20) console.log(`  ... and ${files.length - 20} more`);
  process.exit(0);
}

if (args.includes('--view')) {
  const replayFile = args[args.indexOf('--view') + 1];
  if (!replayFile) {
    console.log('Usage: arena-replay-viewer.mjs --view <replay-file>');
    process.exit(1);
  }
  const path = join(REPLAYS_DIR, replayFile);
  try {
    const data = JSON.parse(readFileSync(path, 'utf-8'));
    console.log(JSON.stringify(data, null, 2));
  } catch {
    console.error(`Failed to read replay: ${path}`);
    process.exit(1);
  }
}
