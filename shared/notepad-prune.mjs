#!/usr/bin/env node
/** Auto-prune expired notepad priority entries (>7 days) */
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const NOTEPAD = join(__DIR, '..', '.omc', 'notepad.md');

console.log('=== Notepad Auto-Prune ===');

if (!existsSync(NOTEPAD)) {
  console.log('notepad.md not found');
  process.exit(0);
}

const content = readFileSync(NOTEPAD, 'utf8');
const lines = content.split('\n');
const now = Date.now();
const SEVEN_DAYS = 7 * 24 * 60 * 60 * 1000;

let removed = 0;
const newLines = lines.filter(line => {
  // Match timestamp in format: YYYY-MM-DD or similar
  const dateMatch = line.match(/\d{4}-\d{2}-\d{2}/);
  if (!dateMatch) return true;
  const entryDate = new Date(dateMatch[0]).getTime();
  if (now - entryDate > SEVEN_DAYS) {
    removed++;
    return false;
  }
  return true;
});

if (removed > 0) {
  writeFileSync(NOTEPAD, newLines.join('\n'), 'utf8');
  console.log('Removed', removed, 'expired entries');
} else {
  console.log('No expired entries found');
}
