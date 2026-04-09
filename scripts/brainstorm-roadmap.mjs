#!/usr/bin/env node
/**
 * scripts/brainstorm-roadmap.mjs
 * Shows how shipped seeds build on each other to evolve project capabilities.
 * Usage:
 *   node scripts/brainstorm-roadmap.mjs              # view full roadmap
 *   node scripts/brainstorm-roadmap.mjs --project <name>   # filter by project
 *   node scripts/brainstorm-roadmap.mjs --json         # JSON output for scripts
 */
import { readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const IDEAS_PATH = join(__DIR, '..', '.omc', 'innovation', 'ideas.md');

const args = process.argv.slice(2);
const projectFilter = args.includes('--project') ? args[args.indexOf('--project') + 1] : null;
const jsonMode = args.includes('--json');
const daysIdx = args.indexOf('--days');
const daysLimit = daysIdx !== -1 ? parseInt(args[daysIdx + 1], 10) : 0;

const content = readFileSync(IDEAS_PATH, 'utf-8');
const lines = content.split('\n');

const seeds = [];
let i = 0;
while (i < lines.length) {
  const line = lines[i];
  const headerMatch = line.match(/^- \[(\d{4}-\d{2}-\d{2}|\d{8})\] STAGE \[([^\]]+)\] \[score:(\d+×\d+=\d+)\] \[f:(\d+)\](?: \[focus:([^\]]+)\])?(?: \[angle:([^\]]+)\])?/);
  if (!headerMatch) { i++; continue; }

  const [, date, source, scoreStr, feas, focus, angle] = headerMatch;
  const rawScoreStr = line.match(/\[score:([^\]]+)\]/)?.[1] || scoreStr;
  const scoreMatch = scoreStr.match(/(\d+)[×x](\d+)=(\d+)/);
  const benefit = scoreMatch ? parseInt(scoreMatch[1], 10) : 0;
  const feasNum = scoreMatch ? parseInt(scoreMatch[2], 10) : 0;
  const score = scoreMatch ? parseInt(scoreMatch[3], 10) : 0;

  // Collect body
  const bodyLines = [];
  let j = i + 1;
  while (j < lines.length && lines[j].match(/^\s{2}/)) {
    bodyLines.push(lines[j].replace(/^\s{2}/, ''));
    j++;
  }
  const bodyText = bodyLines.join('\n');

  const shippedMatch = line.match(/shipped:(\d{4}-\d{2}-\d{2}|\d{8})/) || bodyText.match(/shipped:(\d{4}-\d{2}-\d{2}|\d{8})/);
  const killedMatch = line.match(/killed:(\d{4}-\d{2}-\d{2}|\d{8})/) || bodyText.match(/killed:(\d{4}-\d{2}-\d{2}|\d{8})/);
  const shipped = !!shippedMatch;
  const killed = !!killedMatch;

  // Extract description (first line before |)
  const descMatch = bodyText.match(/description:\s*(.+?)(?:\s*\| benefit:|$)/s);
  const desc = descMatch ? descMatch[1].trim() : line.replace(/^\s*/, '').split('|')[0].trim();

  // Extract project: first try [focus:PROJECT], then → separator in desc
  let project = focus || null;
  if (!project) {
    const arrowMatch = desc.match(/→(\w[\w-]*)/);
    if (arrowMatch) project = arrowMatch[1];
  }
  if (!project) {
    const knownProjects = ['wikipedia', 'task-orchestrator', 'opencli', 'CLI-Anything', 'multi-agent-hub', 'rl-trading', 'conceptual-distance-explorer'];
    for (const p of knownProjects) {
      if (desc.includes(p)) { project = p; break; }
    }
  }

  // Extract benefit
  const benefitMatch = bodyText.match(/\| benefit:\s*(.+?)(?:\s*\| reason:|$)/s) || bodyText.match(/benefit:\s*(.+?)(?:\s*\|)/s);
  const benefitText = benefitMatch ? benefitMatch[1].trim() : '';

  // Extract reason
  const reasonMatch = bodyText.match(/\| reason:\s*(.+?)(?:\s*\| approach:|$)/s) || bodyText.match(/reason:\s*(.+?)(?:\s*\|)/s);
  const reasonText = reasonMatch ? reasonMatch[1].trim() : '';

  seeds.push({
    date: shippedMatch?.[1] || killedMatch?.[1] || date,
    source, score, benefit, feas: parseInt(feas), focus, angle, shipped, killed,
    desc, benefitText, reasonText, project,
    lineIdx: i, bodyLines
  });
  i = j;
}

// Filter: shipped only
const shipped = seeds.filter(s => s.shipped);
if (projectFilter) {
  shipped.filter(s => s.focus === projectFilter);
}

// Filter by days if --days specified (compare YYYYMMDD integers)
const cutoffDate = daysLimit > 0
  ? parseInt(new Date(Date.now() - daysLimit * 24 * 60 * 60 * 1000).toISOString().slice(0, 10).replace(/-/g, ''), 10)
  : null;
const dateFiltered = cutoffDate !== null
  ? shipped.filter(s => parseInt(s.date.replace(/-/g, ''), 10) >= cutoffDate)
  : shipped;

if (jsonMode) {
  console.log(JSON.stringify(dateFiltered, null, 2));
  process.exit(0);
}

// ── Build Project Timeline ───────────────────────────────────────────────────
const byProject = {};
for (const s of dateFiltered) {
  const proj = s.project || 'ws-level';
  if (!byProject[proj]) byProject[proj] = [];
  byProject[proj].push(s);
}

console.log('\n=== Brainstorm Roadmap ===\n');
console.log('Shipped seeds: ' + dateFiltered.length + ' | Projects: ' + Object.keys(byProject).length + '\n');

// Per-project roadmap
for (const [project, projectSeeds] of Object.entries(byProject).sort((a, b) => b[1].length - a[1].length)) {
  if (projectFilter && project !== projectFilter) continue;

  const totalScore = projectSeeds.reduce((sum, s) => sum + s.score, 0);
  const avgScore = (totalScore / projectSeeds.length).toFixed(1);
  const focusCount = projectSeeds.filter(s => s.focus).length;
  const wsCount = projectSeeds.length - focusCount;

  console.log(`## ${project} (${projectSeeds.length} seeds | avg score: ${avgScore})`);
  if (focusCount > 0 && wsCount > 0) console.log(`   focus: ${focusCount} | ws-level: ${wsCount}`);

  // Show seeds chronologically
  for (const s of projectSeeds.sort((a, b) => a.date.localeCompare(b.date))) {
    const dateStr = s.date.replace(/^(\d{4})(\d{2})(\d{2})$/, '$2/$3');
    const badge = s.angle ? `[${s.angle}]` : '';
    console.log(`  [${dateStr}] score:${s.score} ${badge} ${s.desc.slice(0, 60)}`);
    if (s.benefitText) console.log(`    → ${s.benefitText.slice(0, 80)}`);
  }
  console.log('');
}

// ── Capability Chain Analysis ────────────────────────────────────────────────
// Find seeds that enabled other seeds (reason references previous work)
console.log('## Capability Chains (reason referencing other projects)\n');
const chains = [];
for (const s of dateFiltered) {
  const refs = [];
  // Check if reason mentions another project
  for (const [proj] of Object.entries(byProject)) {
    if (proj !== s.focus && s.reasonText.toLowerCase().includes(proj.toLowerCase())) {
      refs.push(proj);
    }
  }
  if (refs.length > 0) {
    chains.push({ seed: s, refs });
  }
}
if (chains.length === 0) {
  console.log('  (no cross-project references found)');
} else {
  for (const { seed, refs } of chains) {
    console.log(`  "${seed.desc.slice(0, 50)}..."`);
    console.log(`    enabled by: ${refs.join(', ')}`);
  }
}

// ── Stats ───────────────────────────────────────────────────────────────────
console.log('\n## Roadmap Stats\n');
const scoreBuckets = { '16+': 0, '12-15': 0, '9-11': 0, '6-8': 0, '<6': 0 };
for (const s of dateFiltered) {
  if (s.score >= 16) scoreBuckets['16+']++;
  else if (s.score >= 12) scoreBuckets['12-15']++;
  else if (s.score >= 9) scoreBuckets['9-11']++;
  else if (s.score >= 6) scoreBuckets['6-8']++;
  else scoreBuckets['<6']++;
}
console.log('Score Distribution:');
for (const [bucket, count] of Object.entries(scoreBuckets)) {
  if (count > 0) console.log('  ' + bucket.padEnd(6) + ': ' + '█'.repeat(count) + ' (' + count + ')');
}

const feasBuckets = { f5: 0, f4: 0, f3: 0, f2: 0, f1: 0 };
for (const s of shipped) feasBuckets[{ 5: 'f5', 4: 'f4', 3: 'f3', 2: 'f2', 1: 'f1' }[s.feas] || 'f3']++;
console.log('\nFeasibility Distribution:');
for (const [f, count] of [['f5', feasBuckets.f5], ['f4', feasBuckets.f4], ['f3', feasBuckets.f3], ['f2', feasBuckets.f2], ['f1', feasBuckets.f1]]) {
  if (count > 0) console.log('  ' + f.padEnd(3) + ': ' + '█'.repeat(count) + ' (' + count + ')');
}
