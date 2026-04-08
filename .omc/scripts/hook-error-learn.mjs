#!/usr/bin/env node
/**
 * OMC Error Learning
 * Calls MCP tools to store error-recovery patterns.
 * Gracefully handles MCP unavailability.
 *
 * Usage:
 *   node hook-error-learn.mjs --type error-recovery --pattern <type> --command <cmd> [--severity s] [--dangerous] [--pattern-name <name>]
 */
import { existsSync, readFileSync, writeFileSync, mkdirSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const STATE_DIR = resolve(__dirname, '../state');

// MCP tool storage (written to file for MCP server to pick up)
const MCP_LEARN_QUEUE = resolve(STATE_DIR, 'mcp-learn-queue.jsonl');

// ── Parse args ────────────────────────────────────────────────────────────────
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

// ── Try MCP call ───────────────────────────────────────────────────────────────
async function tryMCPStore(type, pattern, command, severity, dangerous, patternName) {
  // Write to queue file — the MCP server can pick this up if it polls the file.
  // This is the most reliable approach since we can't directly call MCP tools from Node scripts.
  const entry = {
    type: 'agentdb_pattern-store',
    pattern: `[${type}] ${command}`,
    patternType: type,
    confidence: dangerous ? 0.95 : (severity === 'critical' ? 0.9 : 0.7),
    metadata: {
      severity,
      dangerous: dangerous || false,
      patternName: patternName || null,
      command: command.slice(0, 200),
      learnedAt: new Date().toISOString(),
    },
    queuedAt: new Date().toISOString(),
  };

  const { appendFileSync, existsSync: es } = await import('fs');
  const dir = dirname(MCP_LEARN_QUEUE);
  if (!es(dir)) mkdirSync(dir, { recursive: true });
  appendFileSync(MCP_LEARN_QUEUE, JSON.stringify(entry) + '\n', 'utf-8');
  return true;
}

// ── Try hooks_post-task ───────────────────────────────────────────────────────
async function tryMCPFeedback(taskId, success, quality) {
  const entry = {
    type: 'agentdb_feedback',
    taskId,
    success,
    quality,
    queuedAt: new Date().toISOString(),
  };

  const { appendFileSync, existsSync: es } = await import('fs');
  const dir = dirname(MCP_LEARN_QUEUE);
  if (!es(dir)) mkdirSync(dir, { recursive: true });
  appendFileSync(MCP_LEARN_QUEUE, JSON.stringify(entry) + '\n', 'utf-8');
  return true;
}

// ── Try hooks_post-command ────────────────────────────────────────────────────
async function tryMCPPostCommand(command, exitCode) {
  const entry = {
    type: 'hooks_post-command',
    command: command.slice(0, 200),
    exitCode,
    queuedAt: new Date().toISOString(),
  };

  const { appendFileSync, existsSync: es } = await import('fs');
  const dir = dirname(MCP_LEARN_QUEUE);
  if (!es(dir)) mkdirSync(dir, { recursive: true });
  appendFileSync(MCP_LEARN_QUEUE, JSON.stringify(entry) + '\n', 'utf-8');
  return true;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));

  if (!args.type) {
    console.log('Usage: node hook-error-learn.mjs --type <type> --pattern <pattern> --command <cmd> [--severity s] [--dangerous] [--pattern-name <name>]');
    return;
  }

  try {
    if (args.type === 'error-recovery') {
      const ok = await tryMCPStore(
        args.pattern || 'error-recovery',
        args.pattern || '',
        args.command || '',
        args.severity || 'low',
        args.dangerous || false,
        args.patternName || null,
      );
      console.log(ok ? 'mcp-queued:error-recovery' : 'mcp-unavailable');
    } else if (args.type === 'feedback') {
      const ok = await tryMCPFeedback(args.taskId || 'unknown', args.success !== 'false', parseFloat(args.quality || '0.5'));
      console.log(ok ? 'mcp-queued:feedback' : 'mcp-unavailable');
    } else if (args.type === 'post-command') {
      const ok = await tryMCPPostCommand(args.command || '', parseInt(args.exitCode || '0'));
      console.log(ok ? 'mcp-queued:post-command' : 'mcp-unavailable');
    } else {
      console.log('unknown type');
    }
  } catch (e) {
    console.error('mcp-queue-error:', e.message);
    console.log('mcp-unavailable');
  }
}

main().catch(e => { console.error(e.message); process.exit(1); });
