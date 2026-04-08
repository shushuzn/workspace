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
const INSIGHTS_FILE = resolve(STATE_DIR, 'session-insights.md');
const VERIFY_FILE = resolve(STATE_DIR, 'insight-verifications.md');

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

  // 5. Unexecuted insights from session-insights.md (auto-trigger)
  if (existsSync(INSIGHTS_FILE)) {
    const content = readFileSync(INSIGHTS_FILE, 'utf-8');
    const lines = content.split('\n');
    const unexecuted = [];
    for (const line of lines) {
      if (!line.includes('✅ EXECUTED') && line.includes('### ')) {
        // Extract insight title
        const match = line.match(/^#{3}\s+\d+\.\s+(.+?)(\s+⚠|\s+✅|$)/);
        if (match) unexecuted.push(match[1].trim());
      }
    }
    if (unexecuted.length > 0) {
      parts.push(`## Unexecuted Insights (auto-detected)\n\n${unexecuted.map((t, i) => `${i + 1}. **${t}**`).join('\n')}\n\nGenerate execution plan for each unexecuted insight.`);
    }
  }

  // 6. Recent verification results (feedback loop)
  if (existsSync(VERIFY_FILE)) {
    const content = readFileSync(VERIFY_FILE, 'utf-8').trim();
    if (content) {
      parts.push(`## Recent Insight Verification Results\n\n${content}`);
    }
  }

  if (parts.length === 0) return; // Nothing to inject

  const combined = parts.join('\n\n---\n\n');

  // Claude Code reads stdout as systemMessage
  const output = { systemMessage: combined };
  console.log(JSON.stringify(output));
}

main().catch(() => {}); // Never fail
