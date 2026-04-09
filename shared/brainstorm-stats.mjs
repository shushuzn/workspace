#!/usr/bin/env node
/**
 * Maintain running statistics for brainstorm metacognition
 * Updated after each batch, read by retrospective for fast stats
 */
import { readFileSync, writeFileSync, existsSync } from 'fs';

const HISTORY_FILE = '.omc/innovation/brainstorm-metacognition.jsonl';
const STATS_FILE = '.omc/innovation/brainstorm-stats.json';

function readHistory() {
  if (!existsSync(HISTORY_FILE)) return [];
  const lines = readFileSync(HISTORY_FILE, 'utf8').split('\n').filter(Boolean);
  return lines.map(l => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);
}

function computeStats(history) {
  const last3 = history.slice(-3);
  const gateTotals = {};
  const projectCounts = {};

  for (const h of history) {
    for (const [gate, count] of Object.entries(h.gate_failures || {})) {
      gateTotals[gate] = (gateTotals[gate] || 0) + count;
    }
    for (const p of h.high_score_projects || []) {
      projectCounts[p] = (projectCounts[p] || 0) + 1;
    }
  }

  const avgScores = last3.map(h => h.batch_avg_score);
  const trend = avgScores.length >= 2 ? avgScores[avgScores.length - 1] - avgScores[0] : 0;

  return {
    total_batches: history.length,
    last_3_avg_scores: avgScores,
    avg_score_trend: trend,
    total_gate_failures: gateTotals,
    project_counts: projectCounts,
    last_updated: new Date().toISOString()
  };
}

function main() {
  const history = readHistory();
  const stats = computeStats(history);
  writeFileSync(STATS_FILE, JSON.stringify(stats, null, 2), 'utf8');
  console.log('Stats updated:', stats.total_batches, 'batches');
}

main();
