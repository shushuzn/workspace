#!/usr/bin/env node
/** Replay session operations from transcript */
import { readdirSync, existsSync } from 'fs';
import { join } from 'path';

const PROJECTS_DIR = '.claude/projects';

let sessions = [];
try {
  if (existsSync(PROJECTS_DIR)) {
    sessions = readdirSync(PROJECTS_DIR).filter(f => f.endsWith('.jsonl'));
  }
} catch (e) {}

console.log('=== Session Replay ===');
console.log('Transcript files:', sessions.length);
sessions.slice(0, 5).forEach(s => console.log('  -', s));
console.log('\n[PROTOTYPE] Full implementation parses tool call sequences');
