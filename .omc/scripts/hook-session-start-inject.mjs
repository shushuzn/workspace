#!/usr/bin/env node
/**
 * OMC Session Start Inject
 * Reads drain file → outputs context injection for Claude Code.
 *
 * SessionStart hook → this script → stdout injects context
 * Claude Code reads stdout → prepends MCP learning instructions to session context
 *
 * Also injects: periodic nudge + workflow patterns
 */
import { existsSync, readFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const STATE_DIR = resolve(__dirname, '../state');
const DRAIN_FILE = resolve(STATE_DIR, 'session-start-mcp-inject.md');
const NUDGE_FILE = resolve(STATE_DIR, 'session-nudge.md');
const WF_PATTERNS_FILE = resolve(__dirname, '../innovation/workflow-patterns.md');

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

  // 3. Workflow patterns (from workflow detector)
  if (existsSync(WF_PATTERNS_FILE)) {
    const content = readFileSync(WF_PATTERNS_FILE, 'utf-8').trim();
    if (content) {
      parts.push(`## Detected Workflow Patterns\n\n${content}`);
    }
  }

  // 4. Pending insight actions (from omc-insight-action --pickup)
  const PENDING_FILE = resolve(STATE_DIR, 'pending-actions.md');
  if (existsSync(PENDING_FILE)) {
    const content = readFileSync(PENDING_FILE, 'utf-8').trim();
    if (content) {
      parts.push(`## Pending Insight Actions\n\n${content}\n\nRun each action and mark done with:\n\`node D:/OpenClaw/workspace/.omc/scripts/omc-insight-action.mjs --done <id>\``);
    }
  }

  if (parts.length === 0) return; // Nothing to inject

  const combined = parts.join('\n\n---\n\n');

  // Claude Code reads stdout as systemMessage
  const output = { systemMessage: combined };
  console.log(JSON.stringify(output));
}

main().catch(() => {}); // Never fail
