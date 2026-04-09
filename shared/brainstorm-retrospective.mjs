#!/usr/bin/env node
/**
 * Brainstorm retrospective: after each batch, analyze results and suggest next steps.
 *
 * Reads brainstorm-metacognition.jsonl and generates actionable recommendations
 * for the next batch based on patterns in gate failures, low scores, and project coverage.
 */
import { readFileSync, existsSync } from 'fs';

const HISTORY_FILE = '.omc/innovation/brainstorm-metacognition.jsonl';
const STATS_FILE = '.omc/innovation/brainstorm-stats.json';
const IDEAS_FILE = '.omc/innovation/ideas.md';

function readStats() {
  if (!existsSync(STATS_FILE)) return null;
  try { return JSON.parse(readFileSync(STATS_FILE, 'utf8')); } catch { return null; }
}

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
  const stats = readStats();
  const history = stats ? null : readHistory(); // fallback to history if no stats
  const pool = readCurrentPool();
  const last3 = stats ? stats.last_3_avg_scores : history.slice(-3).map(h => h.batch_avg_score);

  console.log('╔══════════════════════════════════════════════════╗');
  console.log('║  Brainstorm Retrospective                     ║');
  console.log('╚══════════════════════════════════════════════════╝\n');

  const avgScores = last3 || [];

  // 1. Batch trend
  if (avgScores.length > 0) {
    const trend = avgScores[avgScores.length - 1] - avgScores[0];
    console.log(`[Trend] Last ${last3.length} batches avg score: ${avgScores.map(s => s.toFixed(1)).join(' → ')} ${trend >= 0 ? '↑' : '↓'}`);
  }

  // 2. Gate failure patterns (from precomputed stats)
  if (stats) {
    const sortedGates = Object.entries(stats.total_gate_failures).sort((a, b) => b[1] - a[1]);
    if (sortedGates.length > 0) {
      console.log('\n[Gate Failures]');
      for (const [gate, count] of sortedGates.slice(0, 3)) {
        console.log(`  ${gate}: ${count}x`);
      }
    }
    // 3. Project coverage (from precomputed stats)
    console.log('\n[Active Projects] (by appearance in high_score_projects)');
    for (const [p, c] of Object.entries(stats.project_counts).sort((a, b) => b[1] - a[1]).slice(0, 5)) {
      console.log(`  ${p}: ${c}x`);
    }
  } else {
    // Fallback: scan history
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
  }

  // 5. Pool status
  console.log(`\n[Pool] total:${pool.total} active:${pool.active} shipped:${pool.shipped} killed:${pool.killed}`);

  // 6. Next batch recommendations
  console.log('\n╔══════════════════════════════════════════════════╗');
  console.log('║  Next Batch Recommendations                    ║');
  console.log('╚══════════════════════════════════════════════════╝');

  const recs = [];
  const gf = stats ? stats.total_gate_failures : gateTotals;
  const pc = stats ? stats.project_counts : projectCounts;

  // Gate-based
  if (gf['Gate4b'] > 5) {
    recs.push({ priority: 'HIGH', text: 'Gate4b failures high: relax executable prefix for f:1-f:2 seeds or add more allowed prefixes' });
  }
  if (gf['Gate4c'] > 3) {
    recs.push({ priority: 'HIGH', text: 'Gate4c (node -e) still appearing: ensure all seeds use pre-created script approach' });
  }

  // Score trend
  if (avgScores.length >= 2) {
    const recentAvg = avgScores[avgScores.length - 1];
    if (recentAvg < 9) {
      recs.push({ priority: 'MED', text: 'Recent avg score < 9: focus on higher-benefit seeds (Benefit ≥ 3) with clear real-world use' });
    }
  }

  // Project gaps
  const coveredProjects = new Set(Object.keys(pc));
  const missingProjects = ['task-orchestrator', 'opencli', 'CLI-Anything', 'multi-agent-hub', 'wikipedia'].filter(p => !coveredProjects.has(p));
  if (missingProjects.length > 0) {
    recs.push({ priority: 'MED', text: `Projects without recent high-score seeds: ${missingProjects.join(', ')}` });
  }

  // Pool state
  if (pool.active === 0) {
    recs.push({ priority: 'HIGH', text: 'Pool empty: generate new batch immediately' });
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
