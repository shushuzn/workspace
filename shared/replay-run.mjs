#!/usr/bin/env node
/**
 * Replay adapter decisions from history
 * Given a task type, finds best adapter and re-runs
 * Usage: node shared/replay-run.mjs <taskType>
 */
import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const HIST_FILE = join(__DIR, '..', '80-PROJECTS', 'task-orchestrator', 'exec-history.jsonl');

function getBestForTaskType(taskType) {
  if (!existsSync(HIST_FILE)) return null;
  const lines = readFileSync(HIST_FILE, 'utf8').split('\n').filter(Boolean);
  const scores = {};
  for (const l of lines) {
    try {
      const e = JSON.parse(l);
      if (e.taskType !== taskType) continue;
      if (!scores[e.adapterId]) scores[e.adapterId] = { success: 0, total: 0 };
      scores[e.adapterId].total++;
      if (e.success) scores[e.adapterId].success++;
    } catch {}
  }
  let best = null, bestScore = -1;
  for (const [id, s] of Object.entries(scores)) {
    const rate = s.success / s.total;
    if (rate > bestScore) { bestScore = rate; best = { adapterId: id, successRate: rate, count: s.total }; }
  }
  return best;
}

const taskType = process.argv[2] || 'browse';
const best = getBestForTaskType(taskType);
if (!best) {
  console.log(`No history for: ${taskType}`);
  process.exit(1);
}
console.log(`Best adapter for "${taskType}": ${best.adapterId}`);
console.log(`  Success rate: ${(best.successRate * 100).toFixed(1)}% (${best.count} runs)`);
console.log(`\nTo re-run: task orchestrator --adapter ${best.adapterId} "${taskType}..."`);
