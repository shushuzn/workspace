#!/usr/bin/env node
/**
 * OMC Error Capture
 * Reads last-tool-error.json → appends to hook-error-history.jsonl.
 * Also triggers hook-error-learn.mjs for MCP pattern storage.
 *
 * Usage:
 *   node hook-error-capture.mjs [--check]  Capture + learn
 *   node hook-error-capture.mjs --list     Show recent errors
 *   node hook-error-capture.mjs --stats   Show error statistics
 */
import { existsSync, readFileSync, writeFileSync, appendFileSync, mkdirSync, readdirSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const STATE_DIR = resolve(__dirname, '../state');
const ERROR_HISTORY = resolve(STATE_DIR, 'hook-error-history.jsonl');
const PATTERNS_OUT = resolve(STATE_DIR, 'hook-patterns.json');
const LEARN_SCRIPT = resolve(__dirname, 'hook-error-learn.mjs');

// ── Config ──────────────────────────────────────────────────────────────────
const DANGEROUS_PATTERNS = [
  { pattern: /git\s+clean\s+.*-f.*-d/i, name: 'git-clean-fd', severity: 'critical' },
  { pattern: /git\s+reset\s+.*--hard/i, name: 'git-reset-hard', severity: 'high' },
  { pattern: /rm\s+.*-rf/i, name: 'rm-rf', severity: 'high' },
  { pattern: /chmod\s+.*-R\s+777/i, name: 'chmod-777', severity: 'medium' },
  { pattern: /fork\s*:\s*\(\)\s*\{\s*:\|\s*:\s*\}\s*&\s*:/i, name: 'fork-bomb', severity: 'critical' },
  { pattern: /dd\s+.*if=.*of=/i, name: 'dd-destroy', severity: 'critical' },
  { pattern: /mkfs/i, name: 'mkfs-destroy', severity: 'critical' },
  { pattern: /git\s+push\s+.*--force/i, name: 'git-push-force', severity: 'medium' },
];

// ── State ───────────────────────────────────────────────────────────────────
function readLastError() {
  // last-tool-error.json can be in workspace root or any project subdir
  // Check workspace root first
  const workspaceRoot = resolve(__dirname, '../../..');
  const candidates = [
    resolve(STATE_DIR, 'last-tool-error.json'),
    resolve(workspaceRoot, 'last-tool-error.json'),
  ];
  for (const p of candidates) {
    if (existsSync(p)) {
      try {
        return JSON.parse(readFileSync(p, 'utf-8'));
      } catch { /* ignore */ }
    }
  }
  return null;
}

function readErrorHistory() {
  if (!existsSync(ERROR_HISTORY)) return [];
  return readFileSync(ERROR_HISTORY, 'utf-8')
    .split('\n').filter(Boolean)
    .map(l => { try { return JSON.parse(l); } catch { return null; } })
    .filter(Boolean);
}

function appendError(entry) {
  const dir = dirname(ERROR_HISTORY);
  if (!existsSync(dir)) mkdirSync(dir, { recursive: true });
  appendFileSync(ERROR_HISTORY, JSON.stringify(entry) + '\n', 'utf-8');
}

// ── Error Classification ─────────────────────────────────────────────────────
function classifyError(errorObj) {
  const cmd = errorObj.tool_input_preview || '';
  const errorText = errorObj.error || '';

  // Check dangerous patterns
  for (const dp of DANGEROUS_PATTERNS) {
    if (dp.pattern.test(cmd) || dp.pattern.test(errorText)) {
      return { dangerous: true, pattern: dp.name, severity: dp.severity };
    }
  }

  // Classify by error type
  const errorTypes = [
    { pattern: /exit code \d+/i, type: 'exit-code' },
    { pattern: /ENOENT|no such file/i, type: 'not-found' },
    { pattern: /EACCES|permission denied/i, type: 'permission' },
    { pattern: /ECONNREFUSED|connection/i, type: 'network' },
    { pattern: /timeout|timed out/i, type: 'timeout' },
    { pattern: /parse|JSON|syntax/i, type: 'parse-error' },
  ];

  for (const et of errorTypes) {
    if (et.pattern.test(errorText)) {
      return { dangerous: false, type: et.type, severity: 'low' };
    }
  }

  return { dangerous: false, type: 'unknown', severity: 'low' };
}

function parseCommand(jsonStr) {
  try {
    const parsed = JSON.parse(jsonStr);
    return parsed.command || parsed.description || jsonStr;
  } catch {
    return jsonStr;
  }
}

// ── MCP Pattern Learning ───────────────────────────────────────────────────────
async function learnFromError(entry) {
  const { spawn } = await import('child_process');
  const cmd = parseCommand(entry.tool_input_preview || '');
  const errorType = classifyError(entry);

  const args = [
    LEARN_SCRIPT,
    '--type', 'error-recovery',
    '--pattern', errorType.type || 'unknown',
    '--command', cmd.slice(0, 200),
    '--severity', errorType.severity,
  ];

  if (errorType.dangerous) {
    args.push('--dangerous', '--pattern-name', errorType.pattern);
  }

  return new Promise((resolve) => {
    const proc = spawn(process.execPath, args, {
      stdio: 'ignore',
      detached: true,
      windowsHide: true,
    });
    proc.unref();
    resolve();
  });
}

// ── Auto-Rule Generation for Dangerous Patterns ────────────────────────────────
function shouldAutoGenerateRule(entry, history) {
  const cmd = parseCommand(entry.tool_input_preview || '');
  const classification = classifyError(entry);
  if (!classification.dangerous) return false;

  // Count how many times this dangerous pattern appeared
  const count = history.filter(e => {
    const c = parseCommand(e.tool_input_preview || '');
    return classifyError(e).pattern === classification.pattern;
  }).length + 1; // +1 for current

  return count >= 2; // Auto-generate after 2+ occurrences
}

function generateDangerousRule(classification, exampleCmd) {
  const ruleName = `prevent-${classification.pattern}`;
  const ruleFile = resolve(__dirname, `../../.claude/hookify.${ruleName}.local.md`);

  const ruleContent = `---
name: ${ruleName}
enabled: true
event: bash
pattern: ${classification.pattern.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}
---

**危险操作检测：${classification.pattern}**

该命令具有破坏性。${exampleCmd ? `最近出现示例：\`${exampleCmd.slice(0, 80)}\`` : ''}

**建议**：使用 \`--dry-run\` 预览，或选择更安全的替代方案。
`;

  return { ruleName, ruleFile, ruleContent };
}

// ── CLI ─────────────────────────────────────────────────────────────────────
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

  // --stats: show error statistics
  if (args.stats) {
    const history = readErrorHistory();
    const stats = { total: history.length, byType: {}, bySeverity: {} };
    for (const e of history) {
      const cls = classifyError(e);
      stats.byType[cls.type || 'unknown'] = (stats.byType[cls.type || 'unknown'] || 0) + 1;
      stats.bySeverity[cls.severity] = (stats.bySeverity[cls.severity] || 0) + 1;
    }
    console.log(JSON.stringify(stats, null, 2));
    return;
  }

  // --list: show recent errors
  if (args.list) {
    const history = readErrorHistory();
    const recent = history.slice(-10).reverse();
    for (const e of recent) {
      const cls = classifyError(e);
      const cmd = parseCommand(e.tool_input_preview || '').slice(0, 60);
      const danger = cls.dangerous ? '🔴' : '⚠️';
      console.log(`${danger} [${cls.severity}] ${e.error} | ${cmd}`);
    }
    return;
  }

  // --check: capture + learn
  if (args.check) {
    const errorObj = readLastError();
    if (!errorObj) {
      console.log('no-error');
      return;
    }

    const entry = {
      ...errorObj,
      capturedAt: new Date().toISOString(),
      sessionId: process.env.OMC_SESSION_ID || 'unknown',
    };

    const history = readErrorHistory();
    const classification = classifyError(entry);

    // Append to history
    appendError(entry);

    // Learn via MCP (non-blocking)
    learnFromError(entry).catch(() => {});

    // Check if we should auto-generate a rule
    if (shouldAutoGenerateRule(entry, history)) {
      const rule = generateDangerousRule(classification, parseCommand(errorObj.tool_input_preview || ''));
      if (!existsSync(rule.ruleFile)) {
        try {
          writeFileSync(rule.ruleFile, rule.ruleContent, 'utf-8');
          console.log(`AUTO-RULE:${rule.ruleName}`);
        } catch (e) {
          console.error('failed to write rule:', e.message);
        }
      }
    }

    console.log(`captured:${classification.severity}`);
    return;
  }

  // Default: status
  const history = readErrorHistory();
  console.log(`OMC Error Capture`);
  console.log(`  History: ${ERROR_HISTORY}`);
  console.log(`  Total errors: ${history.length}`);
  if (history.length > 0) {
    const dangerous = history.filter(e => classifyError(e).dangerous).length;
    console.log(`  Dangerous: ${dangerous}`);
  }
}

main().catch(e => { console.error(e.message); process.exit(1); });
