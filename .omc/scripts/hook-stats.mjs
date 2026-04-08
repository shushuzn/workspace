#!/usr/bin/env node
/**
 * OMC Unified State Stats
 * Reads all critical state files → outputs single dashboard line.
 * Replaces: ls/cat/tail/wc/node --stats for 10 separate state files.
 */
import { existsSync, readFileSync, readdirSync, statSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const STATE_DIR = resolve(__dirname, '../state');

function getSize(p) {
  try { return statSync(p).size; } catch { return 0; }
}
function getLines(p) {
  try { return readFileSync(p, 'utf-8').split('\n').filter(Boolean).length; } catch { return 0; }
}
function getAge(p) {
  try { const mtime = statSync(p).mtimeMs; return ((Date.now() - mtime) / 60000).toFixed(1) + 'm ago'; } catch { return '?'; }
}

function stat(file, size, lines, age) {
  return `${file}: ${size}B ${lines}L ${age}`;
}

async function main() {
  const d = STATE_DIR;
  const entries = {};

  // Core state files (always present)
  const files = [
    'hook-audit.jsonl', 'mcp-learn-queue.jsonl', 'session-start-mcp-inject.md',
    'insight-gen-manifest.json', 'insight-verifications.md', 'pending-actions.md',
    'workflow-detector-state.json', 'auto-seed-counter.json',
    'session-nudge.md', 'session-insights.md',
  ];

  const lines = [];
  for (const f of files) {
    const p = resolve(d, f);
    if (existsSync(p)) {
      const size = getSize(p);
      const lines2 = getLines(p);
      const age = getAge(p);
      lines.push(stat(f, size, lines2, age));
    }
  }

  // sessions dir count
  const sessionsDir = resolve(d, 'sessions');
  if (existsSync(sessionsDir)) {
    const count = readdirSync(sessionsDir).length;
    lines.push(`sessions/: ${count} sessions ${getAge(sessionsDir)}`);
  }

  // Summary line
  const totalSize = lines.reduce((acc, l) => {
    const m = l.match(/: (\d+)B/);
    return acc + (m ? parseInt(m[1]) : 0);
  }, 0);

  console.log(`[omc-stats] ${new Date().toISOString().slice(11, 19)} | ${lines.join(' | ')} | total:${totalSize}B`);
}

main().catch(() => {});
