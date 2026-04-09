#!/usr/bin/env node
/**
 * Replay session operations from transcript JSONL
 * Parses tool call sequences from Claude Code transcript files
 */
import { readFileSync, readdirSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const PROJECTS_DIR = join(process.env.HOME || process.env.USERPROFILE, '.claude', 'projects', 'D--OpenClaw-workspace');

// Find most recent transcript
let transcripts = [];
try {
  if (existsSync(PROJECTS_DIR)) {
    transcripts = readdirSync(PROJECTS_DIR)
      .filter(f => f.endsWith('.jsonl'))
      .map(f => ({ name: f, path: join(PROJECTS_DIR, f) }))
      .sort((a, b) => b.name.localeCompare(a.name));
  }
} catch (e) {}

console.log('=== Session Replay ===');
console.log('Project dir:', PROJECTS_DIR);
console.log('Transcripts:', transcripts.length);

if (transcripts.length === 0) {
  console.log('No transcripts found');
  process.exit(0);
}

// Show most recent
const recent = transcripts.slice(0, 3);
console.log('\nMost recent:');
for (const t of recent) {
  let size = 0;
  try { size = readFileSync(t.path, 'utf8').length; } catch {}
  console.log(`  ${t.name} (${(size/1024).toFixed(1)}KB)`);
}

// Parse and display tool calls from most recent
if (transcripts.length > 0) {
  const latest = transcripts[0];
  try {
    const content = readFileSync(latest.path, 'utf8');
    const lines = content.split('\n').filter(Boolean);
    console.log(`\nLatest transcript: ${latest.name}`);
    console.log('Lines:', lines.length);

    // Count tool types
    const toolCounts = {};
    for (const line of lines.slice(0, 100)) {
      try {
        const entry = JSON.parse(line);
        if (entry.type === 'user' || entry.type === 'assistant') {
          const msg = entry.message || entry.text || '';
          // Extract tool names
          const matches = msg.matchAll(/(?:Read|Edit|Write|Bash|Grep|Glob|Search|List|TodoWrite|TaskCreate)\s/g);
          for (const m of matches) {
            toolCounts[m[0].trim()] = (toolCounts[m[0].trim()] || 0) + 1;
          }
        }
      } catch {}
    }
    console.log('\nTool usage (first 100 lines):');
    for (const [tool, count] of Object.entries(toolCounts).sort((a,b) => b[1]-a[1]).slice(0, 10)) {
      console.log(`  ${tool}: ${count}`);
    }
  } catch (e) {
    console.error('Error:', e.message);
  }
}

console.log('\n[PROTOTYPE] Full replay requires step-by-step re-execution');
