#!/usr/bin/env node
/**
 * brainstorm-trend.mjs — visualize brainstorm learning trends from metacognition JSONL
 * Usage: node shared/brainstorm-trend.mjs --init
 */
import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const META_FILE = join(__DIR, '..', '.omc', 'innovation', 'brainstorm-metacognition.jsonl');

function loadEntries() {
  if (!existsSync(META_FILE)) return [];
  const content = readFileSync(META_FILE, 'utf8');
  return content.trim().split('\n').filter(Boolean).map(l => {
    try { return JSON.parse(l); } catch { return null; }
  }).filter(Boolean);
}

function main() {
  const args = process.argv.slice(2);
  const mode = args[0];

  const entries = loadEntries();
  if (entries.length === 0) {
    console.log('[TREND] No metacognition entries found');
    return;
  }

  if (mode === '--init') {
    console.log('[TREND] Initialized trend tracking');
    console.log(`  Total batches: ${entries.length}`);
    const scores = entries.map(e => e.batch_avg_score).filter(Boolean);
    if (scores.length > 0) {
      const avg = scores.reduce((a, b) => a + b, 0) / scores.length;
      console.log(`  Avg score: ${avg.toFixed(1)}`);
    }
    return;
  }

  // Default: show trend
  console.log('=== Brainstorm Trend ===\n');
  for (const e of entries.slice(-10)) {
    const date = e.date || 'unknown';
    const score = e.batch_avg_score?.toFixed(1) || 'N/A';
    const assess = e.self_assessment || '?';
    console.log(`  ${date}  score:${score}  ${assess}`);
  }
}

main();
