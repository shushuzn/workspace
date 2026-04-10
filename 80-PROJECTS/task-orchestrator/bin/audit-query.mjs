#!/usr/bin/env node
/**
 * audit-query.mjs — query executor audit logs
 * Usage: node audit-query.mjs --recent N | --run RUNID | --failed | --stats
 */
import { readFileSync, existsSync } from 'fs';
import { join } from 'path';
import { homedir } from 'os';

const AUDIT_FILE = join(homedir(), '.unified-agent-cli', 'audit.jsonl');

function loadLines() {
  if (!existsSync(AUDIT_FILE)) return [];
  return readFileSync(AUDIT_FILE, 'utf8').trim().split('\n').filter(Boolean);
}

function parseEntry(line) {
  try { return JSON.parse(line); } catch { return null; }
}

if (process.argv.includes('--help') || process.argv.includes('-h')) {
  console.log('Usage: node audit-query.mjs [--recent N] [--run RUNID] [--failed] [--stats]');
  console.log('  --recent N  Show last N entries');
  console.log('  --run ID   Show entries for specific runId');
  console.log('  --failed    Show only failed entries');
  console.log('  --stats     Show summary statistics');
  process.exit(0);
}

const cmd = process.argv.includes('--recent') ? 'recent'
  : process.argv.includes('--run') ? 'run'
  : process.argv.includes('--failed') ? 'failed'
  : process.argv.includes('--stats') ? 'stats'
  : 'recent';

const entries = loadLines().map(parseEntry).filter(Boolean);

if (entries.length === 0) {
  console.log('[audit] No audit entries found at ~/.unified-agent-cli/audit.jsonl');
  process.exit(0);
}

if (cmd === 'recent') {
  const n = parseInt(process.argv[process.argv.indexOf('--recent') + 1]) || 5;
  const recent = entries.slice(-n).reverse();
  console.log(`=== Last ${recent.length} audit entries ===`);
  for (const e of recent) {
    const dt = new Date(e.timestamp).toISOString().slice(0, 19).replace('T', ' ');
    const status = e.success ? '✓' : '✗';
    const fatal = e.fatal ? ' [FATAL]' : '';
    const cached = e.cached ? ' [CACHED]' : '';
    const duration = e.durationMs ? ` ${(e.durationMs/1000).toFixed(1)}s` : '';
    console.log(`${status} ${dt} runId=${e.runId?.slice(0,8)} seq=${e.seq} ${e.adapterId}:${e.command}${duration}${fatal}${cached}`);
    if (!e.success && e.error) console.log(`  ERROR: ${e.error.slice(0, 120)}`);
    if (e.causalityDepth > 0) console.log(`  chain depth=${e.causalityDepth} parent=${e.parentStepIdx}`);
  }
} else if (cmd === 'run') {
  const runId = process.argv[process.argv.indexOf('--run') + 1];
  const runEntries = entries.filter(e => e.runId === runId);
  if (runEntries.length === 0) {
    console.log(`[audit] No entries for runId=${runId}`);
  } else {
    console.log(`=== Run ${runId} (${runEntries.length} steps) ===`);
    for (const e of runEntries) {
      const status = e.success ? '✓' : '✗';
      const fatal = e.fatal ? ' [FATAL]' : '';
      console.log(`  seq=${e.seq} ${status} ${e.adapterId}:${e.command} ${e.durationMs ? (e.durationMs/1000).toFixed(1)+'s' : ''}${fatal}`);
      if (!e.success && e.error) console.log(`    ERROR: ${e.error.slice(0, 120)}`);
    }
  }
} else if (cmd === 'failed') {
  const failed = entries.filter(e => !e.success);
  console.log(`=== ${failed.length} failed steps ===`);
  for (const e of failed.slice(-20).reverse()) {
    const dt = new Date(e.timestamp).toISOString().slice(0, 19).replace('T', ' ');
    console.log(`✗ ${dt} ${e.runId?.slice(0,8)} ${e.adapterId}:${e.command}`);
    console.log(`  code=${e.code} error=${e.error?.slice(0, 80)}`);
  }
  process.exit(0);
} else if (cmd === 'stats') {
  const byAdapter = {};
  const byCode = {};
  let total = entries.length;
  let failed = 0;
  for (const e of entries) {
    byAdapter[e.adapterId] = byAdapter[e.adapterId] || { total: 0, success: 0, fail: 0 };
    byAdapter[e.adapterId].total++;
    if (e.success) byAdapter[e.adapterId].success++;
    else { byAdapter[e.adapterId].fail++; failed++; }
    if (e.code) {
      byCode[e.code] = byCode[e.code] || 0;
      byCode[e.code]++;
    }
  }
  console.log(`=== Audit Stats (${total} steps, ${failed} failed) ===`);
  console.log('\nBy adapter:');
  for (const [a, s] of Object.entries(byAdapter)) {
    const rate = ((s.success / s.total) * 100).toFixed(0);
    console.log(`  ${a}: ${s.success}/${s.total} (${rate}%)`);
  }
  if (Object.keys(byCode).length > 0) {
    console.log('\nError codes:');
    for (const [code, cnt] of Object.entries(byCode)) {
      console.log(`  ${code}: ${cnt}`);
    }
  }
}
