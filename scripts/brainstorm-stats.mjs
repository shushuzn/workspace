#!/usr/bin/env node
/**
 * scripts/brainstorm-stats.mjs
 * Visualizes brainstorm-metacognition.jsonl trends.
 * Usage: node scripts/brainstorm-stats.mjs
 */
import { readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const META_PATH = join(__DIR, '..', 'knowledge', 'wikipedia', '.omc', 'innovation', 'brainstorm-metacognition.jsonl');

const content = readFileSync(META_PATH, 'utf-8');
const lines = content.trim().split('\n').filter(Boolean);

const records = lines.map(l => {
  try { return JSON.parse(l); } catch { return null; }
}).filter(Boolean);

if (records.length === 0) {
  console.log('No metacognition data yet.');
  process.exit(0);
}

console.log('\n=== Brainstorm Metacognition Stats ===\n');

// Trend table
console.log('Batch Trend:');
console.log('Date       | Seeds | AvgScore | SelfAss | TopIssues');
console.log('-'.repeat(60));
records.forEach(r => {
  const issues = Object.entries(r.gate_failures || {}).slice(0,2).map(([k,v])=>`${k}:${v}`).join(',') || '-';
  console.log(`${r.date} | ${String(r.batch_seed_count).padStart(5)} | ${String(r.batch_avg_score).padStart(8)} | ${String(r.self_assessment).padStart(8)} | ${issues}`);
});

// Gate failure frequency
const gateFreq = {};
records.forEach(r => {
  Object.entries(r.gate_failures || {}).forEach(([gate, count]) => {
    gateFreq[gate] = (gateFreq[gate] || 0) + count;
  });
});
const gateSorted = Object.entries(gateFreq).sort((a,b)=>b[1]-a[1]);
console.log('\nGate Failure Frequency:');
gateSorted.forEach(([gate, count]) => {
  console.log(`  ${gate}: ${count}`);
});

// Self-assessment rate
const passCount = records.filter(r => r.self_assessment === 'pass').length;
console.log(`\nSelf-Assessment Pass Rate: ${passCount}/${records.length} (${Math.round(passCount/records.length*100)}%)`);
