#!/usr/bin/env node
/**
 * OMC Active Learning Hook
 * PreToolUse: checks if meaningful work was just completed.
 * If so → reads work output → writes insight trigger.
 *
 * Triggers on: Write/Edit success, git commit, TaskCreate/TaskUpdate
 * Does NOT count — triggers on quality of work, not quantity.
 */
import { existsSync, readFileSync, writeFileSync, appendFileSync, mkdirSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const STATE_DIR = resolve(__dirname, '../state');
const WORK_FILE = resolve(STATE_DIR, 'last-work.json');
const TRIGGER_FILE = resolve(STATE_DIR, 'active-learn-trigger.json');
const INSIGHTS_FILE = resolve(STATE_DIR, 'session-insights.md');
const NOTPAD_FILE = resolve(__dirname, '../notepad.md');

const SELF_SCRIPTS = ['hook-stats.mjs', 'hook-auto-seed.mjs', 'hook-session-start-inject.mjs'];

function recordWork(toolName, input, output) {
  const work = {
    tool: toolName,
    input: input || {},
    output: output || '',
    ts: new Date().toISOString(),
  };
  writeFileSync(WORK_FILE, JSON.stringify(work, null, 2), 'utf-8');
}

function readLastWork() {
  if (!existsSync(WORK_FILE)) return null;
  try { return JSON.parse(readFileSync(WORK_FILE, 'utf-8')); }
  catch { return null; }
}

function isMeaningfulWork(toolName, input) {
  const meaningfulTools = ['Write', 'Edit', 'Bash', 'TaskCreate', 'TaskUpdate'];
  if (!meaningfulTools.includes(toolName)) return false;

  // Filter out self/hook operations
  if (toolName === 'Bash') {
    const cmd = input?.command || '';
    if (SELF_SCRIPTS.some(s => cmd.includes(s))) return false;
    if (cmd.includes('node .omc/scripts/hook-')) return false;
    if (cmd.match(/^(ls|cat|echo|cd|pwd|rm |mkdir )\s/)) return false;
  }

  // Filter out test files, hooks, configs
  if (toolName === 'Write' || toolName === 'Edit') {
    const fp = input?.file_path || '';
    if (!fp) return false;
    if (/\.(txt|test\.|spec\.|tmp|log)$/.test(fp)) return false;
    if (/[/\\]test[/\\]/.test(fp)) return false;
    if (fp.includes('.omc/scripts/hook-')) return false;
    if (fp.includes('.claude/') && !fp.includes('memory')) return false;
  }
  return true;
}

function buildInsightFromWork(work) {
  const { tool, input, output } = work;

  if (tool === 'Write' || tool === 'Edit') {
    const file = input.file_path || '';
    const content = output || '';
    return `## IN-SESSION INSIGHT TRIGGER (Active Learning)

检测到文件操作完成: ${file}

请分析这个文件的实际内容，生成一条有深度的 insight：

### N. [标题]
**Observation**: [具体观察：这段代码/内容解决了什么问题？]
**Rule**: [从这个实现中提取的可复用模式]
**Fix**: N/A

要求：
- 重点分析实际代码内容，不是操作本身
- 提取对未来工作有指导价值的 pattern
- 写完后追加到 .omc/state/session-insights.md`;
  }

  if (tool === 'Bash') {
    const cmd = input.command || '';
    return `## IN-SESSION INSIGHT TRIGGER (Active Learning)

检测到命令执行: ${cmd.slice(0, 80)}

请分析这条命令的作用和效果，生成一条 insight：

### N. [标题]
**Observation**: [这条命令实际完成了什么？]
**Rule**: [从这次执行中提取的模式]
**Fix**: N/A

要求：
- 分析结果而非命令本身
- 写完后追加到 .omc/state/session-insights.md`;
  }

  if (tool === 'TaskCreate' || tool === 'TaskUpdate') {
    return `## IN-SESSION INSIGHT TRIGGER (Active Learning)

检测到任务管理操作: ${tool}

请分析这个任务的创建/更新，生成一条 insight：

### N. [标题]
**Observation**: [这个任务反映了什么工作？]
**Rule**: [任务设计/执行中的模式]
**Fix**: N/A

要求：
- 写完后追加到 .omc/state/session-insights.md`;
  }

  return null;
}

async function main() {
  // Read PreToolUse event from stdin
  let event = {};
  try {
    const data = await new Promise(resolve => {
      let d = '';
      process.stdin.setEncoding('utf8');
      process.stdin.on('data', c => d += c);
      process.stdin.on('end', () => resolve(d));
      setTimeout(() => resolve(''), 500);
    });
    if (data.trim()) event = JSON.parse(data);
  } catch {}

  // For PreToolUse: detect tool that is about to be used
  // Tool info comes from the message content blocks in the event
  const toolName = event.tool_name || event.tool?.name || '';
  const toolInput = event.tool_input || event.tool?.input || {};
  const toolOutput = '';

  if (!isMeaningfulWork(toolName, toolInput)) {
    process.exit(0);
  }

  recordWork(toolName, toolInput, toolOutput);

  const lastWork = readLastWork();
  if (!lastWork) return;

  const insightPrompt = buildInsightFromWork(lastWork);
  if (!insightPrompt) return;

  // Write trigger
  writeFileSync(TRIGGER_FILE, JSON.stringify({
    sessionId: event.session_id || process.env.OMC_SESSION_ID || 'unknown',
    work: lastWork,
    prompt: insightPrompt,
    triggeredAt: new Date().toISOString(),
  }, null, 2), 'utf-8');

  // Update notepad
  let notepad = existsSync(NOTPAD_FILE) ? readFileSync(NOTPAD_FILE, 'utf-8') : '';
  const lines = notepad.split('\n');
  const priorityIdx = lines.findIndex(l => l.startsWith('## Priority Context'));
  if (priorityIdx === -1) return;

  const newLine = `⚡ ACTIVE LEARN: ${lastWork.tool} 完成 — 生成 insight: .omc/state/active-learn-trigger.json`;
  const triggerIdx = lines.findIndex(l => l.includes('ACTIVE LEARN'));
  if (triggerIdx !== -1) lines[triggerIdx] = newLine;
  else {
    const insertIdx = lines.findIndex((l, i) => i > priorityIdx && l.startsWith('##'));
    if (insertIdx === -1) lines.push(newLine);
    else lines.splice(insertIdx, 0, newLine);
  }
  writeFileSync(NOTPAD_FILE, lines.join('\n'), 'utf-8');

  console.log(`ACTIVE:learn triggered by ${lastWork.tool}`);
}

main();
