#!/usr/bin/env node
// Add adapter-stats CLI command to exec-history.mjs
import { readFileSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __DIR = dirname(fileURLToPath(import.meta.url));
const TARGET = join(__DIR, '..', '80-PROJECTS', 'task-orchestrator', 'bin', 'exec-history.mjs');
let content = readFileSync(TARGET, 'utf8');

const marker = "} else {\n  console.log('Usage: node exec-history.mjs best <taskType>');";
if (!content.includes(marker)) {
  console.error('[patch] CLI usage marker not found');
  process.exit(1);
}

const statsCmd = "} else if (cmd === 'stats') {\n  const adapterId = process.argv[3];\n  if (!adapterId) {\n    const lines = readFileSync(HISTORY_FILE, 'utf8').split('\\n').filter(Boolean);\n    const byAdapter = {};\n    for (const line of lines) {\n      try {\n        const e = JSON.parse(line);\n        byAdapter[e.adapterId] = byAdapter[e.adapterId] || { success: 0, total: 0, totalDuration: 0 };\n        byAdapter[e.adapterId].total++;\n        if (e.success) byAdapter[e.adapterId].success++;\n        byAdapter[e.adapterId].totalDuration += e.durationMs || 0;\n      } catch {}\n    }\n    console.log('=== Adapter Statistics ===');\n    for (const [id, s] of Object.entries(byAdapter)) {\n      const rate = (s.success / s.total * 100).toFixed(0);\n      const avg = (s.totalDuration / s.total / 1000).toFixed(1) + 's';\n      console.log('  ' + id + ': ' + s.success + '/' + s.total + ' (' + rate + '%) avg=' + avg);\n    }\n  } else {\n    const stats = getAdapterStats(adapterId);\n    if (!stats) {\n      console.log('No history for adapter: ' + adapterId);\n    } else {\n      console.log('=== ' + adapterId + ' ===');\n      console.log('  Runs: ' + stats.count);\n      console.log('  Success rate: ' + (stats.successRate * 100).toFixed(1) + '%');\n      console.log('  Avg duration: ' + (stats.avgDurationMs / 1000).toFixed(1) + 's');\n    }\n  }\n}";

const next = content.replace(marker, statsCmd);
writeFileSync(TARGET, next, 'utf8');
console.log('[patch] exec-history.mjs now has stats command');
