#!/usr/bin/env node
/**
 * OMC Session End Drain
 * Multi-step automation on session end:
 *   Step 1: MCP queue drain → session-start injection
 *   Step 2: Auto-apply dangerous rules (hook-self-improve --auto-apply)
 *   Step 3: Workflow detector if ≥10 new audit entries
 *   Step 4: Trajectory compressor — extract learnings from transcript → .omc/trajectories/
 *   Step 5: Honcho-lite — session summary → MEMORY.md Session History
 */
import { existsSync, readFileSync, writeFileSync, appendFileSync, unlinkSync, mkdirSync, statSync } from 'fs';
import { spawn } from 'child_process';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const STATE_DIR = resolve(__dirname, '../state');
const QUEUE_FILE = resolve(STATE_DIR, 'mcp-learn-queue.jsonl');
const DRAIN_FILE = resolve(STATE_DIR, 'session-start-mcp-inject.md');
const PATTERNS_FILE = resolve(STATE_DIR, 'agentdb-patterns.jsonl');
const WF_STATE = resolve(STATE_DIR, 'workflow-detector-state.json');
const TRAJ_DIR = resolve(STATE_DIR, '../trajectories');
// SessionStart/End hooks inject paths via env vars
// On Windows, hooks run from cwd D:\OpenClaw\workspace but __dirname may differ
// Use absolute paths as primary, env vars as override
const _TRANSCRIPT_BASE = process.env.OMC_TRANSCRIPT_BASE || 'C:/Users/adm/.claude/projects/D--OpenClaw-workspace';
const _MEMORY_BASE = process.env.OMC_MEMORY_BASE || 'C:/Users/adm/.claude/projects/D--OpenClaw-workspace/memory';

function log(...args) { console.log('[drain]', ...args); }

// ── Helpers ─────────────────────────────────────────────────────────────────
function readQueue() {
  if (!existsSync(QUEUE_FILE)) return [];
  return readFileSync(QUEUE_FILE, 'utf-8')
    .split('\n').filter(Boolean)
    .map(l => { try { return JSON.parse(l); } catch { return null; } })
    .filter(Boolean);
}

function writePatternDirect(entry) {
  // Bypass broken MCP → write directly to agentdb-patterns.jsonl
  const id = `${entry.patternType || 'unknown'}-${entry.pattern}-${Date.now()}`;
  const record = { id, ...entry, storedAt: new Date().toISOString() };
  appendFileSync(PATTERNS_FILE, JSON.stringify(record) + '\n', 'utf-8');
}

function readAuditCount() {
  const log = resolve(STATE_DIR, 'hook-audit.jsonl');
  if (!existsSync(log)) return 0;
  try {
    const content = readFileSync(log, 'utf-8');
    return content.split('\n').filter(Boolean).length;
  } catch { return 0; }
}

function readWfState() {
  if (!existsSync(WF_STATE)) return { lastEmitCount: 0 };
  try { return JSON.parse(readFileSync(WF_STATE, 'utf-8')); }
  catch { return { lastEmitCount: 0 }; }
}

function writeWfState(state) {
  writeFileSync(WF_STATE, JSON.stringify(state, null, 2), 'utf-8');
}

function ensureDir(p) {
  if (!existsSync(p)) mkdirSync(p, { recursive: true });
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

// ── Step 1: MCP drain → inject ───────────────────────────────────────────────
function buildInjectMarkdown(entries, sessionId) {
  const patterns = entries.filter(e => e.type === 'agentdb_pattern-store');
  const feedbacks = entries.filter(e => e.type === 'agentdb_feedback');
  const postCommands = entries.filter(e => e.type === 'hooks_post-command');

  let md = `## OMC Learning Log

Patterns and feedback are now written directly to agentdb-patterns.jsonl (MCP tool unavailable).
These patterns are available for semantic search via \`memory_search\` in future sessions.

`;
  return md;
}

function step1_drain(entries, sessionId) {
  // Build hook status summary for transparency
  const auditLog = resolve(STATE_DIR, 'hook-audit.jsonl');
  let hookSummary = '';
  if (existsSync(auditLog)) {
    try {
      const content2 = readFileSync(auditLog, 'utf-8');
      const lines = content2.split('\n').filter(Boolean);
      const today = new Date().toISOString().split('T')[0];
      const todayLines = lines.filter(l => {
        try { return JSON.parse(l).timestamp?.startsWith(today); } catch { return false; }
      });
      const tools = {};
      for (const l of todayLines) {
        try { const e = JSON.parse(l); tools[e.tool] = (tools[e.tool]||0) + 1; } catch {}
      }
      const dedupFile = resolve(STATE_DIR, 'hook-last-cmd.json');
      const dedup = existsSync(dedupFile) ? JSON.parse(readFileSync(dedupFile, 'utf-8')) : null;
      hookSummary = '\n## Hook Status\n\n';
      hookSummary += '- Audit entries today: ' + todayLines.length + '\n';
      hookSummary += '- Tools: ' + Object.entries(tools).map(([t,c])=>t+'('+c+')').join(', ') + '\n';
      hookSummary += '- Last dedup: ' + (dedup ? '"' + dedup.cmd + '" x' + dedup.count : 'none') + '\n';
      hookSummary += '- Queue entries: ' + entries.length + '\n';
    } catch {}
  }

  // Read recent patterns from agentdb-patterns.jsonl (written by step4 this session)
  let patternSummary = '';
  if (existsSync(PATTERNS_FILE)) {
    try {
      const pLines = readFileSync(PATTERNS_FILE, 'utf-8').split('\n').filter(Boolean);
      const recent = pLines.slice(-5);
      if (recent.length > 0) {
        const parsed = recent.map(l => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);
        const summaries = parsed.map(p => {
          const type = p.patternType || 'unknown';
          const pat = p.pattern || '';
          // Pattern string starts with "[type]" — strip it to avoid display duplication
          const bracketPat = '[' + type + '] ';
          const clean = pat.startsWith(bracketPat) ? pat.slice(bracketPat.length) : pat;
          return '- [' + type + '] ' + clean.slice(0, 80) + (clean.length > 80 ? '...' : '');
        });
        patternSummary = '\n## Recent Learned Patterns\n\n' + summaries.join('\n') + '\n';
      }
    } catch {}
  }

  const md = buildInjectMarkdown(entries, sessionId);
  if (!md && !hookSummary && !patternSummary) {
    if (existsSync(DRAIN_FILE)) { try { unlinkSync(DRAIN_FILE); } catch {} }
    log('step1: queue-empty');
    return;
  }
  writeFileSync(DRAIN_FILE, md + patternSummary + hookSummary, 'utf-8');
  writeFileSync(QUEUE_FILE, '', 'utf-8');
  log('step1: ' + entries.length + ' entries drained -> next session');
}

// ── Step 2: Self-improve ───────────────────────────────────────────────────
function step2_selfImprove() {
  return new Promise((resolve) => {
    const script = resolve(__dirname, 'hook-self-improve.mjs');
    const proc = spawn(process.execPath, [script, '--auto-apply'], {
      stdio: ['ignore', 'pipe', 'pipe'],
      cwd: __dirname, windowsHide: true,
    });
    let out = '';
    proc.stdout.on('data', (d) => { out += d.toString(); });
    proc.on('close', () => resolve(out.slice(0, 800)));
    proc.on('error', () => resolve(''));
  });
}

// ── Step 3: Workflow detector ──────────────────────────────────────────────
function step3_workflowDetector(auditCount) {
  const wfState = readWfState();
  const newEntries = auditCount - wfState.lastEmitCount;
  if (newEntries < 10) {
    log(`step3: wf-skip (${newEntries} new < 10)`);
    return Promise.resolve();
  }
  return new Promise((resolve) => {
    const script = resolve(__dirname, 'hook-workflow-detector.mjs');
    const proc = spawn(process.execPath, [script, '--emit', '--min-count=3'], {
      stdio: ['ignore', 'pipe', 'pipe'], cwd: __dirname, windowsHide: true,
    });
    let out = '';
    proc.stdout.on('data', (d) => { out += d.toString(); });
    proc.on('close', () => {
      writeWfState({ lastEmitCount: auditCount, lastSessionId: process.env.OMC_SESSION_ID || null });
      log(`step3: wf-emit (${newEntries} new entries)`);
      resolve(out.slice(0, 300));
    });
    proc.on('error', () => resolve(''));
  });
}

// ── Step 4: Trajectory compressor ───────────────────────────────────────────
async function step4_trajectory() {
  // Find the most recent transcript file
  const projectsDir = _TRANSCRIPT_BASE;
  let transcriptPath = null;
  let latestMtime = 0;

  try {
    if (!existsSync(projectsDir)) { log(`step4: projects dir not found: ${projectsDir}`); return; }
    const { readdirSync, statSync: st } = await import('fs');
    const files = readdirSync(projectsDir).filter(f => f.endsWith('.jsonl'));
    if (files.length === 0) { log('step4: no jsonl files found'); return; }
    for (const f of files) {
      const p = resolve(projectsDir, f);
      try {
        const s = st(p);
        if (s.mtimeMs > latestMtime) {
          latestMtime = s.mtimeMs;
          transcriptPath = p;
        }
      } catch {}
    }
    if (transcriptPath) log(`step4: found transcript ${transcriptPath}`);
  } catch (e) { log(`step4: error: ${e.message}`); return; }

  if (!transcriptPath) {
    log('step4: no transcript found');
    return;
  }

  const MAX_LINES = 200; // Only read last N lines (recent session)
  const content = readFileSync(transcriptPath, 'utf-8');
  const lines = content.split('\n').filter(Boolean).slice(-MAX_LINES);

  const events = lines.map(l => {
    try { return JSON.parse(l); } catch { return null; }
  }).filter(Boolean);

  // Extract tool calls
  const toolCalls = [];
  for (const e of events) {
    if (e.type !== 'assistant') continue;
    const raw = e.message?.content;
    // Modern format: content is array of blocks with type: 'tool_use'
    if (Array.isArray(raw)) {
      for (const block of raw) {
        if (block?.type === 'tool_use' && block?.name) {
          toolCalls.push({ tool: block.name, ts: e.timestamp });
        }
      }
      continue;
    }
    // Legacy format: content is string — look for tool references
    const text = String(raw || '');
    if (!text) continue;
    const toolUseMatch = text.match(/using tools?:?\s*([A-Z][a-zA-Z]+)/g);
    if (toolUseMatch) {
      for (const m of toolUseMatch) {
        const tool = m.replace(/using tools?:?\s*/i, '').trim();
        if (tool) toolCalls.push({ tool, ts: e.timestamp });
      }
    }
  }

  // Count unique tools
  const toolCounts = {};
  for (const tc of toolCalls) {
    toolCounts[tc.tool] = (toolCounts[tc.tool] || 0) + 1;
  }
  const topTools = Object.entries(toolCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([t, c]) => `${t}(${c})`);

  // Extract user prompts
  const userPrompts = [];
  for (const e of events) {
    if (e.type === 'user' && e.message?.content) {
      const raw = e.message.content;
      const text = Array.isArray(raw)
        ? (raw.find(i => i.type === 'text')?.text || '')
        : String(raw || '');
      const short = text.trim().slice(0, 200);
      if (short && !short.startsWith('{')) {
        userPrompts.push(short);
      }
    }
  }
  const recentPrompt = userPrompts[userPrompts.length - 1] || '';
  const firstPrompt = userPrompts[0] || '';

  // Extract seeds suggested
  const seeds = [];
  for (const e of events) {
    if (e.type === 'assistant' && e.message?.content) {
      const raw = e.message.content;
      const text = Array.isArray(raw)
        ? (raw.find(i => i.type === 'text')?.text || '')
        : String(raw || '');
      if (!text) continue;
      const seedMatch = text.match(/STAGE\s*\[([^\]]+)\]\s*\[score:(\d+)[×x](\d+)/g);
      if (seedMatch) {
        for (const m of seedMatch) {
          const src = m.match(/STAGE\[([^\]]+)/)?.[1] || 'unknown';
          const score = m.match(/score:(\d+)[×x](\d+)/)?.[0] || '';
          seeds.push(`${src} ${score}`);
        }
      }
    }
  }

  const today = new Date().toISOString().split('T')[0];
  const sessionId = process.env.OMC_SESSION_ID || 'unknown';

  ensureDir(TRAJ_DIR);
  const trajFile = resolve(TRAJ_DIR, `${today}-${sessionId.slice(0, 8)}.md`);

  let md = `# Session Trajectory\n\n`;
  md += `**Date**: ${today}  \n`;
  md += `**Session**: ${sessionId}  \n`;
  md += `**Events**: ${events.length} (last ${MAX_LINES} of transcript)  \n\n`;

  md += `## Top Tools Used\n\n`;
  if (topTools.length > 0) {
    md += topTools.map(t => `- ${t}`).join('\n') + '\n\n';
  } else {
    md += `(no tool data extracted)\n\n`;
  }

  md += `## Session Topics (first & last user prompts)\n\n`;
  md += `- **Start**: ${firstPrompt.slice(0, 120)}\n`;
  md += `- **End**: ${recentPrompt.slice(0, 120)}\n\n`;

  if (seeds.length > 0) {
    md += `## Seeds Mentioned\n\n`;
    md += seeds.slice(0, 10).map(s => `- ${s}`).join('\n') + '\n\n';
  }

  md += `## Patterns Detected\n\n`;
  const patterns = [];
  const bashCount = toolCalls.filter(t => t.tool === 'Bash').length;
  const readCount = toolCalls.filter(t => t.tool === 'Read').length;
  const editCount = toolCalls.filter(t => t.tool === 'Edit').length;
  if (bashCount > 3) patterns.push('heavy bash usage');
  if (seeds.length > 5) patterns.push('idea generation active');
  if (readCount > editCount * 2) patterns.push('read-heavy workflow');
  // Insight #7: detect debugging mode (high Bash+Read+Edit, no seeds)
  if (bashCount > 30 && readCount > 20 && editCount > 10 && seeds.length === 0) {
    patterns.push('debugging mode (fixing, not creating)');
  }
  if (patterns.length > 0) {
    md += patterns.map(p => `- ${p}`).join('\n') + '\n\n';
  } else {
    md += `(no specific patterns)\n\n`;
  }

  md += `## Summary\n\n`;
  md += `${events.length} events, ${toolCalls.length} tool calls, ${userPrompts.length} user prompts, ${seeds.length} seeds.\n`;
  md += `Top tools: ${topTools.join(', ') || 'none'}.\n`;

  writeFileSync(trajFile, md, 'utf-8');
  log(`step4: trajectory → ${trajFile}`);

  // Extract patterns → queue MCP pattern-store
  const now = new Date().toISOString();
  const mcpPatterns = [];
  if (topTools.length > 0) {
    mcpPatterns.push({
      type: 'agentdb_pattern-store',
      pattern: `[workflow] top tools: ${topTools.join(', ')}`,
      patternType: 'workflow',
      confidence: 0.7,
      metadata: { sessionId, date: today, toolCount: toolCalls.length },
    });
  }
  for (const p of patterns) {
    mcpPatterns.push({
      type: 'agentdb_pattern-store',
      pattern: `[session-pattern] ${p}`,
      patternType: 'session-pattern',
      confidence: 0.6,
      metadata: { sessionId, date: today },
    });
  }
  if (seeds.length > 0) {
    mcpPatterns.push({
      type: 'agentdb_pattern-store',
      pattern: `[seeds] ${seeds.length} seeds generated`,
      patternType: 'idea-generation',
      confidence: 0.7,
      metadata: { sessionId, date: today, seedCount: seeds.length },
    });
  }
  if (toolCalls.length > 20) {
    mcpPatterns.push({
      type: 'agentdb_pattern-store',
      pattern: `[efficiency] high tool-call session (${toolCalls.length} calls)`,
      patternType: 'session-efficiency',
      confidence: 0.6,
      metadata: { sessionId, date: today, callCount: toolCalls.length },
    });
  }
  // Write directly to agentdb-patterns.jsonl (bypass broken MCP tool)
  for (const entry of mcpPatterns) {
    writePatternDirect(entry);
  }
  if (mcpPatterns.length > 0) {
    log(`step4: ${mcpPatterns.length} patterns written to agentdb-patterns.jsonl`);
  }
}

// ── Step 5: Honcho-lite — session summary to MEMORY.md ──────────────────────
function step5_honchoLite() {
  const MEMORY_PATH = resolve(_MEMORY_BASE, 'MEMORY.md');
  if (!existsSync(MEMORY_PATH)) {
    log('step5: MEMORY.md not found, skipping');
    return;
  }

  const sessionId = process.env.OMC_SESSION_ID || 'unknown';
  const today = new Date().toISOString().split('T')[0];

  // Count audit entries for this session
  const auditLog = resolve(STATE_DIR, 'hook-audit.jsonl');
  let toolCount = 0;
  let errorCount = 0;
  let bashCount = 0;
  let topCmd = '';

  if (existsSync(auditLog)) {
    try {
      const content = readFileSync(auditLog, 'utf-8');
      const lines = content.split('\n').filter(Boolean);
      // Approximate: count entries from today
      const todayLines = lines.filter(l => {
        try { return JSON.parse(l).timestamp?.startsWith(today); } catch { return false; }
      });
      toolCount = todayLines.length;
      errorCount = todayLines.filter(l => {
        try { const e = JSON.parse(l); return e.error || (e.exitCode !== null && e.exitCode !== 0); } catch { return false; }
      }).length;
      const bashLines = todayLines.filter(l => {
        try { return JSON.parse(l).tool === 'Bash'; } catch { return false; }
      });
      bashCount = bashLines.length;
      if (bashLines.length > 0) {
        const last = bashLines[bashLines.length - 1];
        try { topCmd = JSON.parse(last).tool_input_preview?.slice(0, 50) || ''; } catch {}
      }
    } catch {}
  }

  // Check for seeds shipped today
  const IDEAS_PATH = resolve(__dirname, '../innovation/ideas.md');
  let shippedToday = 0;
  if (existsSync(IDEAS_PATH)) {
    try {
      const content = readFileSync(IDEAS_PATH, 'utf-8');
      const lines = content.split('\n');
      shippedToday = lines.filter(l => l.includes(`shipped:${today}`)).length;
    } catch {}
  }

  // Generate summary row
  const summary = `| ${today} | ${sessionId.slice(0, 8)}… | tools:${toolCount} err:${errorCount} bash:${bashCount} seeds-shipped:${shippedToday} |`;

  // Append to Session History table
  try {
    let content = readFileSync(MEMORY_PATH, 'utf-8');
    const marker = '## Session History';
    const markerIdx = content.indexOf(marker);

    if (markerIdx === -1) {
      log('step5: no Session History table in MEMORY.md, skipping');
      return;
    }

    // Find end of table (first ## after Session History)
    const afterMarker = content.slice(markerIdx);
    const nextSection = afterMarker.indexOf('\n## ');
    const tableEnd = markerIdx + (nextSection > 0 ? nextSection : content.length);

    // Find last | row in table
    const tableContent = content.slice(markerIdx, tableEnd);
    const rows = tableContent.split('\n');
    let lastRowIdx = -1;
    for (let i = rows.length - 1; i >= 0; i--) {
      if (rows[i].startsWith('|')) {
        lastRowIdx = i;
        break;
      }
    }

    if (lastRowIdx < 0) {
      log('step5: could not find table rows, skipping');
      return;
    }

    // Check if today's row already exists
    if (content.includes(`| ${today} |`)) {
      log(`step5: today already in Session History`);
      return;
    }

    // Insert new row after lastRowIdx
    const newContent = content.slice(0, markerIdx + rows.slice(0, lastRowIdx + 1).join('\n').length + 1)
      + '\n' + summary
      + content.slice(markerIdx + rows.slice(0, lastRowIdx + 1).join('\n').length + 1);

    writeFileSync(MEMORY_PATH, newContent, 'utf-8');
    log(`step5: appended to MEMORY.md Session History`);
  } catch (e) {
    log(`step5: failed: ${e.message}`);
  }
}

// ── Cleanup ────────────────────────────────────────────────────────────────
function cleanup(sessionIdHint) {
  if (!existsSync(DRAIN_FILE)) { log('cleanup: no-drain-file'); return; }
  try {
    const content = readFileSync(DRAIN_FILE, 'utf-8');
    if (sessionIdHint && content.includes(sessionIdHint)) {
      unlinkSync(DRAIN_FILE);
      log(`cleanup: deleted drain file`);
    } else {
      const stat = statSync(DRAIN_FILE);
      const age = Date.now() - stat.mtimeMs;
      if (age > 60 * 60 * 1000) {
        unlinkSync(DRAIN_FILE);
        log(`cleanup: deleted stale drain (${Math.round(age / 60000)}min old)`);
      }
    }
  } catch {}
}

// ── Step 6: Auto-generate insights from trajectory ──────────────────────────
async function step6_insightGenerator() {
  // Detect high-Bash sessions → inject urgency prompt to force actionable Fix
  const trajFile = resolve(__dirname, '../trajectories/' + new Date().toISOString().split('T')[0] + '-unknown.md');
  let extraPrompt = '';
  if (existsSync(trajFile)) {
    try {
      const content = readFileSync(trajFile, 'utf-8');
      const bashMatch = content.match(/Bash\((\d+)\)/);
      const totalMatch = content.match(/(\d+)\s+tool\s+calls/);
      if (bashMatch && totalMatch) {
        const bash = parseInt(bashMatch[1]);
        const total = parseInt(totalMatch[1]);
        if (total > 20 && bash / total > 0.4) {
          log('step6: high-Bash detected (Bash=' + bash + '/total=' + total + '), using urgency prompt');
          extraPrompt = '\n\n[URGENT] This session has Bash ratio ' + Math.round(bash/total*100) + '%. Bash-heavy sessions tend to produce only monitoring rules. You MUST产出 one specific executable Fix — not a tracking rule, not "N/A". If no clear fix exists, invent a minimal one (e.g. "Add Bash:total ratio log to trajectory").';
        }
      }
    } catch {}
  }

  return new Promise((resolve) => {
    const script = resolve(__dirname, 'omc-insight-generator.mjs');
    const proc = spawn(process.execPath, [script], {
      stdio: ['ignore', 'pipe', 'pipe'],
      cwd: __dirname, windowsHide: true,
      env: { ...process.env, OMC_INSIGHT_EXTRA_PROMPT: extraPrompt },
    });
    let out = '';
    proc.stdout.on('data', d => { out += d.toString(); });
    proc.on('close', () => {
      if (out.trim()) log('step6: ' + out.trim().replace(/\n/g, ' ').slice(0, 120));
      resolve();
    });
    proc.on('error', () => resolve());
  });
}

// ── Step 7: Execute pending actions immediately ─────────────────────────────
function step7_executePendingActions() {
  const PENDING = resolve(__dirname, '../state/pending-actions.md');
  if (!existsSync(PENDING)) return;

  let content;
  try { content = readFileSync(PENDING, 'utf-8'); } catch { return; }

  const lines = content.split('\n').filter(l => l.startsWith('- [ ]'));
  if (lines.length === 0) return;

  const PENDING_FILE = PENDING;
  const VERIFY_FILE = resolve(__dirname, '../state/insight-verifications.md');
  const INSIGHTS_FILE = resolve(__dirname, '../state/session-insights.md');

  function markExecuted(desc) {
    if (!existsSync(INSIGHTS_FILE)) return;
    let c = readFileSync(INSIGHTS_FILE, 'utf-8');
    const ls = c.split('\n');
    for (let i = 0; i < ls.length; i++) {
      if (ls[i].includes('### ') && ls[i].includes(desc.slice(0, 40))) {
        if (ls[i].includes('✅ EXECUTED')) break;
        ls[i] = ls[i].replace(/\s*$/, '') + ' ✅ EXECUTED';
        writeFileSync(INSIGHTS_FILE, ls.join('\n'), 'utf-8');
        break;
      }
    }
  }

  function verifyAction(id, result) {
    const record = { id, result, verifiedAt: new Date().toISOString() };
    const existing = existsSync(VERIFY_FILE) ? readFileSync(VERIFY_FILE, 'utf-8') : '';
    writeFileSync(VERIFY_FILE, existing + `## ${id}\n\n- **Result**: ${result}\n- **Verified**: ${record.verifiedAt}\n\n`, 'utf-8');
  }

  for (const line of lines) {
    const match = line.match(/^\- \[ \] (.*?) \| action: (.+?) \| id: (\S+)/);
    if (!match) continue;
    const [, desc, action, id] = match;
    // Shell commands: execute via spawn; code modifications: call patcher
    const isShellCmd = action.includes('node ') || action.includes('npm ') || action.includes('git ') || action.includes('python') || action.includes('pip ');
    if (isShellCmd) {
      log(`step7: executing [${id}] ${desc.slice(0, 60)}`);
      log(`        cmd: ${action.slice(0, 80)}`);
      const child = spawn(action, [], { shell: true, cwd: __dirname + '/../../..' });
      let err = '';
      child.stderr.on('data', d => { err += d.toString(); });
      child.on('close', (code) => {
        if (code !== 0) { log(`step7: action failed (${code}): ${err.slice(0, 120)}`); verifyAction(id, `failed:${code}`); }
        else { log(`step7: action succeeded`); verifyAction(id, 'executed'); }
        markExecuted(desc);
      });
      child.on('error', e => { log(`step7: spawn error: ${e.message}`); verifyAction(id, `error:${e.message}`); });
    } else {
      log(`step7: code mod — calling patcher for [${id}]: ${action.slice(0, 60)}`);
      const patcher = spawn('python', [resolve(__dirname, 'insight-patcher.py')], { shell: false, cwd: __dirname });
      let err = '';
      patcher.stderr.on('data', d => { err += d.toString(); });
      patcher.on('close', (code) => {
        if (code !== 0) { log(`step7: patcher failed: ${err.slice(0, 120)}`); verifyAction(id, `patcher-failed`); }
        else { log(`step7: patcher succeeded`); verifyAction(id, 'patched'); }
        markExecuted(desc);
      });
      patcher.on('error', e => { log(`step7: patcher error: ${e.message}`); verifyAction(id, `patcher-error`); });
    }
  }

  // Clear pending after firing all
  writeFileSync(PENDING_FILE, '', 'utf-8');
  log(`step7: cleared pending-actions.md (${lines.length} actions fired)`);
}

// ── Step 8: Hook system health check ──────────────────────────────────────────
function step8_healthCheck() {
  const STATE_DIR_S = STATE_DIR;
  const COUNTER_FILE = resolve(STATE_DIR_S, 'auto-seed-counter.json');
  const TRIGGER_FILE = resolve(STATE_DIR_S, 'auto-insight-trigger.json');
  const ACTIVE_LEARN_FILE = resolve(STATE_DIR_S, 'active-learn-trigger.json');
  const PATTERN_FILE = resolve(STATE_DIR_S, 'auto-seed-patterns.json');
  const ERROR_FILE = resolve(STATE_DIR_S, 'auto-seed-errors.json');
  const DEBUG_FILE = resolve(STATE_DIR_S, 'auto-seed-debugloop.json');
  const SESSION_ID = process.env.OMC_SESSION_ID || 'unknown';

  const VERIFY_FILE_S = resolve(STATE_DIR_S, 'hook-health-check.md');

  const issues = [];

  // 1. Check counter fired but no trigger file (should have been consumed)
  if (existsSync(COUNTER_FILE)) {
    try {
      const counter = JSON.parse(readFileSync(COUNTER_FILE, 'utf-8'));
      if (counter.fired && counter.sessionId === SESSION_ID && existsSync(TRIGGER_FILE)) {
        issues.push('⚠️ counter.fired=true but trigger file still exists (not consumed)');
      }
      // Counter not reset for this session
      if (counter.sessionId && counter.sessionId !== SESSION_ID && counter.count > 0) {
        issues.push(`⚠️ counter belongs to different session (${counter.sessionId.slice(0,8)}≠${SESSION_ID.slice(0,8)})`);
      }
    } catch {}
  }

  // 2. Check active-learn trigger orphaned (should be consumed next session)
  if (existsSync(ACTIVE_LEARN_FILE)) {
    try {
      const trigger = JSON.parse(readFileSync(ACTIVE_LEARN_FILE, 'utf-8'));
      if (trigger.sessionId && trigger.sessionId !== SESSION_ID) {
        issues.push(`⚠️ active-learn trigger stale (${trigger.sessionId.slice(0,8)}≠${SESSION_ID.slice(0,8)})`);
      }
    } catch { issues.push('⚠️ active-learn trigger file corrupted (invalid JSON)'); }
  }

  // 3. Check patterns accumulated but no insights generated
  if (existsSync(PATTERN_FILE)) {
    try {
      const patterns = JSON.parse(readFileSync(PATTERN_FILE, 'utf-8'));
      if (patterns.sessionId !== SESSION_ID) {
        issues.push(`⚠️ patterns belong to different session (${patterns.sessionId?.slice(0,8) || 'null'})`);
      }
    } catch {}
  }

  // 4. High tool count but no trigger fired
  if (existsSync(COUNTER_FILE)) {
    try {
      const counter = JSON.parse(readFileSync(COUNTER_FILE, 'utf-8'));
      if (counter.count > 15 && !counter.fired && counter.sessionId === SESSION_ID) {
        issues.push(`⚠️ ${counter.count} tool calls but fired=false (threshold=${counter.threshold || 10})`);
      }
    } catch {}
  }

  // 5. Error patterns accumulating but no insight
  if (existsSync(ERROR_FILE)) {
    try {
      const errData = JSON.parse(readFileSync(ERROR_FILE, 'utf-8'));
      if (errData.errors && errData.errors.length > 5 && errData.sessionId === SESSION_ID) {
        issues.push(`⚠️ ${errData.errors.length} error patterns stored, no insight triggered`);
      }
    } catch {}
  }

  // 5b. Recurrence check: error class appeared ≥3 times across sessions → past insight may not be working
  const ERROR_FREQ_FILE = resolve(STATE_DIR_S, 'error-frequency.json');
  if (existsSync(ERROR_FREQ_FILE)) {
    try {
      const freq = JSON.parse(readFileSync(ERROR_FREQ_FILE, 'utf-8'));
      const RECURRENCE_THRESHOLD_DRAIN = 3;
      for (const [cls, data] of Object.entries(freq.classes || {})) {
        if (data.totalCount >= RECURRENCE_THRESHOLD_DRAIN) {
          issues.push(`⚠️ RECURRING ERROR CLASS: "${cls}" ×${data.totalCount} — past insight may not be effective`);
        }
      }
    } catch {}
  }

  // 6. Hook call chain verification: counter not incrementing (PostToolUse not calling --check)
  // Compare transcript tool count vs counter count to detect hook failure
  const transcriptPath = resolve(_TRANSCRIPT_BASE, `${SESSION_ID}.jsonl`);
  let transcriptToolCount = 0;
  if (existsSync(transcriptPath)) {
    try {
      const lines = readFileSync(transcriptPath, 'utf-8').split('\n').filter(Boolean);
      for (const line of lines) {
        try {
          const entry = JSON.parse(line);
          const content = entry.message?.content;
          if (!Array.isArray(content)) continue;
          for (const b of content) {
            if (b.type === 'tool_use' && b.name) transcriptToolCount++;
          }
        } catch {}
      }
    } catch {}
  }
  if (existsSync(COUNTER_FILE)) {
    try {
      const counter = JSON.parse(readFileSync(COUNTER_FILE, 'utf-8'));
      if (counter.sessionId === SESSION_ID && counter.count > 5) {
        const ratio = transcriptToolCount / counter.count;
        if (ratio > 3) {
          issues.push(`⚠️ hook call chain broken: counter=${counter.count} but transcript~${transcriptToolCount} (ratio=${ratio.toFixed(1)} — PostToolUse may not be firing)`);
        }
      }
      // Counter stuck at 0 despite high transcript tool count
      if (counter.count === 0 && transcriptToolCount > 10) {
        issues.push(`🔴 hook call chain dead: counter=0 but transcript has ${transcriptToolCount} tools — PostToolUse not calling --check at all`);
      }
    } catch {}
  }

  // ── Auto-heal: fix known broken states instead of just reporting ──
  const autoFixed = [];

  // Heal 1: stale trigger file (counter.fired but trigger still exists)
  if (existsSync(COUNTER_FILE) && existsSync(TRIGGER_FILE)) {
    try {
      const counter = JSON.parse(readFileSync(COUNTER_FILE, 'utf-8'));
      if (counter.fired && counter.sessionId === SESSION_ID) {
        try { unlinkSync(TRIGGER_FILE); autoFixed.push('cleared stale auto-insight-trigger (fired=true)'); } catch {}
      }
    } catch {}
  }

  // Heal 2: wrong-session counter (wasn't reset at session start)
  if (existsSync(COUNTER_FILE)) {
    try {
      const counter = JSON.parse(readFileSync(COUNTER_FILE, 'utf-8'));
      if (counter.sessionId !== SESSION_ID && counter.count > 0) {
        // Reset it
        writeFileSync(COUNTER_FILE, JSON.stringify({ count: 0, fired: false, sessionId: SESSION_ID }), 'utf-8');
        autoFixed.push(`reset cross-session counter (was ${counter.sessionId?.slice(0,8)}, now ${SESSION_ID.slice(0,8)})`);
      }
    } catch {}
  }

  // Heal 3: stale active-learn trigger
  if (existsSync(ACTIVE_LEARN_FILE)) {
    try {
      const trigger = JSON.parse(readFileSync(ACTIVE_LEARN_FILE, 'utf-8'));
      if (trigger.sessionId && trigger.sessionId !== SESSION_ID) {
        try { unlinkSync(ACTIVE_LEARN_FILE); autoFixed.push('cleared stale active-learn-trigger'); } catch {}
      }
    } catch {}
  }

  // Heal 4: stale pattern/error/debug files from wrong session
  for (const [file, label] of [[PATTERN_FILE, 'patterns'], [ERROR_FILE, 'errors'], [DEBUG_FILE, 'debugloop']]) {
    if (existsSync(file)) {
      try {
        const data = JSON.parse(readFileSync(file, 'utf-8'));
        if (data.sessionId !== SESSION_ID) {
          const defaultData = label === 'patterns'
            ? { cmds: [], sessionId: SESSION_ID }
            : label === 'errors'
              ? { errors: [], sessionId: SESSION_ID }
              : { cycles: [], sessionId: SESSION_ID };
          writeFileSync(file, JSON.stringify(defaultData), 'utf-8');
          autoFixed.push(`reset stale ${label} (was ${data.sessionId?.slice(0,8) || 'null'})`);
        }
      } catch {}
    }
  }

  // Heal 5: Hook call chain dead — counter=0 but transcript has tools
  // Check hooks.json for missing/broken PostToolUse config and auto-fix
  if (existsSync(COUNTER_FILE)) {
    try {
      const counter = JSON.parse(readFileSync(COUNTER_FILE, 'utf-8'));
      if (counter.count === 0 && transcriptToolCount > 10) {
        const HOOKS_FILE = resolve(__dirname, '../../.claude/hooks.json');
        const FIX_HOOKS_FILE = resolve(STATE_DIR_S, 'auto-fix-hooks.md');
        if (existsSync(HOOKS_FILE)) {
          try {
            const hooks = JSON.parse(readFileSync(HOOKS_FILE, 'utf-8'));
            const ptHooks = hooks?.hooks?.PostToolUse || [];
            // Check for duplicate PostToolUse entries (same script called multiple times)
            const seenCmds = new Set();
            const duplicates = [];
            for (const entry of ptHooks) {
              if (!entry?.hooks) continue;
              for (const h of entry.hooks) {
                if (h?.command && seenCmds.has(h.command)) duplicates.push(h.command);
                else if (h?.command) seenCmds.add(h.command);
              }
            }
            // Check for missing PostToolUse entirely
            if (ptHooks.length === 0 || duplicates.length > 0) {
              const correctConfig = {
                description: 'OMC Hooks — Session lifecycle + active learning',
                hooks: {
                  PostToolUse: [{ hooks: [{ type: 'command', command: 'node D:/OpenClaw/workspace/.omc/scripts/hook-auto-seed.mjs --check', timeout: 1000 }, { type: 'command', command: 'node D:/OpenClaw/workspace/.omc/scripts/hook-active-learn.mjs', timeout: 1000 }] }],
                  PreToolUse: [],
                  SessionStart: [{ hooks: [{ type: 'command', command: 'node D:/OpenClaw/workspace/.omc/scripts/hook-session-start-inject.mjs', timeout: 3000 }] }],
                  SessionEnd: [{ hooks: [{ type: 'command', command: 'node D:/OpenClaw/workspace/.omc/scripts/hook-session-end-drain.mjs', timeout: 30000 }] }],
                },
              };
              writeFileSync(HOOKS_FILE, JSON.stringify(correctConfig, null, 2), 'utf-8');
              autoFixed.push('fixed hooks.json: removed duplicate PostToolUse entries + added active-learn hook');
              const flag = `## ⚠️ hooks.json Auto-Fixed

检测到 PostToolUse 配置损坏（重复定义或缺少条目），已自动修复。
请验证下次 session 中工具调用计数器是否正常递增（观察 notepad 中 "INSIGHT TRIGGER" 是否出现）。

修复内容：
- 移除了重复的 PostToolUse 条目
- 添加了 hook-active-learn.mjs 到 PostToolUse
`;
              writeFileSync(FIX_HOOKS_FILE, flag, 'utf-8');
            }
          } catch (e) {
            issues.push(`🔴 hooks.json 修复失败: ${e.message}`);
          }
        }
      }
    } catch {}
  }

  if (issues.length === 0 && autoFixed.length === 0) {
    log('step8: hook-health OK');
    return;
  }

  if (issues.length > 0) {
    log('step8: hook-health ISSUES: ' + issues.length);
    for (const issue of issues) { log('  ' + issue); }
  }
  if (autoFixed.length > 0) {
    log('step8: AUTO-HEALED: ' + autoFixed.join('; '));
  }

  // Write health report for next session injection
  let report = `## Hook System Health Check\n\n`;
  if (issues.length > 0) {
    report += issues.map(i => `- ${i}`).join('\n') + '\n\n';
  }
  if (autoFixed.length > 0) {
    report += `**Auto-healed this session:**\n` + autoFixed.map(i => `- ✅ ${i}`).join('\n') + '\n\n';
  }
  report += `_step8_healthCheck at session end._\n`;
  writeFileSync(VERIFY_FILE_S, report, 'utf-8');
}


// ── Step 9: Meta-cognitive Self-Audit ──────────────────────────────────────────
function step9_selfAudit() {
  const IDEA_FILE = resolve(__dirname, '../innovation/ideas.md');
  const EFF_FILE = resolve(STATE_DIR, 'insight-effectiveness.json');
  const FREQ_FILE = resolve(STATE_DIR, 'error-frequency.json');
  const RECOMMEND_FILE = resolve(STATE_DIR, 'meta-cognitive-recommend.md');
  const today = new Date().toISOString().split('T')[0];

  const recommendations = [];

  // 1. Ineffective insights: recurrenceAfter > 0 means past fix didn't work
  if (existsSync(EFF_FILE)) {
    try {
      const eff = JSON.parse(readFileSync(EFF_FILE, 'utf-8'));
      for (const [cls, data] of Object.entries(eff.classes || {})) {
        const insights = data.insights || [];
        for (const insight of insights) {
          const rec = insight.recurrenceAfter || [];
          if (rec.length > 0) {
            recommendations.push({
              type: 'ineffective-insight',
              severity: rec.length >= 2 ? 'high' : 'medium',
              cls,
              title: insight.title,
              recurrence: rec.length,
              suggestion: `insight "${insight.title.slice(0, 40)}" for ${cls} recurred ${rec.length}× after execution — current fix is insufficient`,
            });
          }
        }
      }
    } catch {}
  }

  // 2. Rising error class trends: 3+ occurrences with no effective insight
  if (existsSync(FREQ_FILE)) {
    try {
      const freq = JSON.parse(readFileSync(FREQ_FILE, 'utf-8'));
      for (const [cls, data] of Object.entries(freq.classes || {})) {
        if (data.totalCount >= 3) {
          let hasEffectiveInsight = false;
          if (existsSync(EFF_FILE)) {
            try {
              const eff = JSON.parse(readFileSync(EFF_FILE, 'utf-8'));
              const insights = eff.classes?.[cls]?.insights || [];
              hasEffectiveInsight = insights.some(i => !(i.recurrenceAfter && i.recurrenceAfter.length > 0));
            } catch {}
          }
          if (!hasEffectiveInsight && data.totalCount >= 3) {
            recommendations.push({
              type: 'rising-error',
              severity: data.totalCount >= 5 ? 'high' : 'medium',
              cls,
              count: data.totalCount,
              suggestion: `error class "${cls}" has ${data.totalCount} occurrences but no effective insight — needs root cause analysis`,
            });
          }
        }
      }
    } catch {}
  }

  // 3. Self-reflect failures: error class 'self-reflect' means implementation lacked post-execution review
  if (existsSync(FREQ_FILE)) {
    try {
      const freq = JSON.parse(readFileSync(FREQ_FILE, 'utf-8'));
      const selfReflect = freq.classes?.['self-reflect'];
      if (selfReflect && selfReflect.totalCount >= 1) {
        recommendations.push({
          type: 'self-reflect',
          severity: selfReflect.totalCount >= 2 ? 'high' : 'medium',
          cls: 'self-reflect',
          count: selfReflect.totalCount,
          suggestion: `self-reflect failure ×${selfReflect.totalCount}: implementation lacked post-execution review — system bypassed its own check mechanism`,
        });
      }
    } catch {}
  }

  if (recommendations.length === 0) {
    // No issues found — still generate a proactive seed
    recommendations.push({
      type: 'proactive',
      severity: 'low',
      suggestion: 'system healthy — consider: 1) review oldest unexecuted insights, 2) prune stale patterns from agentdb',
    });
  }

  // Write recommendation to file for next session injection
  let recommendMd = `## Meta-Cognitive Self-Audit (Step 9)\n\n`;
  recommendMd += `**Audited**: ${today}  \n`;
  recommendMd += `**Issues found**: ${recommendations.filter(r => r.type !== 'proactive').length}  \n\n`;

  const highSeverity = recommendations.filter(r => r.severity === 'high');
  const mediumSeverity = recommendations.filter(r => r.severity === 'medium');
  const lowSeverity = recommendations.filter(r => r.severity === 'low');

  if (highSeverity.length > 0) {
    recommendMd += `### 🔴 High Priority\n\n`;
    for (const r of highSeverity) {
      recommendMd += `- **${r.cls || 'system'}**: ${r.suggestion}\n`;
    }
    recommendMd += '\n';
  }
  if (mediumSeverity.length > 0) {
    recommendMd += `### 🟡 Medium Priority\n\n`;
    for (const r of mediumSeverity) {
      recommendMd += `- **${r.cls || 'system'}**: ${r.suggestion}\n`;
    }
    recommendMd += '\n';
  }
  if (lowSeverity.length > 0) {
    recommendMd += `### 🟢 Proactive\n\n`;
    for (const r of lowSeverity) {
      recommendMd += `- ${r.suggestion}\n`;
    }
    recommendMd += '\n';
  }

  // Generate 1 minimal seed from highest priority issue
  const topIssue = recommendations.find(r => r.type !== 'proactive') || recommendations[0];
  if (topIssue && topIssue.type !== 'proactive') {
    const seedAction = generateSeedAction(topIssue);
    if (seedAction) {
      recommendMd += `### Generated Seed (f:4)\n\n`;
      recommendMd += `- [${today}] STAGE [AUTO:meta-audit] ${seedAction}\n`;
    }
  }

  writeFileSync(RECOMMEND_FILE, recommendMd, 'utf-8');
  log(`step9: self-audit → ${recommendations.length} findings, ${highSeverity.length} high`);
}

function generateSeedAction(issue) {
  const { type, cls, title, suggestion } = issue;
  if (type === 'ineffective-insight') {
    return `[score:3×4=12] [f:4] 改进${cls} insight | benefit: 修复失效的fix，重新设计解决方案 | reason: 现有fix在${issue.recurrence}次recurrence后仍未生效 | approach: 分析recurrence原因→重新设计fix→测试验证`;
  }
  if (type === 'rising-error') {
    return `[score:3×3=9] [f:3] ${cls}根因分析 | benefit: 找到反复出现的${cls}错误根源 | reason: ${issue.count}次出现说明系统性而非偶发性 | approach: 收集${cls}的所有错误日志→归纳模式→建立防御规则`;
  }
  if (type === 'self-reflect') {
    return `[score:4×3=12] [f:3] 自我审视机制修复 | benefit: 消除实现后不复查的惯性 | reason: ${issue.count}次未审视自己，说明系统缺乏自我检查点 | approach: 在hook-skill-router后增加post-execution审查→检查是否自问'还有什么缺陷'`;
  }
  return null;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.cleanup) { cleanup(args.cleanup); return; }

  const sessionId = process.env.OMC_SESSION_ID || Date.now().toString();
  log(`=== session end ===`);

  // Step 1: MCP drain
  step1_drain(readQueue(), sessionId);

  // Step 2: Self-improve (dangerous rules)
  const siOut = await step2_selfImprove();
  if (siOut.trim()) {
    for (const line of siOut.trim().split('\n').slice(0, 5)) {
      if (line.trim() && !line.startsWith('=')) log(`self-improve: ${line.trim().slice(0, 120)}`);
    }
  }

  // Step 3: Workflow detector
  const auditCount = readAuditCount();
  const wfOut = await step3_workflowDetector(auditCount);

  // Step 4: Trajectory compressor
  await step4_trajectory();

  // Step 5: Honcho-lite
  step5_honchoLite();

  // Step 6: Auto-generate insights
  await step6_insightGenerator();

  // Step 7: Execute pending actions immediately
  step7_executePendingActions();

  // Step 8: Hook system health check
  step8_healthCheck();

  // Step 9: Meta-cognitive self-audit
  step9_selfAudit();

  // Step 10: Skill fragment consumer — convert reflect fragments to skills
  try {
    const script = resolve(__dirname, 'hook-skill-fragment-consumer.mjs');
    const p = spawn('node', [script, '--approve-all'], {
      stdio: ['ignore', 'pipe', 'pipe'],
      cwd: __dirname,
      windowsHide: true,
    });
    let out = '';
    p.stdout.on('data', (d) => { out += d.toString(); });
    p.stderr.on('data', (d) => { out += d.toString(); });
    p.on('close', () => {
      if (out.trim()) log(`skill-consumer: ${out.trim().replace(/\n/g, ' ')}`);
    });
  } catch (e) { log(`skill-consumer error: ${e.message}`); }

  log(`=== drain complete ===`);
}

main().catch(() => {});
