#!/usr/bin/env node
/**
 * scripts/audit-shipped.mjs
 * Audits ideas.md shipped seeds, reports per-batch statistics.
 * Usage: node scripts/audit-shipped.mjs [--json]
 */
import { readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const IDEAS_PATH = join(__DIR, '..', 'knowledge', 'wikipedia', '.omc', 'innovation', 'ideas.md');

const jsonMode = process.argv.includes('--json');

const content = readFileSync(IDEAS_PATH, 'utf-8');
const lines = content.split('\n');

const shippedByDate = {};
const killedByDate = {};
let totalSeeds = 0;

let i = 0;
while (i < lines.length) {
  const line = lines[i];
  const headerMatch = line.match(/^- \[(\d{8})\] seed \[brainstorm\]/);
  if (!headerMatch) { i++; continue; }

  const bodyLines = [];
  let j = i + 1;
  while (j < lines.length && lines[j].match(/^\s{2}/)) {
    bodyLines.push(lines[j]);
    j++;
  }
  const bodyText = bodyLines.join('\n').replace(/^\s{2}/gm, '');

  const date = headerMatch[1];
  const scoreMatch = line.match(/\[score:(\d+)x(\d+)\]/);
  const benefit = scoreMatch ? parseInt(scoreMatch[1], 10) : 0;
  const feas = scoreMatch ? parseInt(scoreMatch[2], 10) : 0;
  const score = benefit * feas;

  const shippedMatch = line.match(/\| shipped:(\d{8})/) || bodyText.match(/\| shipped:(\d{8})/);
  const killedMatch = line.match(/killed:(\d{8})\s+([^|]+)/) || bodyText.match(/killed:(\d{8})\s+([^|]+)/);
  totalSeeds++;

  if (shippedMatch) {
    const d = shippedMatch[1];
    if (!shippedByDate[d]) shippedByDate[d] = [];
    shippedByDate[d].push({ date, score, benefit, feas, lineIdx: i });
  }
  if (killedMatch) {
    const d = killedMatch[1];
    const reason = killedMatch[2].trim();
    if (!killedByDate[d]) killedByDate[d] = [];
    killedByDate[d].push({ date, score, reason, lineIdx: i });
  }

  i = j;
}

const allDates = [...new Set([...Object.keys(shippedByDate), ...Object.keys(killedByDate)])].sort();

if (jsonMode) {
  const batches = allDates.map(d => {
    const shipped = shippedByDate[d] || [];
    const killed = killedByDate[d] || [];
    const seeds = shipped.length + killed.length;
    const scores = shipped.map(s => s.score);
    const avgScore = scores.length > 0 ? scores.reduce((a, b) => a + b, 0) / scores.length : 0;
    const topScore = scores.length > 0 ? Math.max(...scores) : 0;
    const killedReasons = {};
    killed.forEach(k => { killedReasons[k.reason] = (killedReasons[k.reason] || 0) + 1; });
    return { date: d, seeds, shipped: shipped.length, killed: killed.length, avgScore: Math.round(avgScore * 10) / 10, topScore, killedReasons };
  });
  console.log(JSON.stringify({ total: totalSeeds, batches }, null, 2));
} else {
  console.log(`\n=== Shipped Seeds Audit ===`);
  console.log(`Total seeds: ${totalSeeds} | Tracked batches: ${allDates.length}`);
  console.log('');
  for (const d of allDates) {
    const shipped = shippedByDate[d] || [];
    const killed = killedByDate[d] || [];
    const seeds = shipped.length + killed.length;
    const scores = shipped.map(s => s.score);
    const avgScore = scores.length > 0 ? scores.reduce((a, b) => a + b, 0) / scores.length : 0;
    const topScore = scores.length > 0 ? Math.max(...scores) : 0;
    const rate = seeds > 0 ? Math.round(shipped.length / seeds * 100) : 0;
    const killedReasons = {};
    killed.forEach(k => { killedReasons[k.reason] = (killedReasons[k.reason] || 0) + 1; });
    const reasonStr = Object.keys(killedReasons).length > 0
      ? Object.entries(killedReasons).map(([r, n]) => `${r}(${n})`).join(', ')
      : '-';
    console.log(`${d} | seeds:${seeds} shipped:${shipped.length} rate:${rate}% avg:${avgScore.toFixed(1)} top:${topScore} | killed: ${reasonStr}`);
  }
}
