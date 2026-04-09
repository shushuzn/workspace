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
const TRIGGER_FILE = resolve(STATE_DIR, 'auto-insight-trigger.json');
const COUNTER_FILE = resolve(STATE_DIR, 'auto-seed-counter.json');

function log(...a) { console.error('[inject]', ...a); }

// Check counter for interrupted insight generation
function readCounter() {
  if (!existsSync(COUNTER_FILE)) return null;
  try { return JSON.parse(readFileSync(COUNTER_FILE, 'utf-8')); } catch { return null; }
}

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

  // 0. Counter check: if count>0 but trigger not fired, AI should complete insight
  const counter = readCounter();
  if (counter && counter.count > 0 && !counter.fired && !existsSync(TRIGGER_FILE)) {
    const prompt = `## COUNTER INTERRUPTED

上次数调用未完成 insight 生成（计数器=${counter.count}，fired=${counter.fired}）。

请立即生成一条 insight，基于以下上下文：
- 当前工具统计可通过读取 transcript 分析
- 或直接基于近期工作内容生成

格式：
### N. [标题]
**Observation**: [具体观察]
**Rule**: [规则]
**Fix**: [可执行动作或 N/A]

写完追加到 .omc/state/session-insights.md，若 Fix 非 N/A 则同步追加到 .omc/state/pending-actions.md
`;
    parts.push(prompt);
  }

  // 1. Auto-insight trigger (highest priority — in-session insight generation)
  if (existsSync(TRIGGER_FILE)) {
    try {
      const trigger = JSON.parse(readFileSync(TRIGGER_FILE, 'utf-8'));
      const today = new Date().toISOString().split('T')[0];
      const prompt = `## IN-SESSION INSIGHT TRIGGER

检测到 ${trigger.count} 次工具调用（阈值 ${trigger.threshold}），请立即生成一条 insight。

当前工具统计：
${trigger.toolStats ? `工具统计: Bash=${trigger.toolStats.tools?.Bash || 0}, Read=${trigger.toolStats.tools?.Read || 0}, Edit=${trigger.toolStats.tools?.Edit || 0}, Write=${trigger.toolStats.tools?.Write || 0}, Grep=${trigger.toolStats.tools?.Grep || 0}` : `${trigger.count} 次工具调用`}
${trigger.toolStats?.topBash?.length ? `Top Bash 命令：\n${trigger.toolStats.topBash.map((c, i) => `${i + 1}. ${c}`).join('\n')}` : ''}

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
      parts.push(prompt);
    } catch { /* invalid JSON, ignore */ }
  }

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

  // 8. Relevant past insights (context-aware retrieval)
  const cwd = process.env.OMC_CWD || process.env.PWD || '';
  if (cwd && existsSync(INSIGHTS_FILE)) {
    const kw = cwd.split(/[\/\\_\-\.]/).filter(Boolean).slice(-3); // last 3 path segments
    const insights = readFileSync(INSIGHTS_FILE, 'utf-8');
    const lines = insights.split('\n');
    const scored = [];
    let currentBlock = '';
    let currentNum = 0;

    for (const line of lines) {
      const tm = line.match(/^### (\d+)\.\s+\[(.+?)\]/);
      if (tm) {
        if (currentNum > 0 && kw.some(k => currentBlock.toLowerCase().includes(k.toLowerCase()))) {
          const relevance = kw.filter(k => currentBlock.toLowerCase().includes(k.toLowerCase())).length;
          scored.push({ num: currentNum, block: currentBlock.slice(0, 300) });
        }
        currentNum = parseInt(tm[1]);
        currentBlock = line;
      } else {
        currentBlock += ' ' + line;
      }
    }
    if (scored.length > 0) {
      const top = scored.sort((a, b) => b.num - a.num).slice(0, 3);
      const insightList = top.map(i => `### ${i.num}. [...]\n> ${i.block.slice(0, 150)}...`).join('\n\n');
      parts.push(`## Relevant Past Insights (context: ${cwd.split(/[\/\\]/).slice(-2).join('/')})

检索关键词: ${kw.join(', ')}

${insightList}

做任务前先检索相关 insight — 避免重复踩坑。`);
    }
  }

  if (parts.length === 0) return; // Nothing to inject

  const combined = parts.join('\n\n---\n\n');
  const output = { systemMessage: combined };
  console.log(JSON.stringify(output));
}

main().catch(() => {}); // Never fail
