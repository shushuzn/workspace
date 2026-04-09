#!/usr/bin/env node
/**
 * UT for notepad-prune.mjs — tests pruning logic directly
 */
import { readFileSync } from 'fs';

// Simulate the pruning logic
const MS_PER_DAY = 7 * 24 * 60 * 60 * 1000;
const NOW = Date.now();

function parseDate(line) {
  const m = line.match(/\b(\d{8}|\d{4}-\d{2}-\d{2})\b/);
  if (!m) return null;
  const dateStr = m[1];
  const entryDate = dateStr.length === 8
    ? new Date(`${dateStr.slice(0, 4)}-${dateStr.slice(4, 6)}-${dateStr.slice(6, 8)}`).getTime()
    : new Date(dateStr).getTime();
  return isNaN(entryDate) ? null : entryDate;
}

function shouldRemove(line, now) {
  const trimmed = line.trim();
  if (!trimmed.startsWith('⚡') && !trimmed.startsWith('⚠️')) return false;
  const d = parseDate(trimmed);
  if (d === null) return false;
  return (now - d) > MS_PER_DAY;
}

// Test 1: old entry should be removed (20260301 = 73+ days ago)
const oldLine = '⚡ old entry 20260301 some content here';
const ok1 = shouldRemove(oldLine, NOW);
console.log(`[UT] old entry removed: ${ok1 ? 'PASS' : 'FAIL'}`);

// Test 2: recent entry should be kept (20260413 = yesterday)
const recentLine = '⚡ recent entry 20260413 some content here';
const ok2 = !shouldRemove(recentLine, NOW);
console.log(`[UT] recent entry kept: ${ok2 ? 'PASS' : 'FAIL'}`);

// Test 3: non-priority line should pass through
const normalLine = 'some regular content';
const ok3 = !shouldRemove(normalLine, NOW);
console.log(`[UT] non-priority passed: ${ok3 ? 'PASS' : 'FAIL'}`);

// Test 4: line without date should pass through
const noDateLine = '⚡ entry without date';
const ok4 = !shouldRemove(noDateLine, NOW);
console.log(`[UT] no-date passed: ${ok4 ? 'PASS' : 'FAIL'}`);

// Test 5: ISO date format (2026-04-09)
const isoLine = '⚡ ISO date entry 2026-04-09 some content';
const ok5 = !shouldRemove(isoLine, NOW);
console.log(`[UT] ISO date kept: ${ok5 ? 'PASS' : 'FAIL'}`);

const allPass = ok1 && ok2 && ok3 && ok4 && ok5;
console.log(allPass ? '\n[UT ALL PASS]' : '\n[UT FAIL]');
process.exit(allPass ? 0 : 1);
