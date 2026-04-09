#!/usr/bin/env node
/**
 * OMC Insight Action Queue
 * Manages pending actions from insights.
 *
 * Usage:
 *   node omc-insight-action.mjs --add "description" --action "command"
 *   node omc-insight-action.mjs --list   Show pending actions
 *   node omc-insight-action.mjs --pickup  Read for injection
 *   node omc-insight-action.mjs --done <id>  Mark complete + mark insight EXECUTED
 *   node omc-insight-action.mjs --execute <id>  Run action then mark done
 */
import { existsSync, readFileSync, writeFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import { spawn } from 'child_process';

const __dirname = dirname(fileURLToPath(import.meta.url));
const STATE_DIR = resolve(__dirname, '../state');
const PENDING_FILE = resolve(STATE_DIR, 'pending-actions.md');
const VERIFY_FILE = resolve(STATE_DIR, 'insight-verifications.md');
const INSIGHTS_FILE = resolve(__dirname, '../state/session-insights.md');

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

function markInsightExecuted(desc) {
  // Find the insight in session-insights.md matching this action's description and mark EXECUTED
  if (!existsSync(INSIGHTS_FILE)) return;
  let content = readFileSync(INSIGHTS_FILE, 'utf-8');
  const lines = content.split('\n');
  let found = false;
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes('### ') && lines[i].includes(desc.slice(0, 40))) {
      // Check if already marked
      if (lines[i].includes('✅ EXECUTED')) break;
      // Append EXECUTED marker on same line
      lines[i] = lines[i].replace(/\s*$/, '') + ' ✅ EXECUTED';
      found = true;
      break;
    }
  }
  if (found) {
    writeFileSync(INSIGHTS_FILE, lines.join('\n'), 'utf-8');
    log(`marked insight: ${desc.slice(0, 40)}`);
  }
}

function doneAction(id, expected, actual) {
  const items = readPending();
  const item = items.find(i => i.id === id);
  if (!item) { log(`not found: ${id}`); return; }
  markInsightExecuted(item.desc);
  verifyAction(id, 'executed', expected, actual);
  writePending(items.filter(i => i.id !== id));
  log(`completed: ${id}`);
}

function verifyAction(id, result, expected, actual) {
  // Write verification record with expected vs actual
  const existing = existsSync(VERIFY_FILE) ? readFileSync(VERIFY_FILE, 'utf-8') : '';
  const judgment = (!expected && !actual)
    ? '⚠️ 未验证'
    : expected === actual
      ? '✅ 有效'
      : '❌ 无效（人工判定）';
  const entry = `## ${id}

- **Result**: ${result || 'executed'}
- **判定**: ${judgment}
- **预期效果**: ${expected || '未记录'}
- **实际效果**: ${actual || '未记录'}
- **Verified**: ${new Date().toISOString()}

`;
  writeFileSync(VERIFY_FILE, existing + entry, 'utf-8');
  log(`verified: ${id} → ${judgment}`);
}

function listVerified() {
  if (!existsSync(VERIFY_FILE)) { console.log('no verifications yet'); return; }
  console.log(readFileSync(VERIFY_FILE, 'utf-8'));
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
  if (idx) {
    const idArg = args[idx];
    const expIdx = args.indexOf('--expected') + 1;
    const actIdx = args.indexOf('--actual') + 1;
    const expected = expIdx && args[expIdx] ? args[expIdx] : '';
    const actual = actIdx && args[actIdx] ? args[actIdx] : '';
    if (idArg === 'all') {
      const items = readPending();
      for (const item of items) verifyAction(item.id, 'executed');
      writePending([]);
      log('all actions verified and cleared');
    } else {
      doneAction(idArg, expected, actual);
    }
  }
} else if (args.includes('--verify')) {
  const idx = args.indexOf('--verify') + 1;
  const idArg = args[idx];
  const expIdx = args.indexOf('--expected') + 1;
  const actIdx = args.indexOf('--actual') + 1;
  const expected = expIdx && args[expIdx] ? args[expIdx] : '';
  const actual = actIdx && args[actIdx] ? args[actIdx] : '';
  const result = args[idx + 1] && !args[idx + 1].startsWith('--') ? args[idx + 1] : 'executed';
  if (idArg && !idArg.startsWith('--')) {
    verifyAction(idArg, result, expected, actual);
    // If expected and actual match, also mark done (remove from pending)
    if (expected && actual && expected === actual) {
      const items = readPending();
      const item = items.find(i => i.id === idArg);
      if (item) {
        markInsightExecuted(item.desc);
        writePending(items.filter(i => i.id !== idArg));
        console.log(`auto-marked done: ${idArg} (expected === actual)`);
      }
    }
  } else {
    listVerified();
  }
} else if (args.includes('--list-verified')) {
  listVerified();
} else if (args.includes('--execute')) {
  const idx = args.indexOf('--execute') + 1;
  if (idx && args[idx] && !args[idx].startsWith('--')) {
    const idArg = args[idx];
    const items = readPending();
    const item = items.find(i => i.id === idArg);
    if (!item) { log(`not found: ${idArg}`); }
    else {
      log(`executing: ${item.action}`);
      const [cmd, ...args2] = item.action.split(' ');
      const proc = spawn(cmd, args2, { shell: true, cwd: __dirname + '/../../..' });
      let err = '';
      proc.stderr.on('data', d => { err += d.toString(); });
      proc.on('close', (code) => {
        if (code !== 0) log(`action failed (${code}): ${err.slice(0, 200)}`);
        doneAction(idArg);
      });
      proc.on('error', e => { log(`spawn error: ${e.message}`); doneAction(idArg); });
    }
  } else {
    log('Usage: --execute <id>');
  }
}

export { addAction, readPending, pickup, doneAction };
