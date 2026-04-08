#!/usr/bin/env node
/**
 * OMC Audit + MCP Reporter
 * Reads PostToolUse JSON from stdin → writes audit log → queues MCP reports.
 *
 * Installed via .claude/hooks.json (PostToolUse):
 *   stdin receives: {tool_name, tool_input, outcome, error, hook_event_name, ...}
 *
 * Also handles CLI mode (for hookify compatibility):
 *   node hook-audit-log-mcp.mjs --check --tool Bash --command "rm -rf" --exit 0 --outcome allowed
 */
import { existsSync, readFileSync, appendFileSync, writeFileSync, mkdirSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const STATE_DIR = resolve(__dirname, '../state');
const AUDIT_LOG = resolve(STATE_DIR, 'hook-audit.jsonl');
const MCP_QUEUE = resolve(STATE_DIR, 'mcp-learn-queue.jsonl');
const ERROR_HISTORY = resolve(STATE_DIR, 'hook-error-history.jsonl');
const NUDGE_COUNTER = resolve(STATE_DIR, 'hook-nudge-counter.json');
const NUDGE_FILE = resolve(STATE_DIR, 'session-nudge.md');
const NUDGE_INTERVAL = 50; // Emit nudge every N tool calls

// ── Config ──────────────────────────────────────────────────────────────────
const DANGEROUS_PATTERNS = [
  { pattern: /git\s+clean\s+.*-f.*-d/i, name: 'git-clean-fd' },
  { pattern: /git\s+reset\s+.*--hard/i, name: 'git-reset-hard' },
  { pattern: /rm\s+.*-rf/i, name: 'rm-rf' },
  { pattern: /chmod\s+.*-R\s+777/i, name: 'chmod-777' },
  { pattern: /dd\s+.*if=.*of=/i, name: 'dd-destroy' },
  { pattern: /git\s+push\s+.*--force/i, name: 'git-push-force' },
];

// ── Write to files ─────────────────────────────────────────────────────────────
function ensureDir() {
  if (!existsSync(STATE_DIR)) mkdirSync(STATE_DIR, { recursive: true });
}

function appendAudit(entry) {
  ensureDir();
  appendFileSync(AUDIT_LOG, JSON.stringify(entry) + '\n', 'utf-8');
}

function appendMCP(entry) {
  ensureDir();
  entry.queuedAt = new Date().toISOString();
  appendFileSync(MCP_QUEUE, JSON.stringify(entry) + '\n', 'utf-8');
}

function appendError(entry) {
  ensureDir();
  appendFileSync(ERROR_HISTORY, JSON.stringify(entry) + '\n', 'utf-8');
}

// ── Periodic nudge (debounce counter) ─────────────────────────────────────────
function readNudgeCount() {
  if (!existsSync(NUDGE_COUNTER)) return 0;
  try { return JSON.parse(readFileSync(NUDGE_COUNTER, 'utf-8')).count || 0; }
  catch { return 0; }
}

function writeNudgeCount(count) {
  writeFileSync(NUDGE_COUNTER, JSON.stringify({ count, updatedAt: new Date().toISOString() }, null, 2), 'utf-8');
}

function emitNudge(count) {
  const nudge = `## Periodic Nudge (${count} tool calls)

You've been working for a while. Consider checking:
- Any stalled seeds or experiments?
- Any obvious quality improvements worth capturing?
- Any patterns worth storing for future reference?

Run \`node D:/OpenClaw/workspace/.omc/scripts/hook-session-end-drain.mjs\` when done to flush learnings.
`;
  writeFileSync(NUDGE_FILE, nudge, 'utf-8');
  writeNudgeCount(0); // Reset counter
  log(`nudge: emitted at ${count} tool calls`);
}

function tickNudge() {
  const count = readNudgeCount() + 1;
  if (count % NUDGE_INTERVAL === 0) {
    emitNudge(count);
  } else {
    writeNudgeCount(count);
  }
}

function log(...args) { console.log('[audit]', ...args); }

// ── Classify command ──────────────────────────────────────────────────────────
function classifyCommand(cmd) {
  for (const dp of DANGEROUS_PATTERNS) {
    if (dp.pattern.test(cmd)) return { dangerous: true, name: dp.name };
  }
  return { dangerous: false, name: null };
}

// ── Build audit entry from stdin JSON ──────────────────────────────────────
function buildAuditEntry(input) {
  const tool = input.tool_name || 'unknown';
  const toolInput = input.tool_input || {};
  const cmd = toolInput.command || toolInput.description || '';

  return {
    tool,
    tool_input_preview: cmd.slice(0, 200),
    description: toolInput.description || null,
    filePath: toolInput.file_path || null,
    exitCode: input.exit_code ?? null,
    outcome: input.outcome || 'unknown',
    error: input.error || null,
    hook_event_name: input.hook_event_name || 'PostToolUse',
    sessionId: process.env.OMC_SESSION_ID || 'unknown',
    timestamp: new Date().toISOString(),
  };
}

// ── Build MCP entries ─────────────────────────────────────────────────────────
function buildMCPEntries(entry) {
  const entries = [];

  // Always queue hooks_post-command
  if (entry.tool === 'Bash' && entry.tool_input_preview) {
    entries.push({
      type: 'hooks_post-command',
      command: entry.tool_input_preview,
      exitCode: entry.exitCode ?? 0,
    });
  }

  // Queue error-recovery on failure
  if (entry.error || (entry.exitCode !== null && entry.exitCode !== 0)) {
    const cls = classifyCommand(entry.tool_input_preview || '');
    entries.push({
      type: 'agentdb_pattern-store',
      pattern: `[error-recovery] ${entry.tool_input_preview || entry.tool}`,
      patternType: 'error-recovery',
      confidence: cls.dangerous ? 0.9 : 0.7,
      metadata: {
        severity: cls.dangerous ? 'high' : 'low',
        dangerous: cls.dangerous || false,
        patternName: cls.name || null,
        tool: entry.tool,
        error: entry.error || `exit ${entry.exitCode}`,
        command: entry.tool_input_preview || '',
        learnedAt: new Date().toISOString(),
      },
    });
  }

  return entries;
}

// ── Parse stdin JSON ──────────────────────────────────────────────────────────
async function readStdin() {
  return new Promise((resolve) => {
    let data = '';
    process.stdin.setEncoding('utf-8');
    process.stdin.on('data', (chunk) => { data += chunk; });
    process.stdin.on('end', () => {
      try { resolve(JSON.parse(data)); }
      catch { resolve(null); }
    });
    process.stdin.on('error', () => resolve(null));
  });
}

// ── Parse CLI args ────────────────────────────────────────────────────────────
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

// ── Main from stdin ───────────────────────────────────────────────────────────
async function mainStdin() {
  const input = await readStdin();
  if (!input) return; // No stdin data

  const entry = buildAuditEntry(input);
  appendAudit(entry);
  tickNudge(); // Periodic nudge every N calls

  // Always report command via MCP
  const mcpEntries = buildMCPEntries(entry);
  for (const e of mcpEntries) appendMCP(e);

  // Error capture for failed Bash
  if (input.tool_name === 'Bash' && input.error) {
    const errEntry = {
      ...entry,
      capturedAt: new Date().toISOString(),
    };
    appendError(errEntry);
  }

  // Output for debugging
  if (entry.tool === 'Bash') {
    console.log(`audit:${entry.tool} outcome=${entry.outcome} cmd=${entry.tool_input_preview?.slice(0, 40)}`);
  }
}

// ── Main from CLI ──────────────────────────────────────────────────────────────
function mainCLI(args) {
  const entry = {
    tool: args.tool || 'Bash',
    tool_input_preview: args.command || '',
    exitCode: parseInt(args.exit || '0'),
    outcome: args.outcome || 'allowed',
    error: args.error || null,
    hook_event_name: 'PostToolUse',
    sessionId: process.env.OMC_SESSION_ID || 'unknown',
    timestamp: new Date().toISOString(),
  };

  appendAudit(entry);

  const mcpEntries = buildMCPEntries(entry);
  for (const e of mcpEntries) appendMCP(e);

  tickNudge(); // Periodic nudge every N calls
  console.log(`audit-logged:${entry.tool} exit=${entry.exitCode}`);
}

// ── Main ──────────────────────────────────────────────────────────────────────
async function main() {
  const args = parseArgs(process.argv.slice(2));

  if (args.check || args.stdin) {
    await mainStdin();
  } else if (args.tool) {
    mainCLI(args);
  } else {
    // Check if stdin has data
    if (!process.stdin.isTTY) {
      await mainStdin();
    } else {
      console.log('OMC Audit+MCP Reporter');
      console.log('  --check    Read PostToolUse JSON from stdin');
      console.log('  --tool X   CLI mode: specify tool name');
    }
  }
}

main().catch(() => {}); // Never fail — hook execution must not block
