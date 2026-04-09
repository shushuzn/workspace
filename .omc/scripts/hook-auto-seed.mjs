#!/usr/bin/env node
/**
 * OMC Auto-Seed & Insight Trigger Hook
 * Dual mode:
 *   --check  : Incremental counter, read transcript only when threshold reached
 *   --active : Track command patterns, trigger immediately on 3x repetition
 *
 * PostToolUse hook → invokes with --check (fast, no transcript read)
 * Anti-recursion: OMC_SKIP_HOOKS env var prevents re-triggering this hook
 */
import { existsSync, readFileSync, writeFileSync, mkdirSync, appendFileSync, readdirSync, statSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const readStdin = () => new Promise(resolve => {
  let data = '';
  process.stdin.setEncoding('utf8');
  process.stdin.on('data', chunk => data += chunk);
  process.stdin.on('end', () => resolve(data));
  process.on('error', () => resolve(''));
  setImmediate(() => resolve(data));
});

const __dirname = dirname(fileURLToPath(import.meta.url));
const STATE_DIR = resolve(__dirname, '../state');
const STATE_FILE = resolve(STATE_DIR, 'auto-seed-counter.json');
const PATTERN_FILE = resolve(STATE_DIR, 'auto-seed-patterns.json');
const TRIGGER_FILE = resolve(STATE_DIR, 'auto-insight-trigger.json');
const ACTIVE_LEARN_FILE = resolve(STATE_DIR, 'active-learn-trigger.json');
const INSIGHTS_FILE = resolve(STATE_DIR, 'session-insights.md');
const IDEAS_FILE = resolve(__dirname, '../innovation/ideas.md');
const NUDGE_FILE = resolve(STATE_DIR, 'session-nudge.md');
const NOTPAD_FILE = resolve(__dirname, '../notepad.md');
const RECURRENCE_FLAG_FILE = resolve(STATE_DIR, 'insight-recurrence-flag.md');
const INSIGHT_EFFECTIVENESS_FILE = resolve(STATE_DIR, 'insight-effectiveness.json');

const THRESHOLD = 10;
const PATTERN_WINDOW = 20;   // Track last N commands
const PATTERN_REPEAT = 3;    // Trigger after 3x repetition
const DEBUG_LOOP_THRESHOLD = 3; // Edit+Bash same-target cycle count
const ERROR_REPEAT_THRESHOLD = 2; // Same error message repeat count

const ERROR_CLASS_FILE = resolve(STATE_DIR, 'error-frequency.json');
const RECURRENCE_THRESHOLD = 3; // Same class error 3x → past insight not working

// Error class patterns
const ERROR_CLASS_PATTERNS = [
  { cls: 'regex-bug',       patterns: [/\bregex\b.*(?:error|invalid|failed)/i, /invalid.*regex/i, /pattern.*match.*fail/i, /regexp/i, /regular.*expression/i, /unterminated.*regex/i] },
  { cls: 'permission',      patterns: [/\b(?:EACCES|PERMISSION DENIED|denied|readonly|eperm)\b/i, /permission\b.*denied/i, /cannot.*write.*readonly/i] },
  { cls: 'path-error',       patterns: [/\b(?:ENOENT|NO SUCH FILE|not found|no such file|path.*not.*exist)\b/i, /cannot.*find.*file/i, /directory.*not.*found/i] },
  { cls: 'git-conflict',     patterns: [/\b(?:CONFLICT|MERGE CONFLICT|unmerged|conflict)\b/i, /git.*conflict/i, /<<<<<|>>>>>/i] },
  { cls: 'bash-syntax',      patterns: [/\b(?:syntax error|unexpected token|parse error|shellcheck|invalid shell)\b/i, /bash:.*:.*error/i, /sh:.*\s+error/i] },
  { cls: 'hook-broken',      patterns: [/\b(?:JSON parse|syntax error.*\.mjs|cannot find module|module.*not found|failed to load)\b/i, /require.*module.*not.*found/i, /import.*error/i] },
  { cls: 'network-fail',     patterns: [/\b(?:ECONNREFUSED|connection refused|timeout|network.*error|etimedout|enotfound)\b/i, /fetch.*fail/i, /request.*timeout/i] },
  { cls: 'null-undefined',   patterns: [/\bcannot read propert.*null\b/i, /null.*is not a function\b/i, /undefined.*is not\b/i, /cannot read.*undefined\b/i] },
  { cls: 'git-clean-fd',    patterns: [/clean.*fetch.*failed.*fd/i, /git.*clean.*fatal/i, /lf.*will.*replace.*crlf/i, /hook.*declined.*update/i] },
];

function classifyError(err) {
  for (const { cls, patterns } of ERROR_CLASS_PATTERNS) {
    for (const p of patterns) {
      if (p.test(err)) return cls;
    }
  }
  return 'unknown';
}

function readErrorFreq() {
  if (!existsSync(ERROR_CLASS_FILE)) return { classes: {}, sessionId: null };
  try { return JSON.parse(readFileSync(ERROR_CLASS_FILE, 'utf-8')); }
  catch { return { classes: {}, sessionId: null }; }
}

function writeErrorFreq(data) {
  writeFileSync(ERROR_CLASS_FILE, JSON.stringify(data, null, 2), 'utf-8');
}

// Check if error class is recurring (past insight may not be working)
function checkRecurrence(errorClass, sessionId) {
  const freq = readErrorFreq();
  const now = new Date().toISOString().split('T')[0];
  if (!freq.classes[errorClass]) {
    freq.classes[errorClass] = { sessions: [], totalCount: 0 };
  }
  const clsData = freq.classes[errorClass];
  // Add this session's occurrence
  clsData.sessions.push({ id: sessionId.slice(0, 8), count: 1, date: now });
  clsData.totalCount++;
  // Keep only last 10 sessions
  clsData.sessions = clsData.sessions.slice(-10);
  writeErrorFreq(freq);
  return clsData.totalCount;
}

// ── Insight Effectiveness Scoring ─────────────────────────────────────────────────
// Track if executing an insight's Fix actually reduces error class recurrence
function recordInsightExecuted(errorClass, insightTitle, fixAction) {
  try {
    const data = existsSync(INSIGHT_EFFECTIVENESS_FILE)
      ? JSON.parse(readFileSync(INSIGHT_EFFECTIVENESS_FILE, 'utf-8'))
      : { classes: {} };
    if (!data.classes[errorClass]) data.classes[errorClass] = { insights: [], recurrenceAfter: [] };
    const cls = data.classes[errorClass];
    cls.insights.push({
      title: insightTitle.slice(0, 80),
      fix: fixAction || '',
      executedAt: new Date().toISOString(),
      recurrenceAfter: [], // filled later when recurrence checked
    });
    writeFileSync(INSIGHT_EFFECTIVENESS_FILE, JSON.stringify(data, null, 2), 'utf-8');
  } catch {}
}

// Called when an error of this class recurs AFTER an insight was executed
function recordRecurrenceAfterInsight(errorClass, sessionId) {
  try {
    const data = existsSync(INSIGHT_EFFECTIVENESS_FILE)
      ? JSON.parse(readFileSync(INSIGHT_EFFECTIVENESS_FILE, 'utf-8'))
      : { classes: {} };
    if (!data.classes[errorClass]) return;
    const cls = data.classes[errorClass];
    const lastInsight = cls.insights[cls.insights.length - 1];
    if (lastInsight && lastInsight.recurrenceAfter.length < 10) {
      lastInsight.recurrenceAfter.push({ sessionId: sessionId.slice(0, 8), at: new Date().toISOString() });
    }
    writeFileSync(INSIGHT_EFFECTIVENESS_FILE, JSON.stringify(data, null, 2), 'utf-8');
  } catch {}
}

// Get effectiveness score for an error class: how many recurrences after last insight
function getInsightEffectiveness(errorClass) {
  try {
    const data = existsSync(INSIGHT_EFFECTIVENESS_FILE)
      ? JSON.parse(readFileSync(INSIGHT_EFFECTIVENESS_FILE, 'utf-8'))
      : { classes: {} };
    if (!data.classes[errorClass]) return null;
    const cls = data.classes[errorClass];
    if (cls.insights.length === 0) return null;
    const last = cls.insights[cls.insights.length - 1];
    return {
      totalInsights: cls.insights.length,
      recurrencesAfterLast: last.recurrenceAfter.length,
      firstExecuted: last.executedAt,
    };
  } catch { return null; }
}

// When recurrence threshold exceeded, mark past insights about this error class as ineffective
function markInsightIneffective(errorClass, eff) {
  if (!existsSync(INSIGHTS_FILE)) return;
  try {
    let content = readFileSync(INSIGHTS_FILE, 'utf-8');
    const lines = content.split('\n');
    let found = false;
    // Error class keywords to match against insight titles/bodies
    const classKeywords = {
      'regex-bug': ['regex', '正则'],
      'permission': ['permission', '权限', 'denied', 'readonly'],
      'path-error': ['path', 'ENOENT', 'not found', '文件'],
      'git-conflict': ['git', 'conflict', 'MERGE'],
      'bash-syntax': ['syntax', 'shell', 'bash'],
      'hook-broken': ['hook', 'module', 'import'],
      'network-fail': ['network', 'connection', 'timeout'],
      'null-undefined': ['null', 'undefined'],
      'git-clean-fd': ['git clean', 'lf.*crlf', 'hook declined'],
    };
    const kwList = classKeywords[errorClass] || [errorClass];

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (!line.includes('### ') || line.includes('⚠️ INEFFECTIVE')) continue;
      // Check if this insight mentions the error class keywords
      const isMatch = kwList.some(kw => line.toLowerCase().includes(kw.toLowerCase()));
      if (isMatch) {
        lines[i] = line.replace(/\s*$/, '') + ' ⚠️ INEFFECTIVE (recurring error)';
        found = true;
        break; // Only mark the most recent one
      }
    }
    if (found) {
      writeFileSync(INSIGHTS_FILE, lines.join('\n'), 'utf-8');
      // Write flag for next session injection
      const effNote = eff
        ? `**已生成 ${eff.totalInsights} 条 insight，仍复发 ${eff.recurrencesAfterLast} 次** — 说明之前的 Fix 不够根本。`
        : '';
      const flag = `## ⚠️ Past Insight Ineffective: ${errorClass}

Error class **${errorClass}** has triggered ≥${RECURRENCE_THRESHOLD} times — the insight above may not be working.
请重新生成一个**更强力的修复**（不只是 tracking，要具体可执行的动作）。
若 Fix 已存在但仍复发，说明 Fix 不够根本，需要找到 root cause。
${effNote}
`;
      writeFileSync(RECURRENCE_FLAG_FILE, flag, 'utf-8');
    }
  } catch {}
}

function readState() {
  if (!existsSync(STATE_FILE)) return { count: 0, fired: false, sessionId: null };
  try { return JSON.parse(readFileSync(STATE_FILE, 'utf-8')); }
  catch { return { count: 0, fired: false, sessionId: null }; }
}

function writeState(state) {
  if (!existsSync(STATE_DIR)) mkdirSync(STATE_DIR, { recursive: true });
  writeFileSync(STATE_FILE, JSON.stringify(state, null, 2), 'utf-8');
}

function readPatterns() {
  if (!existsSync(PATTERN_FILE)) return { cmds: [], sessionId: null };
  try { return JSON.parse(readFileSync(PATTERN_FILE, 'utf-8')); }
  catch { return { cmds: [], sessionId: null }; }
}

function writePatterns(patterns) {
  writeFileSync(PATTERN_FILE, JSON.stringify(patterns, null, 2), 'utf-8');
}

function getCurrentSessionId(hookSessionId) {
  if (hookSessionId) return hookSessionId;
  if (process.env.OMC_SESSION_ID) return process.env.OMC_SESSION_ID;
  if (process.env.OMC_TRANSCRIPT_PATH) {
    const m = process.env.OMC_TRANSCRIPT_PATH.match(/([a-f0-9-]{36})\.jsonl$/);
    if (m) return m[1];
  }
  const transcriptsDir = 'C:/Users/adm/.claude/projects/D--OpenClaw-workspace';
  if (existsSync(transcriptsDir)) {
    try {
      const entries = readdirSync(transcriptsDir);
      let latest = null, latestMtime = 0;
      for (const e of entries) {
        if (!e.endsWith('.jsonl')) continue;
        const s = statSync(resolve(transcriptsDir, e));
        if (s.mtimeMs > latestMtime) { latestMtime = s.mtimeMs; latest = e; }
      }
      if (latest) {
        const m = latest.match(/^([a-f0-9-]+)\.jsonl$/);
        if (m) return m[1];
      }
    } catch {}
  }
  return Date.now().toString();
}

// Normalize command for pattern matching (remove timestamps, PIDs, paths)
function normalizeCmd(cmd) {
  return cmd
    .replace(/\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}/g, '<TS>')
    .replace(/\b\d{5,}\b/g, '<N>')
    .replace(/[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}/g, '<UUID>')
    .replace(/\/c\/Users\/[^\/]+/g, '<HOME>')
    .replace(/\/[^/\s]+(?:\/[^/\s]+){2,}/g, '<PATH>')
    .slice(0, 80);
}

// Normalize error message for pattern matching
function normalizeError(err) {
  if (!err) return '';
  return err
    .replace(/\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}/g, '<TS>')
    .replace(/\b\d{5,}\b/g, '<N>')
    .replace(/[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}/g, '<UUID>')
    .replace(/\/c\/Users\/[^\/]+/g, '<HOME>')
    .replace(/\/[^:\/\s]+:\d+/g, '<FILE:LINE>')
    .replace(/Error:\s*.+/, 'Error: <MSG>')
    .replace(/Exception in thread.+/, 'Exception: <THREAD>')
    .slice(0, 120);
}

const ERROR_PATTERN_FILE = resolve(STATE_DIR, 'auto-seed-errors.json');
const DEBUG_LOOP_FILE = resolve(STATE_DIR, 'auto-seed-debugloop.json');

function readErrorPatterns() {
  if (!existsSync(ERROR_PATTERN_FILE)) return { errors: [], sessionId: null };
  try { return JSON.parse(readFileSync(ERROR_PATTERN_FILE, 'utf-8')); }
  catch { return { errors: [], sessionId: null }; }
}

function writeErrorPatterns(p) { writeFileSync(ERROR_PATTERN_FILE, JSON.stringify(p), 'utf-8'); }

function readDebugLoop() {
  if (!existsSync(DEBUG_LOOP_FILE)) return { cycles: [], sessionId: null };
  try { return JSON.parse(readFileSync(DEBUG_LOOP_FILE, 'utf-8')); }
  catch { return { cycles: [], sessionId: null }; }
}

function writeDebugLoop(p) { writeFileSync(DEBUG_LOOP_FILE, JSON.stringify(p), 'utf-8'); }

// Detect git commit from bash commands in transcript
function detectGitCommit(sessionId) {
  const path = `C:/Users/adm/.claude/projects/D--OpenClaw-workspace/${sessionId}.jsonl`;
  if (!existsSync(path)) return null;
  try {
    const lines = readFileSync(path, 'utf-8').split('\n').filter(Boolean);
    for (const line of lines.slice(-50)) {
      try {
        const entry = JSON.parse(line);
        const content = entry.message?.content;
        if (!Array.isArray(content)) continue;
        for (const b of content) {
          if (b.type === 'tool_use' && b.name === 'Bash' && b.input?.command) {
            const cmd = b.input.command;
            if (/\bgit\s+(?:commit|push|add)\b/.test(cmd)) {
              const msg = cmd.match(/-m\s+["'](.+?)["']/)?.[1] || cmd.slice(0, 60);
              return { cmd: cmd.slice(0, 80), msg };
            }
          }
        }
      } catch {}
    }
  } catch {}
  return null;
}

// Detect repeated Bash errors in transcript (returns error pattern if repeated)
// Only count errors from NEW transcript lines since last call to avoid false positives
function detectErrorRepeat(sessionId) {
  const path = `C:/Users/adm/.claude/projects/D--OpenClaw-workspace/${sessionId}.jsonl`;
  if (!existsSync(path)) return null;
  const p = readErrorPatterns();
  const lastSeen = p.sessionId !== sessionId ? 0 : (p.lastSeen || 0);
  try {
    const lines = readFileSync(path, 'utf-8').split('\n').filter(Boolean);
    // Only scan new lines since last check
    const newLines = lines.slice(lastSeen);
    const newErrors = [];
    for (const line of newLines) {
      try {
        const entry = JSON.parse(line);
        const content = entry.message?.content;
        if (!Array.isArray(content)) continue;
        for (const b of content) {
          if (b.type === 'tool_use' && b.name === 'Bash' && b.output) {
            const out = b.output || '';
            if (/error|exception|failed|cannot|unable|not found/i.test(out)) {
              newErrors.push(normalizeError(out));
            }
          }
        }
      } catch {}
    }
    const prevErrors = p.sessionId === sessionId ? p.errors : [];
    const allErrs = [...prevErrors, ...newErrors];
    const freq = {};
    for (const e of allErrs) { if (e) freq[e] = (freq[e] || 0) + 1; }
    const repeated = Object.entries(freq).find(([, c]) => c >= ERROR_REPEAT_THRESHOLD);
    // Persist: errors from this scan + new errors, track line count
    writeErrorPatterns({ errors: [...prevErrors, ...newErrors].slice(-30), sessionId, lastSeen: lines.length });
    if (repeated) {
      const cls = classifyError(repeated[0]);
      const recurrence = checkRecurrence(cls, sessionId);
      // Flag past insight as ineffective if this class keeps recurring
      if (recurrence >= RECURRENCE_THRESHOLD) {
        const eff = getInsightEffectiveness(cls);
        markInsightIneffective(cls, eff);
      }
      return { pattern: repeated[0], count: repeated[1], cls, recurrence };
    }
  } catch {}
  return null;
}

// Detect Edit+Bash same-target debug loop (same file path cycled > N times)
// Only count cycles from NEW lines since last call
function detectDebugLoop(sessionId) {
  const path = `C:/Users/adm/.claude/projects/D--OpenClaw-workspace/${sessionId}.jsonl`;
  if (!existsSync(path)) return null;
  const p = readDebugLoop();
  const lastSeen = p.sessionId !== sessionId ? 0 : (p.lastSeen || 0);
  try {
    const lines = readFileSync(path, 'utf-8').split('\n').filter(Boolean);
    // Only scan new lines since last check
    const newLines = lines.slice(lastSeen);
    const edits = [];
    for (const line of newLines) {
      try {
        const entry = JSON.parse(line);
        const content = entry.message?.content;
        if (!Array.isArray(content)) continue;
        for (const b of content) {
          if (b.type === 'tool_use') {
            if (b.name === 'Edit' && b.input?.file_path) {
              edits.push({ file: b.input.file_path, type: 'edit' });
            } else if (b.name === 'Bash' && b.input?.command) {
              const f = b.input.command.match(/\s([^\s]+\.(js|ts|mjs|cjs|py|sh|json|md|yml|yaml|css|html))\s*$/)?.[1];
              if (f) edits.push({ file: f, type: 'bash' });
            }
          }
        }
      } catch {}
    }
    // Count edit→bash cycles on same target
    const cycles = [];
    for (let i = 1; i < edits.length; i++) {
      if (edits[i].type === 'bash' && edits[i - 1].type === 'edit' &&
          edits[i].file === edits[i - 1].file) {
        cycles.push(edits[i].file);
      }
    }
    const prevCycles = p.sessionId === sessionId ? p.cycles : [];
    const allCycles = [...prevCycles, ...cycles];
    const freq = {};
    for (const f of allCycles) { freq[f] = (freq[f] || 0) + 1; }
    const repeated = Object.entries(freq).find(([, c]) => c >= DEBUG_LOOP_THRESHOLD);
    writeDebugLoop({ cycles: allCycles.slice(-20), sessionId, lastSeen: lines.length });
    if (repeated) return { file: repeated[0], count: repeated[1] };
  } catch {}
  return null;
}

// Extract work output text from transcript (called ONLY when triggering)
function extractWorkOutput(sessionId, fromCount, toCount) {
  const path = `C:/Users/adm/.claude/projects/D--OpenClaw-workspace/${sessionId}.jsonl`;
  if (!existsSync(path)) return '';
  try {
    const allLines = readFileSync(path, 'utf-8').split('\n').filter(Boolean);
    const WINDOW = 200;
    const lines = allLines.slice(-WINDOW);
    const exchanges = [];
    let toolIdx = fromCount;
    for (const line of lines) {
      try {
        const entry = JSON.parse(line);
        const blocks = entry.message?.content;
        if (!Array.isArray(blocks)) continue;
        for (const b of blocks) {
          if (b.type === 'tool_use') toolIdx++;
          else if (b.type === 'text' && toolIdx > fromCount && toolIdx <= toCount) {
            const t = b.text.trim();
            if (t.length > 30) exchanges.push(t);
          }
        }
      } catch {}
    }
    return exchanges.slice(-3).join('\n---\n');
  } catch { return ''; }
}

// Read tool stats ONCE when threshold reached
function readLiveToolStats(sessionId) {
  const path = `C:/Users/adm/.claude/projects/D--OpenClaw-workspace/${sessionId}.jsonl`;
  if (!existsSync(path)) return null;
  try {
    const lines = readFileSync(path, 'utf-8').split('\n').filter(Boolean);
    const tools = { Bash: 0, Read: 0, Write: 0, Edit: 0, Grep: 0, TaskCreate: 0, TaskUpdate: 0 };
    const bashCommands = [];
    let toolCalls = 0;
    for (const line of lines) {
      try {
        const entry = JSON.parse(line);
        const content = entry.message?.content;
        if (!Array.isArray(content)) continue;
        for (const b of content) {
          if (b.type === 'tool_use' && b.name) {
            toolCalls++;
            for (const t of Object.keys(tools)) { if (b.name.includes(t)) tools[t]++; }
            if (b.name === 'Bash' && b.input?.command) {
              bashCommands.push(b.input.command.slice(0, 80));
            }
          }
        }
      } catch {}
    }
    const selfScripts = ['hook-stats.mjs', 'omc-insight-action.mjs', 'omc-insight-generator.mjs', 'hook-audit-log-mcp.mjs'];
    const topBash = [...new Set(bashCommands)]
      .filter(c => !selfScripts.some(s => c.includes(s)))
      .slice(0, 5);
    return { tools, totalToolCalls: toolCalls, topBash };
  } catch { return null; }
}

function appendIdea(line) {
  mkdirSync(dirname(IDEAS_FILE), { recursive: true });
  appendFileSync(IDEAS_FILE, line + '\n', 'utf-8');
}

function writeTrigger(sessionId, count, toolStats, workOutput, activePattern, errorClass, recurrence) {
  // Extract error class from activePattern like "error-repeat:regex-bug ⚠️ RECURRING:regex-bug×3"
  let errCls = errorClass || null;
  let recurCount = recurrence || 0;
  if (activePattern?.startsWith('error-repeat:')) {
    const match = activePattern.match(/error-repeat:(\S+)/);
    if (match) errCls = match[1];
    const recurMatch = activePattern.match(/RECURRING:(\S+)×(\d+)/);
    if (recurMatch) { errCls = recurMatch[1]; recurCount = parseInt(recurMatch[2]); }
  }
  const trigger = {
    sessionId,
    count,
    threshold: THRESHOLD,
    toolStats,
    workOutput: workOutput || null,
    activePattern: activePattern || null,
    errorClass: errCls,
    recurrence: recurCount,
    triggeredAt: new Date().toISOString(),
  };
  writeFileSync(TRIGGER_FILE, JSON.stringify(trigger, null, 2), 'utf-8');

  const nudgeLine = activePattern
    ? `⚡ ACTIVE LEARN: "${activePattern}" repeated ${PATTERN_REPEAT}x — generate reusable script: .omc/state/session-insights.md`
    : `⚡ INSIGHT TRIGGER: ${count} tool calls (threshold ${THRESHOLD}) — generate insight: .omc/state/session-insights.md`;
  appendFileSync(NUDGE_FILE, nudgeLine + '\n', 'utf-8');

  const priorityLine = activePattern
    ? `⚡ ACTIVE LEARN: "${activePattern}" repeated ${PATTERN_REPEAT}x — generate reusable script from work output | Read trigger: .omc/state/auto-insight-trigger.json`
    : `⚡ INSIGHT TRIGGER: ${count} tool calls (threshold ${THRESHOLD}) — generate insight from work output | Read trigger: .omc/state/auto-insight-trigger.json`;

  let notepad = existsSync(NOTPAD_FILE) ? readFileSync(NOTPAD_FILE, 'utf-8') : '';
  const lines = notepad.split('\n');
  const priorityIdx = lines.findIndex(l => l.startsWith('## Priority Context'));
  if (priorityIdx === -1) return;

  const triggerIdx = lines.findIndex(l => l.includes('INSIGHT TRIGGER') || l.includes('ACTIVE LEARN'));
  if (triggerIdx !== -1) lines[triggerIdx] = priorityLine;
  else {
    const insertIdx = lines.findIndex((l, i) => i > priorityIdx && l.startsWith('##'));
    if (insertIdx === -1) lines.push(priorityLine);
    else lines.splice(insertIdx, 0, priorityLine);
  }
  writeFileSync(NOTPAD_FILE, lines.join('\n'), 'utf-8');

  const today = new Date().toLocaleDateString('en-CA');
  if (activePattern) {
    const entry = `- [${today}] STAGE [AUTO:active-learn] [score:4×4=16] [f:4] 主动学习:${activePattern} | benefit: 3次重复命令生成复用脚本 | reason: 重复执行本身就是可复用信号 | approach: 提取repeated command生成script | AUTO:${Date.now()}`;
    appendIdea(entry);
  } else {
    const entry = `- [${today}] STAGE [AUTO:insight] [score:3×4=12] [f:4] 被动insight生成 | benefit: 工具调用达阈值触发insight | reason: 工具调用已达${count}次 | approach: hook触发→AI生成→session-insights.md→step7执行 | AUTO:${Date.now()}`;
    appendIdea(entry);
  }

  return activePattern
    ? `AUTO:active-learn triggered: "${activePattern}"`
    : `AUTO:insight-spawned (totalCalls:${count})`;
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

async function main() {
  const args = parseArgs(process.argv.slice(2));

  let hookSessionId = null;
  if (args.session) hookSessionId = args.session;
  if (!hookSessionId) {
    try {
      const stdin = await readStdin();
      if (stdin?.trim()) {
        const event = JSON.parse(stdin);
        if (event.session_id) hookSessionId = event.session_id;
      }
    } catch {}
  }

  const currentSession = getCurrentSessionId(hookSessionId);
  const state = readState();
  const sameSession = state.sessionId === currentSession;

  // --reset
  if (args.reset) {
    writeState({ count: 0, fired: false, sessionId: currentSession });
    writePatterns({ cmds: [], sessionId: currentSession });
    if (existsSync(TRIGGER_FILE)) writeFileSync(TRIGGER_FILE, '', 'utf-8'); // clear stale trigger
    if (existsSync(ACTIVE_LEARN_FILE)) writeFileSync(ACTIVE_LEARN_FILE, '', 'utf-8'); // clear active-learn
    writeFileSync(ERROR_PATTERN_FILE, JSON.stringify({ errors: [], sessionId: currentSession }), 'utf-8');
    writeFileSync(DEBUG_LOOP_FILE, JSON.stringify({ cycles: [], sessionId: currentSession }), 'utf-8');
    console.log('counter + patterns reset');
    return;
  }

  // --active: track command patterns, trigger on 3x repetition
  if (args.active) {
    if (!sameSession) {
      writeState({ count: 0, fired: false, sessionId: currentSession });
      writePatterns({ cmds: [], sessionId: currentSession });
      if (existsSync(TRIGGER_FILE)) writeFileSync(TRIGGER_FILE, '', 'utf-8'); // clear stale trigger
      if (existsSync(ACTIVE_LEARN_FILE)) writeFileSync(ACTIVE_LEARN_FILE, '', 'utf-8'); // clear active-learn
      writeFileSync(ERROR_PATTERN_FILE, JSON.stringify({ errors: [], sessionId: currentSession }), 'utf-8');
      writeFileSync(DEBUG_LOOP_FILE, JSON.stringify({ cycles: [], sessionId: currentSession }), 'utf-8');
    }
    const cmd = args.cmd || '';
    if (!cmd) return;
    const norm = normalizeCmd(cmd);
    const patterns = readPatterns();
    const cmds = patterns.sessionId === currentSession ? patterns.cmds : [];
    cmds.push(norm);
    const recentCmds = cmds.slice(-PATTERN_WINDOW);
    writePatterns({ cmds: recentCmds, sessionId: currentSession });
    // Count occurrences of each unique command in window
    const freq = {};
    for (const c of recentCmds) { freq[c] = (freq[c] || 0) + 1; }
    for (const [pattern, count] of Object.entries(freq)) {
      if (count >= PATTERN_REPEAT) {
        const workOutput = extractWorkOutput(currentSession, 0, 99999);
        const msg = writeTrigger(currentSession, count, null, workOutput, pattern, null, 0);
        console.log(msg);
        return;
      }
    }
    return;
  }

  // --check: fast counter mode (NO transcript read unless threshold reached)
  if (args.check) {
    if (!sameSession) {
      writeState({ count: 0, fired: false, sessionId: currentSession });
      writePatterns({ cmds: [], sessionId: currentSession });
      if (existsSync(TRIGGER_FILE)) writeFileSync(TRIGGER_FILE, '', 'utf-8'); // clear stale trigger
      if (existsSync(ACTIVE_LEARN_FILE)) writeFileSync(ACTIVE_LEARN_FILE, '', 'utf-8'); // clear active-learn
      writeFileSync(ERROR_PATTERN_FILE, JSON.stringify({ errors: [], sessionId: currentSession }), 'utf-8');
      writeFileSync(DEBUG_LOOP_FILE, JSON.stringify({ cycles: [], sessionId: currentSession }), 'utf-8');
    }
    const freshState = readState();
    const newCount = freshState.count + 1;
    writeState({ ...freshState, count: newCount });

    // Enhanced proactive triggers: check git commits, error repeats, debug loops
    if (!freshState.fired) {
      // 1. Git commit → "good work" insight (highest priority, no threshold needed)
      const gitCommit = detectGitCommit(currentSession);
      if (gitCommit) {
        writeState({ ...freshState, count: newCount, fired: true });
        const msg = writeTrigger(currentSession, newCount, null, `git commit: ${gitCommit.msg}`, `git:${gitCommit.cmd.slice(0, 40)}`, null, 0);
        console.log(msg);
        return;
      }

      // 2. Error repeat → insight about avoiding the error
      const errRepeat = detectErrorRepeat(currentSession);
      if (errRepeat) {
        writeState({ ...freshState, count: newCount, fired: true });
        const toolStats = readLiveToolStats(currentSession);
        const workOutput = extractWorkOutput(currentSession, 0, newCount);
        const recurrenceNote = errRepeat.recurrence >= RECURRENCE_THRESHOLD
          ? ` ⚠️ RECURRING:${errRepeat.cls}×${errRepeat.recurrence}` : '';
        const msg = writeTrigger(currentSession, newCount, toolStats, workOutput, `error-repeat:${errRepeat.cls}${recurrenceNote}`, errRepeat.cls, errRepeat.recurrence);
        console.log(msg);
        return;
      }

      // 3. Debug loop → insight about fixing the pattern
      const debugLoop = detectDebugLoop(currentSession);
      if (debugLoop) {
        writeState({ ...freshState, count: newCount, fired: true });
        const toolStats = readLiveToolStats(currentSession);
        const workOutput = extractWorkOutput(currentSession, 0, newCount);
        const msg = writeTrigger(currentSession, newCount, toolStats, workOutput, `debug-loop:${debugLoop.file}`, null, 0);
        console.log(msg);
        return;
      }
    }

    if (newCount >= THRESHOLD && !freshState.fired) {
      writeState({ ...freshState, count: newCount, fired: true });
      const toolStats = readLiveToolStats(currentSession);
      const workOutput = extractWorkOutput(currentSession, 0, newCount);
      const msg = writeTrigger(currentSession, newCount, toolStats, workOutput, null, null, 0);
      console.log(msg);
    } else {
      console.log(`count:${newCount}/${THRESHOLD}`);
    }
    return;
  }

  // Default: status
  const st = readState();
  const pt = readPatterns();
  console.log(`OMC Auto-Seed Status`);
  console.log(`  Count: ${st.count}/${THRESHOLD}`);
  console.log(`  Fired: ${st.fired}`);
  console.log(`  Session: ${st.sessionId || 'none'}`);
  console.log(`  Active patterns: ${pt.cmds?.length || 0}`);
  console.log(`\nUsage:`);
  console.log(`  --check        Fast counter (no transcript read)`);
  console.log(`  --active --cmd "..."  Track command pattern, trigger on 3x repeat`);
  console.log(`  --reset        Reset for new session`);
}

main().catch(e => { console.error(e.message); process.exit(1); });
