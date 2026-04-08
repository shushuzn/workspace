#!/usr/bin/env node
/**
 * OMC Insight Action Queue
 * Manages pending actions from insights.
 *
 * Usage:
 *   node omc-insight-action.mjs --add "description" --action "node script.js"
 *   node omc-insight-action.mjs --list   Show pending actions
 *   node omc-insight-action.mjs --pickup  Read for injection
 *   node omc-insight-action.mjs --done <id>  Mark complete
 */
import { existsSync, readFileSync, writeFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PENDING_FILE = resolve(__dirname, '../state/pending-actions.md');

function log(...a) { console.log('[insight]', ...a); }

function readPending() {
  if (!existsSync(PENDING_FILE)) return [];
  return readFileSync(PENDING_FILE, 'utf-8')
    .split('\n')
    .filter(l => l.startsWith('- [ ]'))
    .map(l => {
      const match = l.match(/^\- \[ \] (.*?) \| action: (.+?) \| id: (\S+)/);
      if (!match) return null;
      return { desc: match[1], action: match[2], id: match[3] };
    })
    .filter(Boolean);
}

function writePending(items) {
  const md = items.map(i => `- [ ] ${i.desc} | action: ${i.action} | id: ${i.id}`).join('\n');
  writeFileSync(PENDING_FILE, md || '', 'utf-8');
}

function addAction(desc, action) {
  const id = `action-${Date.now()}`;
  const items = readPending();
  items.push({ desc, action, id });
  writePending(items);
  log(`added: ${id} - ${desc}`);
}

function listActions() {
  const items = readPending();
  if (items.length === 0) {
    log('no pending actions');
    return;
  }
  items.forEach(i => console.log(`  ${i.id}: ${i.desc}`));
}

function pickup() {
  const items = readPending();
  if (items.length === 0) return '';
  return items.map(i => `## Action Item\n\n- **${i.desc}**\n- Run: \`${i.action}\`\n- ID: ${i.id}`).join('\n\n');
}

function doneAction(id) {
  const items = readPending().filter(i => i.id !== id);
  writePending(items);
  log(`completed: ${id}`);
}

// ── CLI ─────────────────────────────────────────────────────────────────────
const args = process.argv.slice(2);
if (args.includes('--add')) {
  const descIdx = args.indexOf('--add') + 1;
  const actionIdx = args.indexOf('--action') + 1;
  if (descIdx && actionIdx) {
    addAction(args[descIdx], args[actionIdx]);
  } else {
    log('Usage: --add "description" --action "command"');
  }
} else if (args.includes('--list')) {
  listActions();
} else if (args.includes('--pickup')) {
  const out = pickup();
  if (out) console.log(out);
} else if (args.includes('--done')) {
  const idx = args.indexOf('--done') + 1;
  if (idx) doneAction(args[idx]);
}

export { addAction, readPending, pickup, doneAction };
