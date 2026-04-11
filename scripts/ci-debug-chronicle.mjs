#!/usr/bin/env node
/**
 * scripts/ci-debug-chronicle.mjs
 * Records and queries CI debug sessions for knowledge accumulation.
 *
 * Usage:
 *   node scripts/ci-debug-chronicle.mjs append <run_id> [key=value ...]
 *   node scripts/ci-debug-chronicle.mjs query [--pattern=<name>] [--since=<days>]
 *   node scripts/ci-debug-chronicle.mjs report
 *
 * Log file: ci-debug-chronicle.jsonl (one JSON per line)
 */
import { readFileSync, appendFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const CHRONICLE_FILE = join(__dirname, '..', 'ci-debug-chronicle.jsonl');

const MODE = process.argv[2] || 'report';
const args = process.argv.slice(3);

// ── Load chronicle ──────────────────────────────────────────────────────────────
function loadChronicle() {
  if (!existsSync(CHRONICLE_FILE)) return [];
  const content = readFileSync(CHRONICLE_FILE, 'utf8');
  return content.trim().split('\n').filter(Boolean).map(l => {
    try { return JSON.parse(l); } catch { return null; }
  }).filter(Boolean);
}

// ── Append entry ──────────────────────────────────────────────────────────────
function appendEntry(fields) {
  const entry = {
    date: new Date().toISOString().split('T')[0],
    timestamp: new Date().toISOString(),
    ...fields
  };
  appendFileSync(CHRONICLE_FILE, JSON.stringify(entry) + '\n');
  console.log(`Appended to ${CHRONICLE_FILE}`);
  console.log(JSON.stringify(entry, null, 2));
}

// ── Parse key=value args ──────────────────────────────────────────────────────
function parseArgs(args) {
  const result = {};
  for (const arg of args) {
    const [k, ...vParts] = arg.split('=');
    if (k) result[k] = vParts.join('=');
  }
  return result;
}

// ── Query entries ─────────────────────────────────────────────────────────────
function queryEntries(pattern, sinceDays) {
  const chronicle = loadChronicle();
  let filtered = chronicle;

  if (pattern) {
    filtered = filtered.filter(e => e.pattern === pattern || e.name === pattern);
  }

  if (sinceDays) {
    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - parseInt(sinceDays, 10));
    filtered = filtered.filter(e => new Date(e.date) >= cutoff);
  }

  return filtered;
}

// ── Generate report ───────────────────────────────────────────────────────────
function generateReport() {
  const chronicle = loadChronicle();
  if (chronicle.length === 0) {
    console.log('No chronicle entries yet.');
    return;
  }

  console.log(`\n=== CI Debug Chronicle ===`);
  console.log(`Total entries: ${chronicle.length}\n`);

  // Pattern frequency
  const patternCounts = {};
  const resolvedCounts = {};
  for (const e of chronicle) {
    const key = e.pattern || e.matched_pattern || 'unknown';
    patternCounts[key] = (patternCounts[key] || 0) + 1;
    if (e.resolved) resolvedCounts[key] = (resolvedCounts[key] || 0) + 1;
  }

  console.log('Top patterns:');
  const sorted = Object.entries(patternCounts).sort((a, b) => b[1] - a[1]);
  for (const [name, count] of sorted.slice(0, 10)) {
    const resolved = resolvedCounts[name] || 0;
    const rate = ((resolved / count) * 100).toFixed(0);
    console.log(`  ${name}: ${count} occurrences, ${resolved} resolved (${rate}%)`);
  }

  // Recent unresolved
  const unresolved = chronicle.filter(e => !e.resolved);
  if (unresolved.length > 0) {
    console.log(`\nRecent unresolved (${unresolved.length}):`);
    for (const e of unresolved.slice(-5).reverse()) {
      console.log(`  ${e.date} | ${e.run_id} | ${e.pattern || e.matched_pattern || 'unknown'}`);
    }
  }

  // MTTR estimation
  const withResolution = chronicle.filter(e => e.resolved && e.resolved_at);
  if (withResolution.length > 0) {
    const totalMinutes = withResolution.reduce((sum, e) => {
      const start = new Date(e.timestamp);
      const end = new Date(e.resolved_at);
      return sum + (end - start) / 60000;
    }, 0);
    const avgMTTR = totalMinutes / withResolution.length;
    console.log(`\nEstimated MTTR: ${avgMTTR.toFixed(0)} minutes (based on ${withResolution.length} resolved cases)`);
  }

  console.log();
}

// ── Main ──────────────────────────────────────────────────────────────────────
async function main() {
  if (MODE === 'append') {
    const fields = parseArgs(args);
    if (!fields.run_id) {
      console.error('Usage: append <run_id> [key=value ...]');
      process.exit(1);
    }
    appendEntry(fields);
    return;
  }

  if (MODE === 'query') {
    const pattern = args.find(a => a.startsWith('--pattern='))?.split('=')[1];
    const since = args.find(a => a.startsWith('--since='))?.split('=')[1];
    const entries = queryEntries(pattern, since);
    console.log(`Found ${entries.length} entries:`);
    for (const e of entries.slice(-20)) {
      console.log(`  ${e.date} | ${e.run_id} | ${e.pattern || e.matched_pattern || 'unknown'} | resolved:${e.resolved}`);
    }
    return;
  }

  // Default: report
  generateReport();
}

main().catch(e => { console.error(e); process.exit(1); });
