#!/usr/bin/env node
/**
 * feasibility-calibrator.mjs
 * Analyze past seeds to calibrate feasibility scoring
 * Usage: node feasibility-calibrator.mjs
 */
import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const IDEAS_FILE = join(__DIR, '..', '.omc', 'innovation', 'ideas.md');
const META_FILE = join(__DIR, '..', '.omc', 'innovation', 'brainstorm-metacognition.jsonl');

function readIdeas() {
  if (!existsSync(IDEAS_FILE)) return [];
  const content = readFileSync(IDEAS_FILE, 'utf8');
  const seeds = [];
  const lines = content.split('\n');
  for (const line of lines) {
    if (!line.includes('seed [brainstorm]')) continue;
    const shipMatch = line.match(/shipped:(\d{8})/);
    const fMatch = line.match(/\[f:(\d+)\]/);
    const feasInflateMatch = line.match(/feas_inflation:([^"\]]+)/);
    if (shipMatch && fMatch) {
      seeds.push({
        date: shipMatch[1],
        f: parseInt(fMatch[1]),
        feasInflate: feasInflateMatch ? feasInflateMatch[1] : null
      });
    }
  }
  return seeds;
}

function readMetacognition() {
  if (!existsSync(META_FILE)) return [];
  const lines = readFileSync(META_FILE, 'utf8').trim().split('\n');
  const entries = [];
  for (const line of lines) {
    try {
      entries.push(JSON.parse(line));
    } catch {}
  }
  return entries;
}

console.log('=== Feasibility Calibration Report ===\n');

const seeds = readIdeas();
const metacog = readMetacognition();

// Group by f score
const byF = {};
for (const s of seeds) {
  if (!byF[s.f]) byF[s.f] = { total: 0, inflated: 0, items: [] };
  byF[s.f].total++;
  if (s.feasInflate) {
    byF[s.f].inflated++;
    byF[s.f].items.push(s);
  }
}

console.log('【f:score 分布】');
for (const f of Object.keys(byF).sort((a, b) => a - b)) {
  const g = byF[f];
  const rate = ((g.inflated / g.total) * 100).toFixed(1);
  console.log(`  f:${f}: ${g.total} seeds, ${g.inflated} inflated (${rate}%)`);
}

console.log('\n【最近 metacognition 批次】');
for (const m of metacog.slice(-5)) {
  console.log(`  ${m.date}: avg=${m.batch_avg_score} self_assess=${m.self_assessment}`);
  if (m.gate_failures && Object.keys(m.gate_failures).length > 0) {
    console.log(`    gate_failures: ${JSON.stringify(m.gate_failures)}`);
  }
}

console.log('\n【Calibration 建议】');
const totalSeeds = seeds.length;
const totalInflated = seeds.filter(s => s.feasInflate).length;
const inflRate = totalInflated / totalSeeds;
if (inflRate > 0.2) {
  console.log('  ⚠️ 建议降低f评分准确性，当前虚高率', inflRate.toFixed(1));
} else {
  console.log('  ✅ f评分基本准确，虚高率低');
}
