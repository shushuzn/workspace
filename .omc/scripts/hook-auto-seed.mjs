#!/usr/bin/env node
/**
 * OMC Auto-Seed Generator Hook
 * Tracks tool call count per session → auto-executes highest-score seed after 5+ calls.
 *
 * Usage (as hook script):
 *   node hook-auto-seed.mjs [--check] [--reset]
 *     --check  : Increment counter, check threshold, spawn executor if reached
 *     --reset  : Reset counter for new session
 *
 * Architecture:
 *   PostToolUse hook fires on every tool call → invokes this with --check
 *   Counter stored in .omc/state/auto-seed-counter.json
 *   When threshold reached (5+ calls):
 *     1. Writes seed entry to ideas.md (backup for manual review)
 *     2. Spawns detached executor via OMC_SKIP_HOOKS + background bash
 *     3. Executor parses ideas.md, picks highest-score un-shipped seed, executes, marks shipped
 *   Anti-recursion: OMC_SKIP_HOOKS env var prevents re-triggering this hook
 */
import { existsSync, readFileSync, writeFileSync, mkdirSync, appendFileSync, readdirSync, statSync } from 'fs';
import { spawn } from 'child_process';
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

// Detect session continuity by comparing sessionId from transcript path.
// Hookify injects session_id in hook env vars; fallback to matching state file sessionId.
// If sessionId changed (compaction continuation), PRESERVE count — don't reset to 0.
function getCurrentSessionId() {
  // Try OMC session state files first — format: sessions/{sessionId}/state.json
  const sessionsDir = resolve(__dirname, '../state/sessions');
  if (existsSync(sessionsDir)) {
    try {
      const entries = readdirSync(sessionsDir);
      // Find the most recent session directory
      let latestSession = null;
      let latestMtime = 0;
      for (const entry of entries) {
        if (entry.startsWith('.')) continue;
        const fullPath = resolve(sessionsDir, entry);
        const stat = statSync(fullPath);
        if (stat.mtimeMs > latestMtime) {
          latestMtime = stat.mtimeMs;
          latestSession = entry;
        }
      }
      if (latestSession) return latestSession;
    } catch { /* fall through */ }
  }
  // Fallback: environment variable set by hook system
  if (process.env.OMC_SESSION_ID) return process.env.OMC_SESSION_ID;
  // Fallback: Date.now (reliable for single session run)
  return Date.now().toString();
}

function writeState(state) {
  if (!existsSync(STATE_DIR)) mkdirSync(STATE_DIR, { recursive: true });
  writeFileSync(STATE_FILE, JSON.stringify(state, null, 2), 'utf-8');
}

function appendIdea(line) {
  mkdirSync(dirname(IDEAS_FILE), { recursive: true });
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

// ── Generate seed suggestion ─────────────────────────────────────────────────
function generateSeedEntry(state) {
  const today = new Date().toISOString().split('T')[0];
  return `- [${today}] STAGE [AUTO:auto-seed-generator] [score:3×4=12] [f:4] 自动化工具调用模式识别 | benefit: 从${state.count}次调用中提取工作流模式并固化 | reason: 工具调用已达${state.count}次，存在可复用的工作流 | approach: 分析调用链→识别高频模式→生成可复用skill或adapter | AUTO:${Date.now()}`;
}

// ── Spawn executor agent ──────────────────────────────────────────────────────
function spawnExecutor() {
  const executorScript = resolve(__dirname, 'hook-seed-executor.mjs');
  const PROMPT_FILE = resolve(STATE_DIR, 'seed-executor-prompt.txt');
  const CLAUDE_BIN = process.platform === 'win32'
    ? resolve(process.env.APPDATA || '', 'npm/claude.cmd')
    : 'claude';

  // Step 1: run seed-executor to write prompt to file
  // Pass OMC_SEED_PROMPT_FILE so executor knows where to write
  const env1 = {
    ...process.env,
    OMC_SKIP_HOOKS: 'PostToolUse,PreToolUse',
    OMC_SEED_PROMPT_FILE: PROMPT_FILE,
  };
  const child = spawn('node', [executorScript], {
    env: env1,
    stdio: ['ignore', 'pipe', 'pipe'],
    cwd: __dirname,
  });

  let stderr = '';
  child.stdout.on('data', (d) => { process.stdout.write(d); }); // pass through
  child.stderr.on('data', (d) => { stderr += d.toString(); });
  child.on('close', (code) => {
    if (code !== 0) {
      console.error('seed-executor failed:', stderr || `exit ${code}`);
      return;
    }
    if (!existsSync(PROMPT_FILE)) {
      console.log('executor:no-seed');
      return;
    }

    // Step 2: spawn claude CLI with prompt piped via heredoc
    const env2 = {
      ...process.env,
      OMC_SKIP_HOOKS: 'PostToolUse,PreToolUse',
    };
    const prompt = readFileSync(PROMPT_FILE, 'utf-8');
    const claude = spawn('bash', [
      '-c',
      `printf '%s' ${JSON.stringify(prompt)} | "${CLAUDE_BIN.replace(/\\/g, '\\\\')}" --add-mcp-tools --dangerously-skip-permissions`,
    ], {
      env: env2,
      stdio: 'inherit',
      detached: true,
      cwd: 'D:/OpenClaw/workspace',
    });
    claude.unref();
    console.log(`AUTO:claude-spawned (pid ${claude.pid})`);
  });
}

// ── Main ─────────────────────────────────────────────────────────────────────
async function main() {
  const args = parseArgs(process.argv.slice(2));

  // --reset: fresh session (use same sessionId detection as --check)
  if (args.reset) {
    const sid = getCurrentSessionId();
    writeState({ count: 0, fired: false, sessionId: sid });
    console.log('counter reset');
    return;
  }

  // --check: increment + evaluate
  if (args.check) {
    const state = readState();
    const currentSession = getCurrentSessionId();
    // Check if sessionId changed:
    // - Legacy: previous ran with Date.now() timestamp, new uses real session dir.
    //   Treat as same logical session → preserve count (don't reset on format change).
    // - Real change: same format AND different value → compaction continuation.
    //   Reset count so the resumed session gets a fresh 5-call window.
    const LEGACY_RE = /^\d{10,14}$/; // Date.now() timestamps look like 10-14 digits
    const prevIsLegacy = state.sessionId && LEGACY_RE.test(state.sessionId);
    const sameSession = !state.sessionId || state.sessionId === currentSession;
    const effectiveCount = (!sameSession && !prevIsLegacy) ? 0 : state.count;
    const newState = { ...state, count: effectiveCount + 1, sessionId: currentSession };
    writeState(newState);

    // Check threshold (and not already fired this session)
    if (newState.count >= THRESHOLD && !newState.fired) {
      try {
        const entry = generateSeedEntry(newState);
        appendIdea(entry);
        spawnExecutor();
        newState.fired = true;
        writeState(newState);
        console.log(`AUTO:${entry}`);
      } catch (e) {
        console.error('failed to spawn executor:', e.message);
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
