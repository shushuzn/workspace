#!/usr/bin/env node
/**
 * Record and query adapter execution history
 *
 * executor.mjs calls this after each step to record:
 *   { taskType, adapterId, success, duration, timestamp }
 *
 * planner.mjs calls this before selecting an adapter to weight by history.
 */
import { readFileSync, writeFileSync, existsSync, appendFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const HISTORY_FILE = join(__DIR, '..', 'exec-history.jsonl');

/**
 * Record one execution result.
 * @param {string} taskType - e.g. "browse", "search", "compute"
 * @param {string} adapterId - e.g. "opencli", "cli-anything"
 * @param {boolean} success
 * @param {number} durationMs
 */
export function recordResult(taskType, adapterId, success, durationMs) {
  const entry = {
    taskType,
    adapterId,
    success,
    durationMs,
    timestamp: Date.now(),
  };
  appendFileSync(HISTORY_FILE, JSON.stringify(entry) + '\n', 'utf8');
  return entry;
}

/**
 * Get best adapter for a task type, weighted by success rate and recency.
 * Returns { adapterId, score, successRate, count }
 */
export function getBestAdapter(taskType) {
  if (!existsSync(HISTORY_FILE)) {
    return null;
  }
  const lines = readFileSync(HISTORY_FILE, 'utf8').split('\n').filter(Boolean);
  const scores = {};

  for (const line of lines) {
    try {
      const e = JSON.parse(line);
      if (e.taskType !== taskType) continue;
      if (!scores[e.adapterId]) {
        scores[e.adapterId] = { success: 0, total: 0, totalDuration: 0 };
      }
      scores[e.adapterId].total++;
      if (e.success) scores[e.adapterId].success++;
      scores[e.adapterId].totalDuration += e.durationMs || 0;
    } catch {}
  }

  let best = null;
  let bestScore = -1;

  for (const [adapterId, s] of Object.entries(scores)) {
    const rate = s.success / s.total;
    const avgDur = s.totalDuration / s.total;
    // Weighted: 70% success rate, 30% speed (inverse of duration)
    const score = rate * 0.7 + Math.max(0, 1 - avgDur / 30000) * 0.3;
    if (score > bestScore) {
      bestScore = score;
      best = { adapterId, score, successRate: rate, count: s.total };
    }
  }
  return best;
}

/**
 * Get statistics for a specific adapter.
 * Returns { adapterId, avgDurationMs, successRate, count }
 */
export function getAdapterStats(adapterId) {
  if (!existsSync(HISTORY_FILE)) return null;
  const lines = readFileSync(HISTORY_FILE, 'utf8').split('\n').filter(Boolean);
  let total = 0, success = 0, totalDuration = 0;
  for (const line of lines) {
    try {
      const e = JSON.parse(line);
      if (e.adapterId !== adapterId) continue;
      total++;
      if (e.success) success++;
      totalDuration += e.durationMs || 0;
    } catch {}
  }
  if (total === 0) return null;
  return { adapterId, avgDurationMs: totalDuration / total, successRate: success / total, count: total };
}

// CLI interface
const args = process.argv.slice(2);
const hasRecent = args.includes('--recent');
const hasStats = args.includes('--stats');

if (hasRecent || hasStats) {
  const lines = readFileSync(HISTORY_FILE, 'utf8').split('\n').filter(Boolean);
  const entries = lines.map(l => JSON.parse(l));
  if (hasStats) {
    const total = entries.length;
    const success = entries.filter(e => e.success).length;
    console.log(JSON.stringify({total, successRate: total ? Math.round(success/total*100) : 0}));
  } else {
    const n = hasRecent ? parseInt(args[args.indexOf('--recent') + 1] || '10') : 10;
    const recent = entries.slice(-n);
    console.log(recent.map(e => `${new Date(e.timestamp).toISOString()} ${e.success ? '✓' : '✗'} ${e.taskType}/${e.adapterId} ${e.durationMs}ms`).join('\n'));
  }
  process.exit(0);
}

const cmd = process.argv.includes('--best') ? 'best' : process.argv[2];
if (cmd === 'best') {
  const taskType = process.argv[3] || 'browse';
  const best = getBestAdapter(taskType);
  if (!best) {
    console.log('No history for:', taskType);
  } else {
    if (process.argv.includes('--json')) {
    console.log(JSON.stringify({ taskType, best }));
  } else {
    console.log(`Best adapter for "${taskType}": ${best.adapterId}`);
  }
    console.log(`  Score: ${(best.score * 100).toFixed(1)}%`);
    console.log(`  Success rate: ${(best.successRate * 100).toFixed(1)}%`);
    console.log(`  Runs: ${best.count}`);
  }
} else if (cmd === 'record') {
  const [, , taskType, adapterId, success, durationMs] = process.argv;
  recordResult(taskType, adapterId, success === 'true', parseInt(durationMs));
  console.log('Recorded:', taskType, adapterId, success);
} else if (cmd === 'stats') {
  const adapterId = process.argv[3];
  if (!adapterId) {
    const lines = readFileSync(HISTORY_FILE, 'utf8').split('\n').filter(Boolean);
    const byAdapter = {};
    for (const line of lines) {
      try {
        const e = JSON.parse(line);
        byAdapter[e.adapterId] = byAdapter[e.adapterId] || { success: 0, total: 0, totalDuration: 0 };
        byAdapter[e.adapterId].total++;
        if (e.success) byAdapter[e.adapterId].success++;
        byAdapter[e.adapterId].totalDuration += e.durationMs || 0;
      } catch {}
    }
    console.log('=== Adapter Statistics ===');
    for (const [id, s] of Object.entries(byAdapter)) {
      const rate = (s.success / s.total * 100).toFixed(0);
      const avg = (s.totalDuration / s.total / 1000).toFixed(1) + 's';
      console.log('  ' + id + ': ' + s.success + '/' + s.total + ' (' + rate + '%) avg=' + avg);
    }
  } else {
    const stats = getAdapterStats(adapterId);
    if (!stats) {
      console.log('No history for adapter: ' + adapterId);
    } else {
      console.log('=== ' + adapterId + ' ===');
      console.log('  Runs: ' + stats.count);
      console.log('  Success rate: ' + (stats.successRate * 100).toFixed(1) + '%');
      console.log('  Avg duration: ' + (stats.avgDurationMs / 1000).toFixed(1) + 's');
    }
  }
}
