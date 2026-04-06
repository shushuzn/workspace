/**
 * session-sprint.mjs
 * Generates a Markdown sprint report from recent sessions.
 * Run: node scripts/session-sprint.mjs
 */

import { readdirSync, readFileSync } from 'fs';
import { join, resolve } from 'path';

const SESSIONS_DIR = resolve('C:/Users/adm/.claude/projects/D--OpenClaw-workspace/30a5354-07bf-458f-bd49-8ef4fae73b5f');

let sessions = [];
try {
  const files = readdirSync(SESSIONS_DIR).filter(f => f.endsWith('.jsonl'));
  for (const file of files.slice(-7)) { // last 7 sessions
    const content = readFileSync(join(SESSIONS_DIR, file), 'utf8');
    const lines = content.split('\n').filter(Boolean);
    sessions.push(...lines);
  }
} catch {
  console.log('No session data found');
  process.exit(0);
}

const shipped = sessions.filter(l => l.includes('shipped')).length;
const seeds = sessions.filter(l => l.includes('[seed]')).length;
const date = new Date().toISOString().slice(0, 10);

console.log(`\n# Sprint Report — ${date}\n`);
console.log(`| Metric | Value |`);
console.log(`|--------|-------|`);
console.log(`| Sessions reviewed | ${sessions.length} |`);
console.log(`| Ideas shipped | ${shipped} |`);
console.log(`| Ideas generated | ${seeds} |`);
console.log(`\nGenerated: ${date}\n`);
