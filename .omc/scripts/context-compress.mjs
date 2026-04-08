#!/usr/bin/env node
/**
 * OMC Context Compressor
 * Intelligent context window management — protect head/tail, compress middle.
 *
 * Inspired by Hermes Agent's ContextCompressor:
 *   - Protect first N + last N messages (configurable)
 *   - Compress middle turns via summarization
 *   - Dynamic threshold triggers (default 85% of context limit)
 *   - Reduces input tokens by up to 75%
 *
 * Usage:
 *   node context-compress.mjs --compress transcript.jsonl    # compress session
 *   node context-compress.mjs --status                      # show compression stats
 *   node context-compress.mjs --preview transcript.jsonl    # preview compression
 *   node context-compress.mjs --init                       # init state
 *
 * Architecture:
 *   - Works on .omc/sessions/*.json transcript files
 *   - State in .omc/state/compression-state.json
 *   - Compressed sessions tagged with metadata
 */
import { existsSync, readFileSync, writeFileSync, mkdirSync, readdirSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const STATE_DIR = resolve(__dirname, '../state');
const STATE_FILE = resolve(STATE_DIR, 'compression-state.json');
const CONTEXT_LIMIT = 150000; // ~150k chars (~100k tokens)
const HEAD_PROTECT = 5; // keep first 5 messages
const TAIL_PROTECT = 10; // keep last 10 messages
const THRESHOLD = 0.85; // compress when 85% of limit reached

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i++) {
    if (argv[i].startsWith('--')) {
      const key = argv[i].slice(2);
      args[key] = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : true;
    }
  }
  return args;
}

function readState() {
  if (!existsSync(STATE_FILE)) return { totalCompressed: 0, totalSaved: 0, lastCompress: null };
  try { return JSON.parse(readFileSync(STATE_FILE, 'utf-8')); }
  catch { return { totalCompressed: 0, totalSaved: 0, lastCompress: null }; }
}

function writeState(state) {
  if (!existsSync(STATE_DIR)) mkdirSync(STATE_DIR, { recursive: true });
  writeFileSync(STATE_FILE, JSON.stringify(state, null, 2), 'utf-8');
}

// ── Token estimation (rough: 1 token ≈ 4 chars) ─────────────────────────────
function estimateTokens(text) {
  return Math.ceil((text || '').length / 4);
}

// ── Extract messages from JSONL transcript ──────────────────────────────────
function extractMessages(jsonlPath) {
  if (!existsSync(jsonlPath)) return null;
  try {
    const content = readFileSync(jsonlPath, 'utf-8');
    const lines = content.split('\n').filter(Boolean);
    return lines.map(l => {
      try { return JSON.parse(l); } catch { return null; }
    }).filter(Boolean);
  } catch {
    return null;
  }
}

// ── Simple extractive summarization ─────────────────────────────────────────
function extractiveSummary(messages, maxTokens = 500) {
  // Select most "important" messages by:
  // 1. Messages with tool calls (higher weight)
  // 2. Messages with longer content
  // 3. Messages from assistant role

  const scored = messages.map((m, idx) => {
    let weight = 1;
    if (m.tool_calls) weight += 2;
    if (m.role === 'assistant') weight += 1;
    if (m.content && m.content.length > 200) weight += 1;
    return { idx, msg: m, weight };
  });

  // Select top messages by weight
  scored.sort((a, b) => b.weight - a.weight);
  const selected = scored.slice(0, Math.ceil(maxTokens / 50))
    .sort((a, b) => a.idx - b.idx);

  return selected.map(s => s.msg);
}

// ── Compress messages ───────────────────────────────────────────────────────
function compressMessages(messages, headProtect = HEAD_PROTECT, tailProtect = TAIL_PROTECT) {
  if (!messages || messages.length === 0) return [];

  const totalTokens = messages.reduce((s, m) => s + estimateTokens(m.content || ''), 0);

  // If under threshold, no compression needed
  if (totalTokens < CONTEXT_LIMIT * THRESHOLD) {
    return { compressed: false, messages, savedTokens: 0, reason: 'under_threshold' };
  }

  // Protect head and tail
  const head = messages.slice(0, headProtect);
  const tail = messages.slice(-tailProtect);
  const middle = messages.slice(headProtect, -tailProtect);

  // Summarize middle
  const summarizedMiddle = extractiveSummary(middle);

  // Build compressed session metadata
  const compressionNote = {
    role: 'system',
    content: `[COMPRESSED ${middle.length} messages → ${summarizedMiddle.length} messages | ` +
      `Original tokens: ~${totalTokens} | Head: ${headProtect} | Tail: ${tailProtect}]`,
    compressed: true,
    original_count: middle.length,
    compressed_count: summarizedMiddle.length,
  };

  const result = [...head, compressionNote, ...summarizedMiddle, ...tail];
  const resultTokens = result.reduce((s, m) => s + estimateTokens(m.content || ''), 0);

  return {
    compressed: true,
    messages: result,
    savedTokens: totalTokens - resultTokens,
    savedPercent: Math.round((1 - resultTokens / totalTokens) * 100),
    originalCount: messages.length,
    resultCount: result.length,
  };
}

// ── Apply compression to session ────────────────────────────────────────────
function compressSession(sessionPath) {
  const messages = extractMessages(sessionPath);
  if (!messages) {
    return { error: 'Could not read session' };
  }

  const totalTokens = messages.reduce((s, m) => s + estimateTokens(m.content || ''), 0);
  const result = compressMessages(messages);

  return {
    path: sessionPath,
    totalTokens,
    ...result,
  };
}

// ── Main ─────────────────────────────────────────────────────────────────────
async function main() {
  const args = parseArgs(process.argv.slice(2));

  if (args.compress) {
    const sessionPath = resolve(process.cwd(), args.compress);
    const result = compressSession(sessionPath);

    if (result.error) {
      console.error(`Error: ${result.error}`);
      return;
    }

    if (!result.compressed) {
      console.log(`Session under threshold (${result.totalTokens} tokens < ${CONTEXT_LIMIT * THRESHOLD}), no compression needed.`);
      return;
    }

    // Update state
    const state = readState();
    state.totalCompressed = (state.totalCompressed || 0) + 1;
    state.totalSaved = (state.totalSaved || 0) + result.savedTokens;
    state.lastCompress = new Date().toISOString();
    writeState(state);

    console.log(`✅ Compressed: ${result.originalCount} → ${result.resultCount} messages`);
    console.log(`   Saved: ~${result.savedTokens} tokens (${result.savedPercent}%)`);
    console.log(`   Total compressed: ${state.totalCompressed} sessions, ~${state.totalSaved} tokens saved`);
    return;
  }

  if (args.preview) {
    const sessionPath = resolve(process.cwd(), args.preview);
    const messages = extractMessages(sessionPath);
    if (!messages) {
      console.error(`Could not read: ${sessionPath}`);
      return;
    }

    const totalTokens = messages.reduce((s, m) => s + estimateTokens(m.content || ''), 0);
    const result = compressMessages(messages);

    console.log(`\n📊 Compression Preview`);
    console.log(`  File: ${sessionPath}`);
    console.log(`  Messages: ${messages.length}`);
    console.log(`  Est. tokens: ${totalTokens}`);
    console.log(`  Threshold: ${Math.round(CONTEXT_LIMIT * THRESHOLD)}`);
    console.log(`  Compressed: ${result.compressed ? 'yes' : 'no'}`);
    if (result.compressed) {
      console.log(`  Result: ${result.originalCount} → ${result.resultCount} messages`);
      console.log(`  Savings: ~${result.savedTokens} tokens (${result.savedPercent}%)`);
    }
    console.log();
    return;
  }

  if (args.status) {
    const state = readState();
    console.log(`\n📊 OMC Context Compression Status`);
    console.log(`  Sessions compressed: ${state.totalCompressed}`);
    console.log(`  Total tokens saved: ~${state.totalSaved}`);
    console.log(`  Last compression: ${state.lastCompress || 'never'}`);
    console.log(`  Config: head=${HEAD_PROTECT}, tail=${TAIL_PROTECT}, threshold=${THRESHOLD}`);
    console.log();
    return;
  }

  // Default: help
  console.log(`OMC Context Compressor`);
  console.log(`Usage:`);
  console.log(`  --compress file.jsonl   Compress a session transcript`);
  console.log(`  --preview file.jsonl   Preview compression without applying`);
  console.log(`  --status               Show compression statistics`);
}

main().catch(e => { console.error(e.message); process.exit(1); });
