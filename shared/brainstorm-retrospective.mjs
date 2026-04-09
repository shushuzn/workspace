#!/usr/bin/env node
/**
 * Brainstorm retrospective: after each batch, analyze results and suggest next steps.
 *
 * Reads brainstorm-metacognition.jsonl and generates actionable recommendations
 * for the next batch based on patterns in gate failures, low scores, and project coverage.
 */
import { readFileSync, existsSync } from 'fs';

const HISTORY_FILE = '.omc/innovation/brainstorm-metacognition.jsonl';
const IDEAS_FILE = '.omc/innovation/ideas.md';

function readHistory() {
  if (!existsSync(HISTORY_FILE)) return [];
  const lines = readFileSync(HISTORY_FILE, 'utf8').split('\n').filter(Boolean);
  return lines.map(l => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);
}

function readCurrentPool() {
  if (!existsSync(IDEAS_FILE)) return { total: 0, active: 0, shipped: 0, killed: 0 };
  const lines = readFileSync(IDEAS_FILE, 'utf8').split('\n');
  let shipped = 0, killed = 0, active = 0;
  for (const l of lines) {
    if (l.match(/shipped:/)) shipped++;
    else if (l.match(/killed:/)) killed++;
    else if (l.match(/^- \[/)) active++;
  }
  return { total: shipped + killed + active, active, shipped, killed };
}

function analyze() {
  const history = readHistory();
  const pool = readCurrentPool();
  const last3 = history.slice(-3);

  console.log('╔══════════════════════════════════════════════════╗');
  console.log('║  Brainstorm Retrospective                     ║');
  console.log('╚══════════════════════════════════════════════════╝\n');

  const avgScores = last3.length > 0 ? last3.map(h => h.batch_avg_score) : [];

  // 1. Batch trend
  if (avgScores.length > 0) {
    const trend = avgScores[avgScores.length - 1] - avgScores[0];
    console.log(`[Trend] Last ${last3.length} batches avg score: ${avgScores.map(s => s.toFixed(1)).join(' → ')} ${trend >= 0 ? '↑' : '↓'}`);
  }

  // 2. Gate failure patterns
  const gateTotals = {};
  for (const h of history) {
    for (const [gate, count] of Object.entries(h.gate_failures || {})) {
      gateTotals[gate] = (gateTotals[gate] || 0) + count;
    }
  }
  const sortedGates = Object.entries(gateTotals).sort((a, b) => b[1] - a[1]);
  if (sortedGates.length > 0) {
    console.log('\n[Gate Failures]');
    for (const [gate, count] of sortedGates.slice(0, 3)) {
      console.log(`  ${gate}: ${count}x`);
    }
  }

  // 3. Project coverage
  const projectCounts = {};
  for (const h of history) {
    for (const p of h.high_score_projects || []) {
      projectCounts[p] = (projectCounts[p] || 0) + 1;
    }
  }
  console.log('\n[Active Projects] (by appearance in high_score_projects)');
  for (const [p, c] of Object.entries(projectCounts).sort((a, b) => b[1] - a[1]).slice(0, 5)) {
    console.log(`  ${p}: ${c}x`);
  }

  // 4. Low-score angles
  const lowAngles = {};
  for (const h of history) {
    for (const a of h.low_score_angles || []) {
      lowAngles[a] = (lowAngles[a] || 0) + 1;
    }
  }
  if (Object.keys(lowAngles).length > 0) {
    console.log('\n[Low Score Angles] (avoid or restructure)');
    for (const [a, c] of Object.entries(lowAngles)) {
      console.log(`  ${a}: ${c}x`);
    }
  }

  // 5. Pool status
  console.log(`\n[Pool] total:${pool.total} active:${pool.active} shipped:${pool.shipped} killed:${pool.killed}`);

  // 6. Next batch recommendations
  console.log('\n╔══════════════════════════════════════════════════╗');
  console.log('║  Next Batch Recommendations                    ║');
  console.log('╚══════════════════════════════════════════════════╝');

  const recs = [];

  // Gate-based
  if (gateTotals['Gate4b'] > 5) {
    recs.push({ priority: 'HIGH', text: 'Gate4b failures high: relax executable prefix for f:1-f:2 seeds or add more allowed prefixes' });
  }
  if (gateTotals['Gate4c'] > 3) {
    recs.push({ priority: 'HIGH', text: 'Gate4c (node -e) still appearing: ensure all seeds use pre-created script approach' });
  }

  // Score trend
  if (last3.length >= 2) {
    const recentAvg = avgScores[avgScores.length - 1];
    if (recentAvg < 9) {
      recs.push({ priority: 'MED', text: 'Recent avg score < 9: focus on higher-benefit seeds (Benefit ≥ 3) with clear real-world use' });
    }
  }

  // Project gaps
  const coveredProjects = new Set(Object.keys(projectCounts));
  const missingProjects = ['task-orchestrator', 'opencli', 'CLI-Anything', 'multi-agent-hub', 'wikipedia'].filter(p => !coveredProjects.has(p));
  if (missingProjects.length > 0) {
    recs.push({ priority: 'MED', text: `Projects without recent high-score seeds: ${missingProjects.join(', ')}` });
  }

  // Pool state
  if (pool.active === 0) {
    recs.push({ priority: 'HIGH', text: 'Pool empty: generate new batch immediately' });
  }

  // Low angle check
  if (Object.keys(lowAngles).length > 0) {
    const worstAngle = Object.entries(lowAngles).sort((a, b) => b[1] - a[1])[0];
    recs.push({ priority: 'MED', text: `Angle "${worstAngle[0]}" repeatedly low-score: skip or restructure before next batch` });
  }

  // F:1 seed gap
  const f1Seeds = history.reduce((sum, h) => {
    // Count seeds with score indicating f:1 (score 1-2)
    return sum + (h.batch_seed_count >= 1 ? 0 : 0);
  }, 0);
  const hasRecentF1 = last3.some(h => h.batch_seed_count > 0 && h.self_assessment !== 'fail');
  if (!hasRecentF1) {
    recs.push({ priority: 'MED', text: 'No f:1 (exploration) seeds in recent batches: add complex architecture idea' });
  }

  if (recs.length === 0) {
    console.log('\n  [OK] No critical issues found. Continue normal batch.');
  }

  for (const r of recs) {
    const icon = r.priority === 'HIGH' ? '🔴' : '🟡';
    console.log(`\n  ${icon} [${r.priority}] ${r.text}`);
  }

  console.log('');
}

analyze();
