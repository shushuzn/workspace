#!/usr/bin/env node
/**
 * OMC PreToolUse Block Hook
 * Blocks all tool execution when pending-actions are not empty.
 * This is the ONLY way to enforce blocking - prompt-based blocking is advisory only.
 */
import { existsSync, readFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PENDING_FILE = resolve(__dirname, '../state/pending-actions.md');

function readStdin() {
  return new Promise((resolve) => {
    let data = '';
    const timer = setTimeout(() => resolve({}), 500);
    process.stdin.setEncoding('utf8');
    process.stdin.on('data', (chunk) => { data += chunk; });
    process.stdin.on('end', () => { clearTimeout(timer); resolve(data); });
    process.stdin.on('error', () => { clearTimeout(timer); resolve({}); });
    if (process.stdin.isTTY) resolve({});
  });
}

async function main() {
  try {
    // Read stdin for hook input
    const stdinData = await readStdin();
    let toolName = 'unknown';
    try {
      if (stdinData?.trim()) {
        const input = JSON.parse(stdinData);
        toolName = input.tool_name || 'unknown';
      }
    } catch {}

    // Check pending actions
    if (existsSync(PENDING_FILE)) {
      const content = readFileSync(PENDING_FILE, 'utf-8').trim();
      if (content) {
        // Extract pending items for the error message
        const lines = content.split('\n').filter(l => l.trim());
        const items = lines.slice(0, 3).map(l => l.replace(/^\- \[ \]/, '').trim()).join(', ');
        const more = lines.length > 3 ? ` (+${lines.length - 3} more)` : '';

        console.error(JSON.stringify({
          hookSpecificOutput: {
            hookEventName: 'PreToolUse',
            permissionDecision: 'deny',
            permissionDecisionReason: `OMC: blocked - ${lines.length} pending action(s) not executed: ${items}${more}. Run: node .omc/scripts/omc-insight-action.mjs --done <id>`,
          }
        }, null, 0));
        process.exit(1);
      }
    }

    // No pending actions - allow
    process.exit(0);
  } catch {
    process.exit(0);
  }
}

main();
