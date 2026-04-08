#!/usr/bin/env node
/**
 * OMC Periodic Nudge Hook
 * Session-end hook that prompts to persist knowledge after N operations.
 *
 * Inspired by Hermes Agent's Periodic Nudge:
 *   After N tool calls or operations, prompt to:
 *   - Persist learnings to memory
 *   - Update skill effectiveness
 *   - Log session insights
 *
 * Usage:
 *   node hook-nudge.mjs --check      # check if nudge should fire
 *   node hook-nudge.mjs --reset      # reset counter for new session
 *   node hook-nudge.mjs --force      # force nudge regardless of count
 *
 * Architecture:
 *   PrePrompt hook checks counter → if threshold reached, shows nudge prompt
 *   State stored in .omc/state/nudge-state.json
 */
import { existsSync, readFileSync, writeFileSync, mkdirSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const STATE_DIR = resolve(__dirname, '../state');
const STATE_FILE = resolve(STATE_DIR, 'nudge-state.json');
const MEMORY_FILE = resolve(__dirname, '../memory/key-learnings.md');
const NOTEPAD_FILE = resolve(__dirname, '../notepad.md');

// ── Config ──────────────────────────────────────────────────────────────────
const NUDGE_THRESHOLD = 10; // nudge every 10 tool calls
const COOLDOWN_FILE = resolve(STATE_DIR, 'nudge-cooldown.json');

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

function readCooldown() {
  if (!existsSync(COOLDOWN_FILE)) return { lastNudge: null };
  try {
    return JSON.parse(readFileSync(COOLDOWN_FILE, 'utf-8'));
  } catch {
    return { lastNudge: null };
  }
}

function writeCooldown(state) {
  writeFileSync(COOLDOWN_FILE, JSON.stringify(state, null, 2), 'utf-8');
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

// ── Extract recent context from hook audit ─────────────────────────────────
function extractRecentContext() {
  const auditPath = resolve(__dirname, '../state/hook-audit.jsonl');
  if (!existsSync(auditPath)) return [];

  const raw = readFileSync(auditPath, 'utf-8');
  const lines = raw.split('\n').filter(Boolean).slice(-50);

  const entries = lines.map(l => {
    try { return JSON.parse(l); } catch { return null; }
  }).filter(Boolean);

  // Build context summary
  const tools = new Set();
  const commands = [];
  for (let i = entries.length - 1; i >= 0; i--) {
    const e = entries[i];
    if (e.tool) tools.add(e.tool);
    if (e.command && commands.length < 5) {
      commands.push(e.command.slice(0, 60));
    }
  }

  return { tools: Array.from(tools), commands };
}

// ── Nudge message generator ─────────────────────────────────────────────────
function generateNudge(state, context) {
  const { tools, commands } = context;
  const toolList = tools.slice(0, 5).join(', ') || 'unknown';

  return `🧠 **Hermes Periodic Nudge** (operation #${state.count})

You've performed ${state.count} operations this session. Time for a knowledge checkpoint.

**Recent tools**: ${toolList}
${commands.length > 0 ? `**Recent commands**:\n${commands.map(c => `  - ${c}`).join('\n')}` : ''}

Consider:
1. **Key Learning**: Any insight worth remembering for next session?
2. **Skill Update**: Did any skill perform unexpectedly well/poorly?
3. **Pattern**: Any repeated mistake to avoid?
4. **Seed**: Any new idea sparked by this work?

Reply with any learnings to persist, or 'skip' to continue.`;
}

// ── Main ─────────────────────────────────────────────────────────────────────
async function main() {
  const args = parseArgs(process.argv.slice(2));

  // --reset: fresh session
  if (args.reset) {
    writeState({ count: 0, fired: false, sessionId: Date.now().toString() });
    writeCooldown({ lastNudge: null });
    console.log('nudge counter reset');
    return;
  }

  // --check: increment + evaluate
  if (args.check) {
    const state = readState();
    const newState = { ...state, count: state.count + 1 };
    writeState(newState);

    // Check threshold (or force)
    const shouldNudge = args.force || newState.count >= NUDGE_THRESHOLD;
    const cooldown = readCooldown();

    // Cooldown: don't nudge twice within 5 minutes
    const now = Date.now();
    const cooldownActive = cooldown.lastNudge && (now - cooldown.lastNudge) < 5 * 60 * 1000;

    if (shouldNudge && !cooldownActive) {
      const context = extractRecentContext();
      const nudge = generateNudge(newState, context);

      console.log('NUDGE:' + JSON.stringify({ message: nudge, count: newState.count }));

      writeCooldown({ lastNudge: now });
      newState.fired = true;
      writeState(newState);
    } else {
      console.log(`count:${newState.count}/${NUDGE_THRESHOLD}`);
    }
    return;
  }

  // Default: show status
  const state = readState();
  const cooldown = readCooldown();
  console.log(`OMC Periodic Nudge Status`);
  console.log(`  Count: ${state.count}/${NUDGE_THRESHOLD}`);
  console.log(`  Fired: ${state.fired}`);
  console.log(`  Last nudge: ${cooldown.lastNudge ? new Date(cooldown.lastNudge).toISOString() : 'never'}`);
  console.log(`\nUsage:`);
  console.log(`  --reset  Reset counter for new session`);
  console.log(`  --check  Increment counter, fire nudge if threshold reached`);
  console.log(`  --force  Force nudge regardless of count`);
}

main().catch(e => { console.error(e.message); process.exit(1); });
