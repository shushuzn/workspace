#!/usr/bin/env node
/**
 * scripts/ci-pattern-graph.mjs
 * Pattern causal association graph — learns which patterns tend to occur together.
 *
 * Usage:
 *   node scripts/ci-pattern-graph.mjs              # show association graph
 *   node scripts/ci-pattern-graph.mjs detect <p> # which patterns precede/succeed <p>
 */
import { existsSync, readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PATTERN_FILE = join(__dirname, 'ci-failure-patterns.jsonl');
const STATE_FILE = join(__dirname, '..', 'ci-state.json');

function loadPatterns() {
  if (!existsSync(PATTERN_FILE)) return [];
  try {
    const content = readFileSync(PATTERN_FILE, 'utf8');
    return content.trim().split('\n').filter(Boolean).map(l => {
      try { return JSON.parse(l); } catch { return null; }
    }).filter(Boolean);
  } catch { return []; }
}

function loadDiagnosisLog() {
  if (!existsSync(STATE_FILE)) return [];
  try {
    const state = JSON.parse(readFileSync(STATE_FILE, 'utf8'));
    return state.patterns?.diagnosisLog || [];
  } catch { return []; }
}

function buildCooccurrence() {
  const log = loadDiagnosisLog();
  const cooc = {};
  const temporal = {};

  for (const entry of log) {
    const matched = entry.patterns || [];
    if (matched.length < 2) continue;

    for (let i = 0; i < matched.length; i++) {
      for (let j = i + 1; j < matched.length; j++) {
        const a = matched[i], b = matched[j];
        if (!cooc[a]) cooc[a] = {};
        if (!cooc[a][b]) cooc[a][b] = 0;
        cooc[a][b]++;
        if (!cooc[b]) cooc[b] = {};
        if (!cooc[b][a]) cooc[b][a] = 0;
        cooc[b][a]++;
      }
    }
  }

  for (let i = 1; i < log.length; i++) {
    const prev = log[i - 1].patterns || [];
    const curr = log[i].patterns || [];
    for (const a of prev) {
      for (const b of curr) {
        if (!temporal[a]) temporal[a] = { before: {}, after: {} };
        if (!temporal[a].after[b]) temporal[a].after[b] = 0;
        temporal[a].after[b]++;
        if (!temporal[b]) temporal[b] = { before: {}, after: {} };
        if (!temporal[b].before[a]) temporal[b].before[a] = 0;
        temporal[b].before[a]++;
      }
    }
  }

  return { cooc, temporal };
}

function getConfidence(p) {
  if (p.confirmations == null || p.rejections == null) return null;
  if (p.confirmations + p.rejections === 0) return null;
  return p.confirmations / (p.confirmations + p.rejections);
}

function detectCausalChain(targetPattern) {
  const { temporal } = buildCooccurrence();
  const causes = Object.entries(temporal[targetPattern]?.before || {})
    .sort((a, b) => b[1] - a[1]).filter(([, c]) => c >= 1)
    .map(([p, count]) => ({ pattern: p, count }));
  const effects = Object.entries(temporal[targetPattern]?.after || {})
    .sort((a, b) => b[1] - a[1]).filter(([, c]) => c >= 1)
    .map(([p, count]) => ({ pattern: p, count }));
  return { causes, effects, target: targetPattern };
}

function printGraph() {
  const { cooc, temporal } = buildCooccurrence();
  const patterns = loadPatterns();

  console.log('\n=== Pattern Association Graph ===\n');
  console.log('Co-occurrence (same CI run):\n');

  const patternNames = patterns.map(p => p.name);
  console.log('  ' + patternNames.map(n => n.substring(0, 12).padEnd(13)).join(''));
  console.log('  ' + '—'.repeat(patternNames.length * 13));

  for (const a of patternNames) {
    const row = patternNames.map(b => {
      const count = cooc[a]?.[b] || 0;
      if (a === b) return '     —    ';
      if (count === 0) return '         ';
      return `${count}x`.padEnd(13);
    }).join('');
    console.log(`  ${a.substring(0, 12).padEnd(12)} ${row}`);
  }

  console.log('\n--- Temporal chains ---\n');
  const links = [];
  for (const [a, data] of Object.entries(temporal)) {
    for (const [b, count] of Object.entries(data.after)) {
      if (count >= 1) links.push({ from: a, to: b, count });
    }
  }
  links.sort((a, b) => b.count - a.count);

  if (links.length === 0) {
    console.log('  (no data yet — diagnosis log empty)');
  } else {
    for (const { from, to, count } of links.slice(0, 10)) {
      console.log(`  ${from} → ${to}  [${count}x consecutive]`);
    }
  }

  console.log('\n--- High-confidence causal chains (confidence ≥ 70%) ---\n');
  const seen = new Set();
  let found = false;
  for (const { from, to, count } of links.slice(0, 8)) {
    if (seen.has(`${from}→${to}`)) continue;
    seen.add(`${from}→${to}`);
    const fromP = patterns.find(p => p.name === from);
    const conf = fromP ? getConfidence(fromP) : null;
    if (conf !== null && conf >= 0.7) {
      console.log(`  🔗 ${from} → ${to}  [confidence: ${(conf * 100).toFixed(0)}%, ${count}x]`);
      console.log(`     Fix: ${fromP?.fix || 'unknown'}`);
      found = true;
    }
  }
  if (!found) console.log('  (need more data or confirmations for high-confidence chains)');
  console.log();
}

async function main() {
  const [, , cmd, ...args] = process.argv;

  if (cmd === 'detect') {
    const name = args.join(' ');
    const result = detectCausalChain(name);
    console.log(`\n=== ${name} — Causal Analysis ===\n`);
    if (result.causes.length > 0) {
      console.log('  Likely caused BY:');
      for (const { pattern, count } of result.causes) {
        console.log(`    ← ${pattern} [${count}x consecutive]`);
      }
    }
    if (result.effects.length > 0) {
      console.log('\n  Likely leads TO:');
      for (const { pattern, count } of result.effects) {
        console.log(`    → ${pattern} [${count}x consecutive]`);
      }
    }
    if (result.causes.length === 0 && result.effects.length === 0) {
      console.log('  No causal links yet (need more diagnoses)');
    }
    console.log();
    return;
  }

  printGraph();
  console.log('Run: node scripts/ci-pattern-graph.mjs detect "<pattern>"  # analyze one pattern');
}

main().catch(e => { console.error(e); process.exit(1); });
