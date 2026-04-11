#!/usr/bin/env node
/**
 * scripts/ci-fix-log.mjs
 * Decision audit trail for CI fix confidence changes.
 * Shows why confidence changed, when, and by how much.
 *
 * Usage:
 *   node scripts/ci-fix-log.mjs              # show all pattern histories
 *   node scripts/ci-fix-log.mjs <name>       # show history for one pattern
 *   node scripts/ci-fix-log.mjs --summary    # show confidence scorecard
 */
import { existsSync, readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PATTERN_FILE = join(__dirname, 'ci-failure-patterns.jsonl');
const STATE_FILE = join(__dirname, '..', 'ci-state.json');

function loadPatterns() {
  if (!existsSync(PATTERN_FILE)) return [];
  try {
    const content = readFileSync(PATTERN_FILE, 'utf8');
    return content.trim().split('\n').filter(Boolean).map(l => {
      try { return JSON.parse(l); } catch { return null; }
    }).filter(Boolean);
  } catch { return []; }
}

function loadState() {
  if (!existsSync(STATE_FILE)) return {};
  try { return JSON.parse(readFileSync(STATE_FILE, 'utf8')); } catch { return {}; }
}

function getConfidence(p) {
  if (p.confirmations == null || p.rejections == null) return null;
  if (p.confirmations + p.rejections === 0) return null;
  return p.confirmations / (p.confirmations + p.rejections);
}

function loadFixHistory(name) {
  const state = loadState();
  const fh = state.patterns?.fixHistory?.[name] || [];
  return fh;
}

function updatePatternConfidence(name, confirmed, reason = null) {
  const patterns = loadPatterns();
  const idx = patterns.findIndex(p => p.name === name);
  if (idx === -1) { console.error(`Pattern not found: ${name}`); process.exit(1); }
  if (patterns[idx].confirmations == null) patterns[idx].confirmations = 0;
  if (patterns[idx].rejections == null) patterns[idx].rejections = 0;
  if (confirmed) patterns[idx].confirmations++;
  else patterns[idx].rejections++;
  const lines = patterns.map(p => JSON.stringify(p)).join('\n') + '\n';
  require('fs').writeFileSync(PATTERN_FILE, lines);

  // Record in state history
  const state = loadState();
  if (!state.patterns) state.patterns = {};
  if (!state.patterns.fixHistory) state.patterns.fixHistory = {};
  if (!state.patterns.lastFixAttempt) state.patterns.lastFixAttempt = {};
  const entry = {
    pattern: name,
    timestamp: new Date().toISOString(),
    result: confirmed ? 'confirmed' : 'rejected',
    source: 'manual',
    reason: reason,
    smokeTest: confirmed
  };
  if (!state.patterns.fixHistory[name]) state.patterns.fixHistory[name] = [];
  state.patterns.fixHistory[name].push(entry);
  state.patterns.lastFixAttempt[name] = entry;
  state.lastUpdated = new Date().toISOString();
  require('fs').writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));

  const conf = patterns[idx].confirmations / (patterns[idx].confirmations + patterns[idx].rejections);
  const confStr = (conf * 100).toFixed(0);
  const icon = confirmed ? '✅' : '❌';
  console.log(`${icon} ${name}: ${confirmed ? 'confirmed' : 'rejected'}`);
  console.log(`   Confidence: ${confStr}% (${patterns[idx].confirmations} confirm, ${patterns[idx].rejections} reject)`);
  if (reason) console.log(`   Reason: ${reason}`);
}

function showHistory(name) {
  const patterns = loadPatterns();
  const pattern = patterns.find(p => p.name === name);
  const fh = loadFixHistory(name);

  if (!pattern) {
    console.log(`Pattern not found: ${name}`);
    return;
  }

  const conf = getConfidence(pattern);
  const events = fh.slice().reverse(); // newest first

  console.log(`\n=== Fix Decision Audit: ${name} ===\n`);
  console.log(`Current confidence: ${conf !== null ? `${(conf * 100).toFixed(0)}%` : 'N/A'} (${pattern.confirmations || 0} confirms, ${pattern.rejections || 0} rejects)`);
  console.log(`Severity: ${pattern.severity} | Fix: ${pattern.fix}\n`);

  if (events.length === 0) {
    console.log('No fix events recorded yet.');
    console.log();
    return;
  }

  console.log('Timeline:');
  for (const ev of events) {
    const date = new Date(ev.timestamp).toLocaleDateString();
    const time = new Date(ev.timestamp).toLocaleTimeString();
    const icon = ev.result === 'confirmed' ? '✅' : ev.result === 'rejected' ? '❌' : ev.result === 'applied' ? '📋' : '?';
    const smoke = ev.smokeTest === true ? 'smoke:PASS' : ev.smokeTest === false ? 'smoke:FAIL' : ev.smokeTest === null ? 'smoke:skip' : '';
    console.log(`  ${icon}  ${date} ${time}  |  ${ev.result}  |  ${smoke}`);
  }
  console.log();
}

function showSummary() {
  const patterns = loadPatterns();
  const state = loadState();

  console.log('\n=== Fix Confidence Scorecard ===\n');
  console.log('Pattern'.padEnd(40) + 'Conf   | Confirms | Rejects | Trend');
  console.log('─'.repeat(75));

  for (const p of patterns) {
    const conf = getConfidence(p);
    const confStr = conf !== null ? `${(conf * 100).toFixed(0).padStart(3)}%` : ' N/A ';
    const c = p.confirmations || 0;
    const r = p.rejections || 0;
    const fh = state.patterns?.fixHistory?.[p.name] || [];
    const lastEv = fh[fh.length - 1];
    const trend = lastEv ? (lastEv.result === 'confirmed' ? '↑' : lastEv.result === 'rejected' ? '↓' : '→') : ' ';

    const lastDate = lastEv ? new Date(lastEv.timestamp).toLocaleDateString().substring(5) : '';
    const name40 = p.name.length > 38 ? p.name.substring(0, 37) + '…' : p.name;
    console.log(`${name40.padEnd(40)} ${confStr}  |  ${String(c).padStart(3)}  |  ${String(r).padStart(3)}  | ${trend} ${lastDate}`);
  }
  console.log();
}

async function main() {
  const [, , cmd, ...args] = process.argv;

  if (cmd === '--summary' || cmd === 'summary') {
    showSummary();
    return;
  }

  if (cmd === 'confirm' || cmd === 'reject') {
    const name = args.filter(a => !a.startsWith('--')).join(' ');
    const reason = args.find(a => a.startsWith('--reason='))?.slice(9) || null;
    const action = cmd; // 'confirm' or 'reject'
    updatePatternConfidence(name, action === 'confirm', reason);
    return;
  }

  if (cmd) {
    showHistory(args.join(' '));
    return;
  }

  // Default: show all histories
  const patterns = loadPatterns();
  showSummary();

  const state = loadState();
  const fhKeys = Object.keys(state.patterns?.fixHistory || {});

  if (fhKeys.length > 0) {
    console.log('Recent events (last 10):');
    const allEvents = [];
    for (const [name, events] of Object.entries(state.patterns?.fixHistory || {})) {
      for (const ev of events) {
        allEvents.push({ name, ...ev });
      }
    }
    allEvents.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    for (const ev of allEvents.slice(0, 10)) {
      const icon = ev.result === 'confirmed' ? '✅' : ev.result === 'rejected' ? '❌' : ev.result === 'applied' ? '📋' : '?';
      const smoke = ev.smokeTest === true ? 'smoke:PASS' : ev.smokeTest === false ? 'smoke:FAIL' : '';
      const dt = new Date(ev.timestamp);
      console.log(`  ${icon} ${dt.toLocaleDateString()} ${dt.toLocaleTimeString()}  ${ev.name}  ${smoke}`);
    }
    console.log();
    console.log('Run: node scripts/ci-fix-log.mjs "<name>"  # detail for one pattern');
  }
}

main().catch(e => { console.error(e); process.exit(1); });
