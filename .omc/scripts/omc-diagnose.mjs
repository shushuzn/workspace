#!/usr/bin/env node
/**
 * OMC Combined Diagnostic
 * Replaces: hook-self-improve --stats + hook-workflow-detector --emit + queue stats
 *
 * Usage:
 *   node omc-diagnose.mjs           Full diagnostic
 *   node omc-diagnose.mjs --stats   Self-improve stats only
 *   node omc-diagnose.mjs --wf      Workflow patterns only
 *   node omc-diagnose.mjs --queue   Queue stats only
 */
import { existsSync, readFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const STATE_DIR = resolve(__dirname, '../state');
const AUDIT_LOG = resolve(STATE_DIR, 'hook-audit.jsonl');
const QUEUE = resolve(STATE_DIR, 'mcp-learn-queue.jsonl');
const WF_LOG = resolve(STATE_DIR, 'workflow-log.jsonl');
const DEDUP = resolve(STATE_DIR, 'hook-last-cmd.json');

// ── Args ─────────────────────────────────────────────────────────────────────
const args = process.argv.slice(2);
const full = args.length === 0 || args.includes('--full');
const doStats = full || args.includes('--stats');
const doWf = full || args.includes('--wf');
const doQueue = full || args.includes('--queue');

// ── Helpers ─────────────────────────────────────────────────────────────────
function log(...a) { console.log('[diag]', ...a); }

function readLines(p) {
  if (!existsSync(p)) return [];
  return readFileSync(p, 'utf-8').split('\n').filter(Boolean);
}

function countEntries() {
  const lines = readLines(AUDIT_LOG);
  const tools = {};
  let errors = 0;
  for (const l of lines) {
    try {
      const e = JSON.parse(l);
      tools[e.tool] = (tools[e.tool] || 0) + 1;
      if (e.error || (e.exitCode !== null && e.exitCode !== 0)) errors++;
    } catch {}
  }
  return { total: lines.length, tools, errors };
}

function getDedupStats() {
  if (!existsSync(DEDUP)) return null;
  try {
    const d = JSON.parse(readFileSync(DEDUP, 'utf-8'));
    return d;
  } catch { return null; }
}

function detectWorkflowPatterns(lines, minCount = 3) {
  // N-gram detection: count consecutive Bash, Read, Edit, etc.
  const seqs = {};
  for (let i = 0; i < lines.length - 2; i++) {
    try {
      const a = JSON.parse(lines[i]);
      const b = JSON.parse(lines[i+1]);
      const c = JSON.parse(lines[i+2]);
      const key = `${a.tool} → ${b.tool} → ${c.tool}`;
      seqs[key] = (seqs[key] || 0) + 1;
    } catch {}
  }
  return Object.entries(seqs)
    .filter(([,c]) => c >= minCount)
    .sort((a,b) => b[1] - a[1])
    .slice(0, 5);
}

// ── Main ─────────────────────────────────────────────────────────────────────
async function main() {
  if (full) {
    console.log('═'.repeat(60));
    console.log(' OMC Combined Diagnostic');
    console.log('═'.repeat(60));
  }

  if (doStats) {
    const { total, tools, errors } = countEntries();
    const dup = getDedupStats();
    const topTools = Object.entries(tools).sort((a,b) => b[1]-a[1]).slice(0,5);

    console.log('\n📊 Audit Stats');
    console.log('─'.repeat(40));
    console.log(`  Total entries: ${total}`);
    console.log(`  Errors: ${errors}`);
    if (dup) console.log(`  Last dedup: "${dup.cmd}" x${dup.count}`);
    console.log('  Top tools:');
    topTools.forEach(([t,c]) => console.log(`    ${t}: ${c}`));
  }

  if (doQueue) {
    const q = readLines(QUEUE);
    const patterns = q.filter(l => l.includes('agentdb_pattern-store'));
    console.log('\n📬 Queue');
    console.log('─'.repeat(40));
    console.log(`  Total: ${q.length}`);
    console.log(`  Patterns: ${patterns.length}`);
  }

  if (doWf) {
    const lines = readLines(AUDIT_LOG);
    const patterns = detectWorkflowPatterns(lines);
    console.log('\n🔗 Workflow Patterns');
    console.log('─'.repeat(40));
    if (patterns.length === 0) {
      console.log('  (none ≥3 occurrences)');
    } else {
      patterns.forEach(([pat, count]) => {
        console.log(`  ${pat}: ${count}×`);
      });
    }
  }

  if (full) console.log('\n' + '═'.repeat(60));
}

main().catch(e => console.error('[diag] error:', e.message));
