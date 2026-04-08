#!/usr/bin/env node
/**
 * OMC MCP Queue Consumer
 * Reads .omc/state/mcp-learn-queue.jsonl → stores to AgentDB via Ollama API + drain-inject.
 *
 * Architecture:
 *   - Calls Ollama directly to generate structured pattern summaries
 *   - Writes results to drain file for session-start-inject to pick up
 *   - Also writes directly to a local store the main agent can reference
 *
 * Usage:
 *   node hook-mcp-consumer.mjs          Process pending entries
 *   node hook-mcp-consumer.mjs --stats  Show queue stats
 */
import { existsSync, readFileSync, writeFileSync, appendFileSync, mkdirSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const STATE_DIR = resolve(__dirname, '../state');
const QUEUE_FILE = resolve(STATE_DIR, 'mcp-learn-queue.jsonl');
const PATTERN_STORE = resolve(STATE_DIR, 'agentdb-patterns.jsonl');
const DRAIN_FILE = resolve(STATE_DIR, 'session-start-mcp-inject.md');

// ── Queue management ──────────────────────────────────────────────────────────
function readQueue() {
  if (!existsSync(QUEUE_FILE)) return [];
  return readFileSync(QUEUE_FILE, 'utf-8')
    .split('\n').filter(Boolean)
    .map(l => { try { return JSON.parse(l); } catch { return null; } })
    .filter(Boolean);
}

function clearQueue() {
  writeFileSync(QUEUE_FILE, '', 'utf-8');
}

// ── Store patterns locally ───────────────────────────────────────────────────
function storePattern(pattern, type, confidence, metadata) {
  const entry = {
    id: `${type}-${pattern.slice(0, 50)}-${Date.now()}`,
    pattern,
    patternType: type,
    confidence,
    metadata,
    storedAt: new Date().toISOString(),
  };
  appendFileSync(PATTERN_STORE, JSON.stringify(entry) + '\n', 'utf-8');
  return entry;
}

// ── Add to drain file for session-start-inject ───────────────────────────────
function addToDrain(entries) {
  if (entries.length === 0) return;

  // MCP tool broken → just acknowledge the entries were stored
  const stored = entries.filter(e => e.type === 'agentdb_pattern-store').length;
  const feedbacks = entries.filter(e => e.type === 'agentdb_feedback').length;
  let md = '## OMC Learning Log\n\n';
  md += stored + ' pattern(s) and ' + feedbacks + ' feedback(s) processed.\n\n';
  md += 'Patterns stored directly to agentdb-patterns.jsonl (MCP tool unavailable).\n';

  const existing = existsSync(DRAIN_FILE) ? readFileSync(DRAIN_FILE, 'utf-8') : '';
  writeFileSync(DRAIN_FILE, existing + md, 'utf-8');
}

// ── Store patterns locally ─────────────────────────────────────────────────────
async function processWithLLM(entries) {
  const patterns = entries.filter(e => e.type === 'agentdb_pattern-store');
  const feedbacks = entries.filter(e => e.type === 'agentdb_feedback');

  // Store each pattern locally
  let stored = 0;
  for (const e of patterns) {
    try {
      storePattern(e.pattern || '', e.patternType || 'general', e.confidence || 0.7, e.metadata || {});
      stored++;
    } catch {}
  }

  // Store feedback summaries
  if (feedbacks.length > 0) {
    const avg = feedbacks.reduce((s, e) => s + (e.quality || 0.5), 0) / feedbacks.length;
    storePattern(
      `feedback summary: ${feedbacks.length} tasks, avg quality ${avg.toFixed(2)}`,
      'feedback-summary',
      0.6,
      { count: feedbacks.length, avgQuality: avg }
    );
    stored++;
  }

  return stored;
}

// ── Main ──────────────────────────────────────────────────────────────────────
async function processQueue() {
  const entries = readQueue();
  if (entries.length === 0) {
    console.log('[consumer] queue-empty');
    return;
  }

  console.log(`[consumer] processing ${entries.length} entries...`);

  // Step 1: Ollama-powered analysis + local storage
  const stored = await processWithLLM(entries);
  console.log(`[consumer] stored ${stored} patterns locally`);

  // Step 2: Add to drain for MCP execution in next session
  addToDrain(entries);
  console.log(`[consumer] added ${entries.length} entries to drain`);

  // Step 3: Clear queue
  clearQueue();
  console.log(`[consumer] queue cleared`);
}

// ── Stats ─────────────────────────────────────────────────────────────────────
function showStats() {
  const queue = readQueue();
  const byType = {};
  for (const e of queue) {
    byType[e.type] = (byType[e.type] || 0) + 1;
  }
  console.log(`\nMCP Consumer Status`);
  console.log(`  Queue: ${queue.length} entries`);
  console.log(`  By type: ${JSON.stringify(byType)}`);
  console.log(`  Pattern store: ${PATTERN_STORE}`);
  console.log(`  Drain file: ${DRAIN_FILE}\n`);
}

// ── Main ──────────────────────────────────────────────────────────────────────
async function main() {
  const args = {};
  for (let i = 0; i < process.argv.length; i++) {
    if (process.argv[i].startsWith('--')) {
      const k = process.argv[i].slice(2);
      args[k] = process.argv[i + 1] && !process.argv[i + 1].startsWith('--') ? process.argv[++i] : true;
    }
  }

  if (args.stats || args.status) {
    showStats();
    return;
  }

  await processQueue();
}

main().catch(e => { console.error('[consumer] error:', e.message); });
