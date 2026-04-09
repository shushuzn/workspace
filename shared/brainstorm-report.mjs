#!/usr/bin/env node
/** Analyze brainstorm-metacognition.jsonl for batch quality stats */
import { readFileSync } from 'fs';

const lines = readFileSync('.omc/innovation/brainstorm-metacognition.jsonl', 'utf8')
  .split('\n').filter(Boolean);
const batches = [];
for (const l of lines) {
  if (!l.trim()) continue;
  try { batches.push(JSON.parse(l)); }
  catch (e) { console.warn('Skipping bad line:', e.message); }
}
const avg = batches.reduce((a, b) => a + b.batch_avg_score, 0) / batches.length;

console.log('=== Brainstorm Metacognition ===');
console.log('Batches:', batches.length, '| Avg score:', avg.toFixed(1));

const failGate = {};
batches.forEach(b => {
  Object.entries(b.gate_failures || {}).forEach(([g, c]) => {
    failGate[g] = (failGate[g] || 0) + c;
  });
});
console.log('Gate failures:', JSON.stringify(failGate));

const shipped = batches.filter(b => b.self_assessment === 'pass').length;
console.log('Pass:', shipped, '/', batches.length);
