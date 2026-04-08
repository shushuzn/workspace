#!/usr/bin/env node
/**
 * OMC Session Start Inject
 * Reads drain file → outputs context injection for Claude Code.
 *
 * SessionStart hook → this script → stdout injects context
 * Claude Code reads stdout → prepends MCP learning instructions to session context
 *
 * Also injects: mid-session reminder + workflow patterns
 */
import { existsSync, readFileSync, readdirSync, statSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const STATE_DIR = resolve(__dirname, '../state');
const TRAJ_DIR = resolve(__dirname, '../trajectories');
const DRAIN_FILE = resolve(STATE_DIR, 'session-start-mcp-inject.md');
const NUDGE_FILE = resolve(STATE_DIR, 'session-nudge.md');
const WF_PATTERNS_FILE = resolve(__dirname, '../innovation/workflow-patterns.md');
const INSIGHTS_FILE = resolve(STATE_DIR, 'session-insights.md');
const VERIFY_FILE = resolve(STATE_DIR, 'insight-verifications.md');
const MID_FILE = resolve(STATE_DIR, 'mid-session-inject.md');

function log(...a) { console.error('[inject]', ...a); }

// Read last trajectory for mid-session context
function readLastTrajectory() {
  if (!existsSync(TRAJ_DIR)) return null;
  let latest = null, latestMtime = 0;
  for (const f of readdirSync(TRAJ_DIR).filter(p => p.endsWith('.md'))) {
    const p = resolve(TRAJ_DIR, f);
    const s = statSync(p);
    if (s.mtimeMs > latestMtime) { latestMtime = s.mtimeMs; latest = p; }
  }
  if (!latest) return null;
  try { return readFileSync(latest, 'utf-8'); } catch { return null; }
}

async function main() {
  const parts = [];

  // 1. MCP drain (highest priority — patterns to store)
  if (existsSync(DRAIN_FILE)) {
    const content = readFileSync(DRAIN_FILE, 'utf-8').trim();
    if (content) parts.push(content);
  }

  // 2. Periodic nudge
  if (existsSync(NUDGE_FILE)) {
    const content = readFileSync(NUDGE_FILE, 'utf-8').trim();
    if (content) parts.push(content);
  }

  // 3. Mid-session reminder (from last trajectory analysis)
  const traj = readLastTrajectory();
  if (traj) {
    const lines = traj.split('\n');
    const sumIdx = lines.findIndex(l => l.includes('## Summary'));
    const summaryLine = sumIdx >= 0 ? (lines[sumIdx + 2] || '') : '';
    const toolLine = lines.find(l => l.includes('Top tools:'));
    const patternsLine = lines.find(l => l.includes('Patterns detected:'));

    const reminders = [];

    // High tool count reminder
    if (summaryLine) {
      const m = summaryLine.match(/(\d+) tool calls/);
      if (m && parseInt(m[1]) > 80) {
        reminders.push(`⚠️ 上个 session 有 ${m[1]} 次工具调用 — 确认没有死循环或重复调试`);
      }
    }

    // No seeds reminder
    if (summaryLine && summaryLine.includes('0 seeds')) {
      reminders.push(`⚠️ 上个 session 未生成任何 seed — 本 session 注意产出 ideas`);
    }

    // Heavy bash reminder
    if (toolLine) {
      const m = toolLine.match(/Bash\((\d+)\)/);
      if (m && parseInt(m[1]) > 30) {
        reminders.push(`⚠️ Bash 调用 ${m[1]} 次 — 确认是否需要 Grep/Edit 替代`);
      }
    }

    // Debugging pattern
    if (patternsLine && patternsLine.includes('debugging')) {
      reminders.push(`🔧 上个 session 处于调试模式 — 本 session 优先创造而非修复`);
    }

    if (reminders.length > 0) {
      parts.push(`## Mid-Session Context (from last session)\n\n${reminders.join('\n')}\n\n${traj}`);
    }
  }

  // 4. Workflow patterns (from workflow detector)
  if (existsSync(WF_PATTERNS_FILE)) {
    const content = readFileSync(WF_PATTERNS_FILE, 'utf-8').trim();
    if (content) {
      parts.push(`## Detected Workflow Patterns\n\n${content}`);
    }
  }

  // 5. Pending insight actions (from omc-insight-action --pickup)
  const PENDING_FILE = resolve(STATE_DIR, 'pending-actions.md');
  if (existsSync(PENDING_FILE)) {
    const content = readFileSync(PENDING_FILE, 'utf-8').trim();
    if (content) {
      parts.push(`## Pending Insight Actions\n\n${content}\n\nRun each action and mark done with:\n\`node D:/OpenClaw/workspace/.omc/scripts/omc-insight-action.mjs --done <id>\``);
    }
  }

  // 6. Unexecuted insights from session-insights.md (auto-trigger)
  if (existsSync(INSIGHTS_FILE)) {
    const content = readFileSync(INSIGHTS_FILE, 'utf-8');
    const lines = content.split('\n');
    const unexecuted = [];
    for (const line of lines) {
      if (!line.includes('✅ EXECUTED') && line.includes('### ')) {
        const match = line.match(/^#{3}\s+\d+\.\s+(.+?)(\s+⚠|\s+✅|$)/);
        if (match) unexecuted.push(match[1].trim());
      }
    }
    if (unexecuted.length > 0) {
      parts.push(`## Unexecuted Insights (auto-detected)\n\n${unexecuted.map((t, i) => `${i + 1}. **${t}**`).join('\n')}\n\nGenerate execution plan for each unexecuted insight.`);
    }
  }

  // 7. Recent verification results (feedback loop)
  if (existsSync(VERIFY_FILE)) {
    const content = readFileSync(VERIFY_FILE, 'utf-8').trim();
    if (content) {
      parts.push(`## Recent Insight Verification Results\n\n${content}`);
    }
  }

  if (parts.length === 0) return; // Nothing to inject

  const combined = parts.join('\n\n---\n\n');
  const output = { systemMessage: combined };
  console.log(JSON.stringify(output));
}

main().catch(() => {}); // Never fail
