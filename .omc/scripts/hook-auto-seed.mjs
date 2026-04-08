#!/usr/bin/env node
/**
 * OMC Auto-Seed Generator Hook
 * Tracks tool call count per session → auto-creates seed in ideas.md after 5+ calls.
 *
 * Usage (as hook script):
 *   node hook-auto-seed.mjs [--check] [--reset]
 *     --check  : Increment counter, check threshold, write seed if reached
 *     --reset  : Reset counter for new session
 *
 * Architecture:
 *   PostToolUse hook fires on every tool call → invokes this with --check
 *   Counter stored in .omc/state/auto-seed-counter.json
 *   When threshold reached (5+ calls), writes AUTO: marker to ideas.md
 *   Pre-prompt hook detects AUTO: marker → prompts user for seed adoption
 *   User says "yes" → seed becomes a real seed in ideas.md
 *
 * Anti-recursion: Uses --check flag, counter only increments on actual task tools.
 */
import { existsSync, readFileSync, writeFileSync, mkdirSync, appendFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const STATE_DIR = resolve(__dirname, '../state');
const STATE_FILE = resolve(STATE_DIR, 'auto-seed-counter.json');
const IDEAS_FILE = resolve(__dirname, '../innovation/ideas.md');

// ── Config ──────────────────────────────────────────────────────────────────
const THRESHOLD = 5; // 5+ tool calls triggers seed auto-creation

// ── State ───────────────────────────────────────────────────────────────────
function readState() {
  if (!existsSync(STATE_FILE)) return { count: 0, fired: false, sessionId: null };
  try {
    return JSON.parse(readFileSync(STATE_FILE, 'utf-8'));
  } catch {
    return { count: 0, fired: false, sessionId: null };
  }
}

function writeState(state) {
  if (!existsSync(STATE_DIR)) mkdirSync(STATE_DIR, { recursive: true });
  writeFileSync(STATE_FILE, JSON.stringify(state, null, 2), 'utf-8');
}

function appendIdea(line) {
  appendFileSync(IDEAS_FILE, line + '\n', 'utf-8');
}

function hasRecentAutoSeed() {
  if (!existsSync(IDEAS_FILE)) return false;
  const content = readFileSync(IDEAS_FILE, 'utf-8');
  const lines = content.split('\n');
  // Check last 10 lines for AUTO: marker
  const recent = lines.slice(-10);
  return recent.some(l => l.includes('[AUTO:'));
}

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

// ── Extract context from recent audit log ────────────────────────────────────
function extractRecentContext() {
  const auditPath = resolve(__dirname, '../state/hook-audit.jsonl');
  if (!existsSync(auditPath)) return null;

  const raw = readFileSync(auditPath, 'utf-8');
  const lines = raw.split('\n').filter(Boolean).slice(-20);

  const entries = lines.map(l => {
    try { return JSON.parse(l); } catch { return null; }
  }).filter(Boolean);

  // Build simple context: last 5 unique commands
  const cmds = [];
  for (let i = entries.length - 1; i >= 0; i--) {
    const e = entries[i];
    if (e.command && !cmds.includes(e.command)) {
      cmds.push(e.command);
    }
    if (cmds.length >= 5) break;
  }

  return cmds.length > 0 ? cmds.join('; ') : null;
}

// ── Generate seed suggestion ─────────────────────────────────────────────────
function generateSeedEntry(state, context) {
  const today = new Date().toISOString().split('T')[0];
  const count = state.count;
  const ctx = context || '工具调用累计达到5+次';

  // Generate a plausible seed based on context
  // Format: - [DATE] STAGE [source] [score:Benefit×Feasibility] [f:Feasibility] description
  // For now, create a generic "automated discovery" seed
  // In the future, could use LLM to generate context-specific seeds
  const entry = `- [${today}] STAGE [AUTO:auto-seed-generator] [score:3×4=12] [f:4] 自动化工具调用模式识别 | benefit: 从${count}次调用中提取工作流模式并固化 | reason: 工具调用已达${count}次，存在可复用的工作流 | approach: 分析调用链→识别高频模式→生成可复用skill或adapter | AUTO:${Date.now()}`;

  return entry;
}

// ── Main ─────────────────────────────────────────────────────────────────────
async function main() {
  const args = parseArgs(process.argv.slice(2));

  // --reset: fresh session
  if (args.reset) {
    writeState({ count: 0, fired: false, sessionId: Date.now().toString() });
    console.log('counter reset');
    return;
  }

  // --check: increment + evaluate
  if (args.check) {
    const state = readState();
    const newState = { ...state, count: state.count + 1 };
    writeState(newState);

    // Check threshold (and not already fired this session)
    if (newState.count >= THRESHOLD && !newState.fired && !hasRecentAutoSeed()) {
      const context = extractRecentContext();
      const entry = generateSeedEntry(newState, context);

      try {
        appendIdea(entry);
        newState.fired = true;
        writeState(newState);
        console.log(`AUTO:${entry}`);
      } catch (e) {
        console.error('failed to write seed:', e.message);
      }
    } else {
      console.log(`count:${newState.count}/${THRESHOLD}`);
    }
    return;
  }

  // Default: show status
  const state = readState();
  console.log(`OMC Auto-Seed Status`);
  console.log(`  Count: ${state.count}/${THRESHOLD}`);
  console.log(`  Fired: ${state.fired}`);
  console.log(`  Session: ${state.sessionId || 'none'}`);
  console.log(`  Ideas file: ${IDEAS_FILE}`);
  console.log(`\nUsage:`);
  console.log(`  --reset  Reset counter for new session`);
  console.log(`  --check  Increment counter, fire seed if threshold reached`);
}

main().catch(e => { console.error(e.message); process.exit(1); });
