#!/usr/bin/env node
/**
 * notepad-prune.mjs
 * Delete Priority Context entries older than 7 days from .omc/notepad.md
 * Only prunes lines within ## Priority Context ... ## Working Memory section
 */
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const NOTEPAD = join(__DIR, '..', '.omc', 'notepad.md');

if (!existsSync(NOTEPAD)) {
  console.error('[notepad-prune] notepad.md not found');
  process.exit(1);
}

const content = readFileSync(NOTEPAD, 'utf8');
const lines = content.split('\n');
const now = Date.now();
const SEVEN_DAYS = 7 * 24 * 60 * 60 * 1000;

let inPriority = false;
let removed = 0;
const newLines = lines.map(line => {
  const trimmed = line.trim();
  if (trimmed === '## Priority Context') { inPriority = true; return line; }
  if (trimmed === '## Working Memory') { inPriority = false; return line; }
  if (trimmed.startsWith('## ')) { inPriority = false; return line; }

  if (inPriority && (trimmed.startsWith('⚡') || trimmed.startsWith('⚠️'))) {
    // Match compact date: 20260409 or ISO date: 2026-04-09
    const dateMatch = trimmed.match(/\b(\d{8}|\d{4}-\d{2}-\d{2})\b/);
    if (!dateMatch) return line;
    const dateStr = dateMatch[1];
    const entryDate = dateStr.length === 8
      ? new Date(`${dateStr.slice(0, 4)}-${dateStr.slice(4, 6)}-${dateStr.slice(6, 8)}`).getTime()
      : new Date(dateStr).getTime();
    if (isNaN(entryDate)) return line;
    if (now - entryDate > SEVEN_DAYS) { removed++; return null; }
  }
  return line;
}).filter(line => line !== null);

if (removed > 0) {
  writeFileSync(NOTEPAD, newLines.join('\n'), 'utf8');
  console.log(`[notepad-prune] Removed ${removed} expired entries`);
} else {
  console.log('[notepad-prune] No expired entries found');
}
process.exit(0);
