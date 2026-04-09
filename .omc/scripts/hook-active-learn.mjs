#!/usr/bin/env node
/**
 * OMC Active Learning Hook
 * PostToolUse: checks if meaningful novel work was just completed.
 * Triggers on: git commits, first-ever file extensions, novel tool combos
 * Does NOT fire on routine operations.
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
const PATTERNS_FILE = resolve(STATE_DIR, '../state/agentdb-patterns.jsonl');
const NOVELTY_FILE = resolve(STATE_DIR, 'novelty-seen.json');
const COMBO_FILE = resolve(STATE_DIR, 'tool-combos.json');

const SELF_SCRIPTS = ['hook-stats.mjs', 'hook-auto-seed.mjs', 'hook-session-start-inject.mjs'];

// ── Combo novelty detection ──────────────────────────────────────────────────
function isComboNovel(comboKey) {
  try {
    const data = existsSync(COMBO_FILE) ? JSON.parse(readFileSync(COMBO_FILE, 'utf-8')) : { combos: {} };
    if (!data.combos) data.combos = {};
    if (!data.combos[comboKey]) {
      data.combos[comboKey] = { firstSeen: new Date().toISOString().split('T')[0], count: 1 };
      writeFileSync(COMBO_FILE, JSON.stringify(data), 'utf-8');
      return true;
    }
    data.combos[comboKey].count++;
    writeFileSync(COMBO_FILE, JSON.stringify(data), 'utf-8');
  } catch {}
  return false;
}

// ── Rich novelty detection ───────────────────────────────────────────────────
function isRichNovel(tool, input) {
  const cwd = process.env.OMC_CWD || process.cwd();
  const proj = cwd.split(/[/\\]/).slice(-2).join('/');
  const markers = [];

  if (tool === 'Write' || tool === 'Edit') {
    const fp = input?.file_path || '';
    if (!fp) return false;
    const ext = fp.match(/\.(\w+)$/)?.[1];
    if (ext) markers.push(`proj:${proj}|ext:${ext}`);
    const dir = fp.match(/([^/\\]+)\/[^/\\]+\.\w+$/)?.[1];
    if (dir && !['node_modules', 'dist', 'build', '.git'].includes(dir)) {
      markers.push(`proj:${proj}|new-dir:${dir}`);
    }
  }
  if (tool === 'Bash') {
    const cmd = input?.command || '';
    // Novel pipe combo: e.g. grep|awk, find|xargs
    const pipeTools = cmd.split('|').map(p => p.trim().split(/\s/)[0]).filter(Boolean);
    if (pipeTools.length >= 2) {
      const combo = pipeTools.sort().join('+');
      const key = `proj:${proj}|pipe:${combo}`;
      if (isComboNovel(key)) return true;
    }
    // Novel redirect
    if (/\s>\s[\w.-]+/.test(cmd)) {
      const rf = cmd.match(/>\s+([\w.-]+)/)?.[1];
      if (rf) markers.push(`proj:${proj}|redirect:${rf}`);
    }
  }
  if (tool === 'TaskCreate') {
    const desc = input?.description || '';
    const word = desc.split(/\s/)[0].toLowerCase();
    if (word) markers.push(`task:${word}`);
  }

  if (markers.length === 0) return false;
  try {
    const data = existsSync(NOVELTY_FILE) ? JSON.parse(readFileSync(NOVELTY_FILE, 'utf-8')) : { seen: {} };
    for (const m of markers) {
      if (!data.seen[m]) {
        data.seen[m] = { firstSeen: new Date().toISOString().split('T')[0], count: 1 };
        writeFileSync(NOVELTY_FILE, JSON.stringify(data), 'utf-8');
        return true;
      }
      data.seen[m].count++;
      writeFileSync(NOVELTY_FILE, JSON.stringify(data), 'utf-8');
    }
  } catch {}
  return false;
}

function recordWork(toolName, input, output) {
  const work = { tool: toolName, input: input || {}, output: output || '', ts: new Date().toISOString() };
  writeFileSync(WORK_FILE, JSON.stringify(work, null, 2), 'utf-8');
}

function readLastWork() {
  if (!existsSync(WORK_FILE)) return null;
  try { return JSON.parse(readFileSync(WORK_FILE, 'utf-8')); }
  catch { return null; }
}

function isDuplicateInsight(tool, input) {
  if (!existsSync(PATTERNS_FILE)) return false;
  try {
    const lines = readFileSync(PATTERNS_FILE, 'utf-8').split('\n').filter(Boolean);
    const recent = lines.slice(-20);
    for (const line of recent) {
      try {
        const p = JSON.parse(line);
        if (p?.pattern && input?.file_path && p.pattern.includes(input.file_path.split(/[/\\]/).pop())) return true;
      } catch {}
    }
  } catch {}
  return false;
}

function isMeaningfulWork(toolName, input) {
  const meaningfulTools = ['Write', 'Edit', 'Bash', 'TaskCreate', 'TaskUpdate'];
  if (!meaningfulTools.includes(toolName)) return false;

  if (toolName === 'Bash') {
    const cmd = input?.command || '';
    if (SELF_SCRIPTS.some(s => cmd.includes(s))) return false;
    if (cmd.includes('node .omc/scripts/hook-')) return false;
    if (cmd.match(/^(ls|cat|echo|cd|pwd|rm |mkdir )\s/)) return false;
    // Git commits = meaningful work
    if (/\bgit\s+(commit|push|add)\b/i.test(cmd)) return true;
    // Novel tool combos trigger
    const pipeTools = cmd.split('|').map(p => p.trim().split(/\s/)[0]).filter(Boolean);
    if (pipeTools.length >= 2) {
      const cwd = process.env.OMC_CWD || process.cwd();
      const proj = cwd.split(/[/\\]/).slice(-2).join('/');
      const combo = pipeTools.sort().join('+');
      const key = `proj:${proj}|pipe:${combo}`;
      return isComboNovel(key);
    }
    return false;
  }

  if (toolName === 'Write' || toolName === 'Edit') {
    const fp = input?.file_path || '';
    if (!fp) return false;
    if (/\.(txt|test\.|spec\.|tmp|log)$/.test(fp)) return false;
    if (/[/\\]test[/\\]/.test(fp)) return false;
    if (fp.includes('.omc/scripts/hook-')) return false;
    if (fp.includes('.claude/') && !fp.includes('memory')) return false;
    if (isDuplicateInsight(toolName, input)) return false;
    return isRichNovel(toolName, input);
  }

  if (toolName === 'TaskCreate' || toolName === 'TaskUpdate') {
    return isRichNovel(toolName, input);
  }

  return false;
}

function buildInsightFromWork(work) {
  const { tool, input } = work;
  const cwd = process.env.OMC_CWD || process.cwd();
  const proj = cwd.split(/[/\\]/).slice(-2).join('/');

  if (tool === 'Write' || tool === 'Edit') {
    const file = input.file_path || '';
    const ext = file.match(/\.(\w+)$/)?.[1] || '';
    return `## IN-SESSION INSIGHT TRIGGER (Active Learning)

检测到创新: **新${ext ? ext.toUpperCase() : ''}文件** — ${file} (项目: ${proj})

请分析这个文件的实际内容，生成一条有深度的 insight：

### N. [标题]
**Observation**: [这个 ${ext} 文件解决了什么问题？创新点在哪里？]
**Rule**: [从这个实现中提取的可复用模式]
**Fix**: N/A

要求：
- 重点分析实际代码内容，不是操作本身
- 写完后追加到 .omc/state/session-insights.md`;
  }

  if (tool === 'Bash') {
    const cmd = input.command || '';
    const isCombo = /\|\s*\w/.test(cmd);
    const comboNote = isCombo ? '（工具组合创新）' : '';
    return `## IN-SESSION INSIGHT TRIGGER (Active Learning)${comboNote}

检测到创新命令: **${cmd.slice(0, 80)}** (项目: ${proj})

请分析这条命令的作用和效果，生成一条 insight：

### N. [标题]
**Observation**: [这条命令实际完成了什么？创新点——组合新、方法新还是工具新？]
**Rule**: [从这次执行中提取的可复用模式]
**Fix**: N/A

要求：
- 如果是组合创新（pipe/subshell），重点分析"为什么这些工具能组合"
- 写完后追加到 .omc/state/session-insights.md`;
  }

  if (tool === 'TaskCreate' || tool === 'TaskUpdate') {
    return `## IN-SESSION INSIGHT TRIGGER (Active Learning)

检测到创新任务: **${tool}** — ${input?.description?.slice(0, 60) || ''} (项目: ${proj})

请分析这个任务的创建/更新，生成一条 insight：

### N. [标题]
**Observation**: [这个任务反映了什么创新工作？]
**Rule**: [任务设计/执行中的可复用模式]
**Fix**: N/A

要求：
- 写完后追加到 .omc/state/session-insights.md`;
  }

  return null;
}

async function main() {
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

  const toolName = event.tool_name || event.tool?.name || '';
  const toolInput = event.tool_input || event.tool?.input || {};

  if (!isMeaningfulWork(toolName, toolInput)) {
    process.exit(0);
  }

  recordWork(toolName, toolInput, '');

  const lastWork = readLastWork();
  if (!lastWork) return;

  const insightPrompt = buildInsightFromWork(lastWork);
  if (!insightPrompt) return;

  writeFileSync(TRIGGER_FILE, JSON.stringify({
    sessionId: event.session_id || process.env.OMC_SESSION_ID || 'unknown',
    work: lastWork,
    prompt: insightPrompt,
    triggeredAt: new Date().toISOString(),
  }, null, 2), 'utf-8');

  let notepad = existsSync(NOTPAD_FILE) ? readFileSync(NOTPAD_FILE, 'utf-8') : '';
  const lines = notepad.split('\n');
  const priorityIdx = lines.findIndex(l => l.startsWith('## Priority Context'));
  if (priorityIdx === -1) return;

  const newLine = `⚡ ACTIVE LEARN: ${lastWork.tool} — 创新工作触发 insight | Read trigger: .omc/state/active-learn-trigger.json`;
  const triggerIdx = lines.findIndex(l => l.includes('ACTIVE LEARN'));
  if (triggerIdx !== -1) lines[triggerIdx] = newLine;
  else {
    const insertIdx = lines.findIndex((l, i) => i > priorityIdx && l.startsWith('##'));
    if (insertIdx === -1) lines.push(newLine);
    else lines.splice(insertIdx, 0, newLine);
  }
  writeFileSync(NOTPAD_FILE, lines.join('\n'), 'utf-8');

  console.log(`ACTIVE:learn triggered by ${lastWork.tool} (novelty)`);
}

main();
