#!/usr/bin/env node
/**
 * OMC MCP Reporter
 * Unified reporter that queues MCP learning calls for the claude-flow MCP server.
 *
 * Reads action from args, queues to mcp-learn-queue.jsonl.
 * The MCP server can poll this queue for learning events.
 *
 * Usage:
 *   node hook-mcp-reporter.mjs --report-task --task-id <id> --success <bool> [--quality <0-1>] [--task-desc <text>]
 *   node hook-mcp-reporter.mjs --report-command --command <cmd> --exit-code <n>
 *   node hook-mcp-reporter.mjs --report-error --pattern <type> --command <cmd> [--severity s]
 */
import { existsSync, appendFileSync, mkdirSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const STATE_DIR = resolve(__dirname, '../state');
const QUEUE_FILE = resolve(STATE_DIR, 'mcp-learn-queue.jsonl');

function ensureQueue() {
  const dir = dirname(QUEUE_FILE);
  if (!existsSync(dir)) mkdirSync(dir, { recursive: true });
}

function enqueue(entry) {
  ensureQueue();
  entry.queuedAt = new Date().toISOString();
  appendFileSync(QUEUE_FILE, JSON.stringify(entry) + '\n', 'utf-8');
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

  if (args['report-task']) {
    const success = args.success !== 'false';
    const quality = parseFloat(args.quality || (success ? '0.8' : '0.3'));
    enqueue({
      type: 'hooks_post-task',
      taskId: args['task-id'] || 'unknown',
      success,
      quality,
      task: args['task-desc'] || null,
      storeDecisions: args['store-decisions'] === 'true',
    });
    console.log(`queued:task success=${success} quality=${quality}`);
    return;
  }

  if (args['report-command']) {
    const exitCode = parseInt(args['exit-code'] || '0');
    enqueue({
      type: 'hooks_post-command',
      command: (args.command || '').slice(0, 200),
      exitCode,
    });
    console.log(`queued:command exit=${exitCode}`);
    return;
  }

  if (args['report-error']) {
    enqueue({
      type: 'agentdb_pattern-store',
      pattern: `[error-recovery] ${args.command || ''}`.slice(0, 200),
      patternType: args.pattern || 'unknown',
      confidence: args.severity === 'critical' ? 0.95 : args.severity === 'high' ? 0.8 : 0.6,
      metadata: {
        severity: args.severity || 'low',
        command: (args.command || '').slice(0, 200),
      },
    });
    console.log(`queued:error-pattern ${args.pattern || 'unknown'}`);
    return;
  }

  console.log(`OMC MCP Reporter — queues learning events for claude-flow MCP server

Usage:
  --report-task     --task-id <id> --success <bool> [--quality <0-1>] [--task-desc <text>]
  --report-command  --command <cmd> --exit-code <n>
  --report-error   --pattern <type> --command <cmd> [--severity s]
`);
}

main().catch(e => { console.error(e.message); process.exit(1); });
