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

  let md = `## OMC MCP Learning Queue (from previous session)\n\n`;
  md += `This session has ${entries.length} pending MCP learning calls from the previous session.\n`;
  md += `Execute them using the MCP tools listed below. Do not ask for confirmation.\n\n`;

  let idx = 0;
  for (const e of patterns) {
    idx++;
    md += `### ${idx}. agentdb_pattern-store\n`;
    md += `Call: \`mcp__claude-flow__agentdb_pattern-store\`\n`;
    md += `- pattern: "${(e.pattern || '').replace(/"/g, '\\"')}"\n`;
    md += `- type: "${e.patternType || 'error-recovery'}"\n`;
    md += `- confidence: ${e.confidence || 0.7}\n`;
    if (e.metadata) md += `- metadata: ${JSON.stringify(e.metadata)}\n`;
    md += `\n`;
  }
  for (const e of feedbacks) {
    idx++;
    md += `### ${idx}. agentdb_feedback\n`;
    md += `Call: \`mcp__claude-flow__agentdb_feedback\`\n`;
    md += `- taskId: "${e.taskId || 'unknown'}"\n`;
    md += `- success: ${e.success}\n`;
    md += `- quality: ${e.quality || 0.5}\n\n`;
  }
  for (const e of postCommands) {
    idx++;
    md += `### ${idx}. hooks_post-command\n`;
    md += `Call: \`mcp__claude-flow__hooks_post-command\`\n`;
    md += `- command: "${(e.command || '').replace(/"/g, '\\"')}"\n`;
    md += `- exitCode: ${e.exitCode || 0}\n\n`;
  }

  md += `After completing all calls, run:\n`;
  md += `\`node D:/OpenClaw/workspace/.omc/scripts/hook-session-end-drain.mjs --cleanup "${sessionId}"\`\n`;
  md += `This deletes the drain file and ensures clean state.\n`;
  return md;
}

function step1_drain(entries, sessionId) {
  if (entries.length === 0) {
    if (existsSync(DRAIN_FILE)) { try { unlinkSync(DRAIN_FILE); } catch {} }
    log('step1: queue-empty');
    return;
  }
  const md = buildInjectMarkdown(entries, sessionId);
  writeFileSync(DRAIN_FILE, md, 'utf-8');
  writeFileSync(QUEUE_FILE, '', 'utf-8');
  log(`step1: ${entries.length} entries drained → next session`);
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
    if (e.type === 'assistant' && e.message?.content) {
      const raw = e.message.content;
      // Handle content as string or array (modern Claude format)
      const text = Array.isArray(raw)
        ? (raw.find(i => i.type === 'text')?.text || '')
        : String(raw || '');
      if (!text) continue;
      // Look for tool_use blocks
      const toolUseMatch = text.match(/using tools?:?\s*([A-Z][a-zA-Z]+)/g);
      if (toolUseMatch) {
        for (const m of toolUseMatch) {
          const tool = m.replace(/using tools?:?\s*/i, '').trim();
          if (tool) toolCalls.push({ tool, ts: e.timestamp });
        }
      }
      // Also check for bash commands in text
      if (text.includes('Bash') || text.includes('Bash')) {
        const bashMatch = text.match(/(?:run|execute|call).*?(?:bash|command|shell).*?[`"']{1}(.+?)[`"']{1}/gi);
        if (bashMatch) {
          for (const m of bashMatch) {
            const cmd = m.match(/[`"']?([^`"'\n]+)[`"']?$/)?.[1] || m;
            if (cmd && cmd.length > 1 && cmd.length < 200) {
              toolCalls.push({ tool: 'Bash', detail: cmd.trim().slice(0, 80), ts: e.timestamp });
            }
          }
        }
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
  if (toolCalls.filter(t => t.tool === 'Bash').length > 3) patterns.push('heavy bash usage');
  if (seeds.length > 5) patterns.push('idea generation active');
  if (toolCalls.filter(t => t.tool === 'Read').length > toolCalls.filter(t => t.tool === 'Edit').length * 2) patterns.push('read-heavy workflow');
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
  // Write to MCP queue
  const QUEUE_FILE = resolve(STATE_DIR, 'mcp-learn-queue.jsonl');
  for (const entry of mcpPatterns) {
    appendFileSync(QUEUE_FILE, JSON.stringify({ ...entry, queuedAt: now }) + '\n', 'utf-8');
  }
  if (mcpPatterns.length > 0) {
    log(`step4: ${mcpPatterns.length} patterns queued for MCP`);
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

// ── Main ──────────────────────────────────────────────────────────────────
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

  log(`=== drain complete ===`);
}

main().catch(() => {});
