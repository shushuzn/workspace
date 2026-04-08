#!/usr/bin/env node
/**
 * OMC Auto-Insight Generator Hook
 * Tracks tool call count per session → triggers in-session insight generation after 10+ calls.
 *
 * Usage (as hook script):
 *   node hook-auto-seed.mjs [--check] [--reset]
 *     --check  : Increment counter, check threshold, trigger insight if reached
 *     --reset  : Reset counter for new session
 *
 * Architecture:
 *   PostToolUse hook fires on every tool call → invokes this with --check
 *   Counter stored in .omc/state/auto-seed-counter.json
 *   When threshold reached (10+ calls):
 *     1. Writes tool call stats to .omc/state/auto-insight-trigger.json
 *     2. AI detects trigger on next prompt → generates insight with Fix in-session
 *     3. Insight written to session-insights.md → pending-actions.md → step7 executes Fix
 *   Anti-recursion: OMC_SKIP_HOOKS env var prevents re-triggering this hook
 *
 * INSIGHT GENERATION IS IN-SESSION:
 *   The AI itself generates the insight (not a subagent). The hook only sets the trigger.
 *   On next user prompt, the AI sees the trigger and generates:
 *     ### N. [title]
 *     **Observation**: ...
 *     **Rule**: ...
 *     **Fix**: [concrete executable action]
 */
import { existsSync, readFileSync, writeFileSync, mkdirSync, appendFileSync, readdirSync, statSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const readStdin = () => new Promise(resolve => {
  let data = '';
  process.stdin.setEncoding('utf8');
  process.stdin.on('data', chunk => data += chunk);
  process.stdin.on('end', () => resolve(data));
  process.stdin.on('error', () => resolve(''));
  // No timeout - resolve immediately if stdin is already exhausted
  setImmediate(() => resolve(data));
});

const __dirname = dirname(fileURLToPath(import.meta.url));
const STATE_DIR = resolve(__dirname, '../state');
const STATE_FILE = resolve(STATE_DIR, 'auto-seed-counter.json');
const TRIGGER_FILE = resolve(STATE_DIR, 'auto-insight-trigger.json');
const INSIGHTS_FILE = resolve(STATE_DIR, 'session-insights.md');
const IDEAS_FILE = resolve(__dirname, '../innovation/ideas.md');
const NUDGE_FILE = resolve(STATE_DIR, 'session-nudge.md');
const NOTPAD_FILE = resolve(__dirname, '../notepad.md');

// ── Config ──────────────────────────────────────────────────────────────────
const THRESHOLD = 10; // 10+ tool calls triggers insight generation

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
// Hook injects session_id via stdin; env vars also checked as fallback.
// If sessionId changed (compaction continuation), PRESERVE count — don't reset to 0.
function getCurrentSessionId(hookSessionId) {
  // stdin from hook has highest priority
  if (hookSessionId) return hookSessionId;
  // OMC_SESSION_ID env var is the current session — always prefer it
  if (process.env.OMC_SESSION_ID) return process.env.OMC_SESSION_ID;
  // Transcript path contains session ID: .../{sessionId}.jsonl
  if (process.env.OMC_TRANSCRIPT_PATH) {
    const match = process.env.OMC_TRANSCRIPT_PATH.match(/([a-f0-9-]{36})\.jsonl$/);
    if (match) return match[1];
  }
  // Fallback: find latest transcript file (most recently modified .jsonl = current session)
  const transcriptsDir = 'C:/Users/adm/.claude/projects/D--OpenClaw-workspace';
  if (existsSync(transcriptsDir)) {
    try {
      const entries = readdirSync(transcriptsDir);
      let latestTranscript = null;
      let latestMtime = 0;
      for (const entry of entries) {
        if (!entry.endsWith('.jsonl')) continue;
        const fullPath = resolve(transcriptsDir, entry);
        const stat = statSync(fullPath);
        if (stat.mtimeMs > latestMtime) {
          latestMtime = stat.mtimeMs;
          latestTranscript = entry;
        }
      }
      if (latestTranscript) {
        const match = latestTranscript.match(/^([a-f0-9-]+)\.jsonl$/);
        if (match) return match[1];
      }
    } catch { /* fall through */ }
  }
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
  const recent = lines.slice(-30); // look back 30 lines for today's entries
  const todayLocal = new Date().toLocaleDateString('en-CA'); // YYYY-MM-DD local timezone
  return recent.some(l => {
    if (!l.includes('[AUTO:') || l.includes('shipped:') || l.includes('killed:')) return false;
    const dateMatch = l.match(/^\- \[(\d{4}-\d{2}-\d{2})\]/);
    return dateMatch && dateMatch[1] === todayLocal;
  });
}

// ── Generate trigger for in-session insight ──────────────────────────────────
function writeInsightTrigger(state, toolStats) {
  const trigger = {
    sessionId: state.sessionId,
    count: state.count,
    threshold: THRESHOLD,
    toolStats,
    triggeredAt: new Date().toISOString(),
  };
  writeFileSync(TRIGGER_FILE, JSON.stringify(trigger, null, 2), 'utf-8');
}

// Read tool stats from current transcript (live stats)
function readLiveToolStats(sessionId) {
  if (!sessionId) return null;
  const transcriptPath = `C:/Users/adm/.claude/projects/D--OpenClaw-workspace/${sessionId}.jsonl`;
  if (!existsSync(transcriptPath)) return null;
  try {
    const lines = readFileSync(transcriptPath, 'utf-8').split('\n').filter(Boolean);
    const tools = { Bash: 0, Read: 0, Write: 0, Edit: 0, Grep: 0, TaskCreate: 0, TaskUpdate: 0 };
    const bashCommands = [];
    let toolCalls = 0;
    for (const line of lines) {
      try {
        const entry = JSON.parse(line);
        const content = entry.message?.content;
        if (Array.isArray(content)) {
          for (const block of content) {
            if (block.type === 'tool_use' && block.name) {
              toolCalls++;
              for (const t of Object.keys(tools)) { if (block.name.includes(t)) tools[t]++; }
              if (block.name === 'Bash' && block.input?.command) {
                bashCommands.push(block.input.command.slice(0, 80));
              }
            }
          }
        }
      } catch {}
    }
    // Top 5 bash commands (deduped, excluding self-scripts)
    const selfScripts = ['hook-stats.mjs', 'omc-insight-action.mjs', 'omc-insight-generator.mjs', 'hook-audit-log-mcp.mjs'];
    const topBash = [...new Set(bashCommands)]
      .filter(cmd => !selfScripts.some(s => cmd.includes(s)))
      .slice(0, 5);
    return { tools, totalToolCalls: toolCalls, topBash };
  } catch { return null; }
}

// ── Generate insight prompt for in-session AI ────────────────────────────────
function buildInsightPrompt(trigger) {
  const { toolStats, count } = trigger;
  const statsText = toolStats
    ? `工具统计: Bash=${toolStats.tools.Bash}, Read=${toolStats.tools.Read}, Edit=${toolStats.tools.Edit}, Write=${toolStats.tools.Write}, Grep=${toolStats.tools.Grep}`
    : `${count} 次工具调用`;

  return `## IN-SESSION INSIGHT TRIGGER

检测到 ${count} 次工具调用（阈值 ${THRESHOLD}），请立即生成一条 insight。

当前工具统计：
${statsText}
${toolStats?.topBash?.length ? `Top Bash 命令：\n${toolStats.topBash.map((c, i) => `${i + 1}. ${c}`).join('\n')}` : ''}

请分析上述数据，生成一条 insight，格式：

### N. [标题]
**Observation**: [具体观察，数据驱动]
**Rule**: [规则/模式识别]
**Fix**: [如果可以执行的具体修复动作，写具体命令/文件/代码；否则写 N/A]

要求：
- Fix 必须是可执行的（具体文件、具体改动）
- 如果观察到的模式只有 tracking 价值，写 Fix: N/A
- 生成 1 条高质量 insight 即可
- 写完后将 insight 追加到 .omc/state/session-insights.md
- 如果 Fix 不是 N/A，同时追加到 .omc/state/pending-actions.md，格式："- [ ] title | action: Fix内容 | id: auto-[timestamp]"
`;
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

// ── Main ─────────────────────────────────────────────────────────────────────
async function main() {
  const args = parseArgs(process.argv.slice(2));

  // Read session_id: from --session arg, then stdin (PostToolUse passes JSON via stdin)
  let hookSessionId = null;
  if (args.session) hookSessionId = args.session;
  if (!hookSessionId) {
    try {
      const stdin = await readStdin();
      if (stdin && stdin.trim()) {
        const event = JSON.parse(stdin);
        if (event.session_id) hookSessionId = event.session_id;
      }
    } catch {}
  }

  // --reset: fresh session
  if (args.reset) {
    const sid = getCurrentSessionId(hookSessionId);
    writeState({ count: 0, fired: false, sessionId: sid });
    console.log('counter reset');
    return;
  }

  // --check: read transcript total tool calls, trigger if >= THRESHOLD
  if (args.check) {
    const currentSession = getCurrentSessionId(hookSessionId);
    const state = readState();
    const sameSession = state.sessionId === currentSession;

    // Read live tool count from transcript
    const toolStats = readLiveToolStats(currentSession) || { totalToolCalls: 0, tools: {}, topBash: [] };
    const totalCalls = toolStats.totalToolCalls || 0;

    // Only reset if session changed
    if (!sameSession) {
      writeState({ count: 0, fired: false, sessionId: currentSession });
    }

    // Read current state fresh
    const freshState = readState();
    if (totalCalls >= THRESHOLD) {
      try {
        const trigger = {
          sessionId: currentSession,
          count: totalCalls,
          threshold: THRESHOLD,
          toolStats,
          triggeredAt: new Date().toISOString(),
        };
        writeFileSync(TRIGGER_FILE, JSON.stringify(trigger, null, 2), 'utf-8');

        const today = new Date().toLocaleDateString('en-CA');
        const entry = `- [${today}] STAGE [AUTO:auto-insight] [score:3×4=12] [f:4] 原生insight生成 | benefit: AI在会话中实时生成带Fix的insight | reason: 工具调用已达${totalCalls}次，触发实时insight | approach: hook触发→AI生成→session-insights.md→step7执行 | AUTO:${Date.now()}`;
        appendIdea(entry);

        // Also append trigger to nudge file so AI sees it on next prompt
        const nudgeLine = `⚡ INSIGHT TRIGGER: ${totalCalls} tool calls reached — generate insight now: .omc/state/session-insights.md`;
        appendFileSync(NUDGE_FILE, nudgeLine + '\n', 'utf-8');

        // Write to notepad Priority Context for immediate AI visibility
        const notepadContent = `# Notepad
<!-- Auto-managed by OMC. Manual edits preserved in MANUAL section. -->

## Priority Context
<!-- ALWAYS loaded. Keep under 500 chars. Critical discoveries only. -->
⚡ INSIGHT TRIGGER: ${totalCalls} tool calls (threshold ${THRESHOLD}) — generate insight: .omc/state/session-insights.md | Read trigger: .omc/state/auto-insight-trigger.json

DESIGN.md pattern (VoltAgent/awesome-design-md): 9 sections — Visual Theme, Colors, Typography, Components, Layout, Depth, Do's/Don'ts, Responsive, Agent Prompts. Key: dark themes use bg luminance stepping + semi-transparent white borders. Light themes use shadow-as-border technique. All use variable fonts with negative tracking at display sizes. REF: memory/design-systems-learned.md

## Working Memory
<!-- Session notes. Auto-pruned after 7 days. -->

## MANUAL
<!-- User content. Never auto-pruned. -->
`;
        writeFileSync(NOTPAD_FILE, notepadContent, 'utf-8');

        // Spawn subagent to generate insight AND execute Fix — avoids compact session output trap
        const { spawn } = await import('child_process');
        const insightsFile = INSIGHTS_FILE;
        const triggerFile = TRIGGER_FILE;
        const prompt = `Read ${triggerFile}. Generate ONE insight in this format: ### N. [title] | **Observation**: [data from tool stats] | **Rule**: [pattern] | **Fix**: [action or N/A]. If Fix is not N/A: execute it via node/Bash/Edit tools, then append insight to ${insightsFile} marked EXECUTED. If Fix is N/A, just append.`;
        const agentCmd = `claude.cmd --print --bare "${prompt.replace(/"/g, '\\"')}"`;

        spawn(agentCmd, {
          shell: true,
          cwd: resolve(__dirname, '../..'),
          detached: true,
          stdio: 'ignore'
        }).unref();

        console.log(`AUTO:insight-spawned (totalCalls:${totalCalls})`);
      } catch (e) {
        console.error('failed to trigger insight:', e.message);
      }
    } else {
      console.log(`totalToolCalls:${totalCalls}/${THRESHOLD}`);
    }
    return;
  }

  // Default: show status
  const state = readState();
  console.log(`OMC Auto-Insight Status`);
  console.log(`  Count: ${state.count}/${THRESHOLD}`);
  console.log(`  Fired: ${state.fired}`);
  console.log(`  Session: ${state.sessionId || 'none'}`);
  console.log(`  Trigger file: ${TRIGGER_FILE}`);
  console.log(`\nUsage:`);
  console.log(`  --reset  Reset counter for new session`);
  console.log(`  --check  Increment counter, fire insight trigger if threshold reached`);
}

main().catch(e => { console.error(e.message); process.exit(1); });
