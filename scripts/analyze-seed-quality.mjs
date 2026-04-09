#!/usr/bin/env node
/**
 * scripts/analyze-seed-quality.mjs
 * Scans ideas.md unshipped seeds, validates approach executability.
 * Usage:
 *   node scripts/analyze-seed-quality.mjs [--auto-kill] [--json]
 *   node scripts/analyze-seed-quality.mjs --days N      # filter to last N days
 *   node scripts/analyze-seed-quality.mjs --source X    # filter by source tag
 */
import { createReadStream, writeFileSync } from 'fs';
import { createInterface } from 'readline';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const IDEAS_PATH = join(__DIR, '..', '.omc', 'innovation', 'ideas.md');

const autoKill = process.argv.includes('--auto-kill');
const jsonMode = process.argv.includes('--json');
const cleanDaysIdx = process.argv.indexOf('--clean-shipped-days');
const cleanDays = cleanDaysIdx !== -1 ? parseInt(process.argv[cleanDaysIdx + 1], 10) : 0;
const daysIdx = process.argv.indexOf('--days');
const daysLimit = daysIdx !== -1 ? parseInt(process.argv[daysIdx + 1], 10) : 0;
const sourceIdx = process.argv.indexOf('--source');
const sourceFilter = sourceIdx !== -1 ? process.argv[sourceIdx + 1] : null;

const EXECUTABLE_PREFIXES = [
  'python ', 'node ', 'npx ', 'bun ', 'bash ', 'sh ',
  'cd ', 'mkdir ', 'task ', '#', '/', '//',
  '读 ', '写 ', '创建 ', '删除 ', '搜索 ', '执行 ',
  '修改 ', '在 ', '调研 ', '设计 ', '规划 ', '分析 ', '运行 ', '编译 ', '打包 '
];

// ── Stream-based parser ────────────────────────────────────────────────────────
const rl = createInterface(createReadStream(IDEAS_PATH, { encoding: 'utf-8' }));

const results = [];
let currentHeader = null;
let currentHeaderLine = '';
let currentBodyLines = [];
let lineIdx = 0;

for await (const line of rl) {
  const headerMatch = line.match(/^- \[(\d{4}-\d{2}-\d{2}|\d{8})\] (?:STAGE|seed) \[brainstorm\]/);

  if (headerMatch) {
    // Flush previous entry
    if (currentHeader) {
      const bodyText = currentBodyLines.join('\n').replace(/^\s{2}/gm, '');

      const shippedMatch = line.match(/shipped:(\d{4}-\d{2}-\d{2}|\d{8})/) || bodyText.match(/shipped:(\d{4}-\d{2}-\d{2}|\d{8})/);
      const killedMatch = line.match(/killed:(\d{4}-\d{2}-\d{2}|\d{8})/) || bodyText.match(/killed:(\d{4}-\d{2}-\d{2}|\d{8})/);
      if (!shippedMatch && !killedMatch) {
        // Source filter
        if (!sourceFilter || currentHeaderLine.includes(`[${sourceFilter}]`)) {
          // Date filter
          const dateStr = currentHeader;
          if (daysLimit <= 0 || parseInt(dateStr.replace(/-/g, ''), 10) >= parseInt(new Date(Date.now() - daysLimit * 24 * 60 * 60 * 1000).toISOString().slice(0, 10).replace(/-/g, ''), 10)) {
            const approachMatch = bodyText.match(/\|?\s*approach:\s*(.+?)(?:\s*\| shipped:|\s*\| killed:|$)/s)
              || currentHeaderLine.match(/\| approach:\s*(.+?)(?:\s*\| shipped:|\s*\| killed:|$)/s);
            const approachText = approachMatch ? approachMatch[1].trim() : '';

            const stepPrefixPattern = /^(?:\d+\. |阶段[一二三四五六七八九]?(?:\([^)]+\))?：\s*)(.+?)(?:\n\s*(?:\d+\.|阶段[一二三四五六七八九]?(?:\([^)]+\))?：)|$)/s;
            const firstStepMatch = approachText.match(stepPrefixPattern);
            const firstStep = firstStepMatch ? stepPrefixPattern[1].replace(/；$/, '').trim() : approachText;

            const scoreMatch = currentHeaderLine.match(/\[score:(\d+)×(\d+)\]/);
            const benefit = scoreMatch ? parseInt(scoreMatch[1], 10) : 0;
            const feas = scoreMatch ? parseInt(scoreMatch[2], 10) : 0;

            const isExecutable = firstStep.length > 0 && (
              EXECUTABLE_PREFIXES.some(p => firstStep.startsWith(p) || firstStep.includes(p)) ||
              /^[a-zA-Z]:\\/.test(firstStep)
            );

            const angleMatch = currentHeaderLine.match(/\[angle:([^\]]+)\]/);
            const angle = angleMatch ? angleMatch[1] : 'unknown';

            results.push({ date: currentHeader, score: benefit * feas, feas, angle, firstStep, isExecutable, lineIdx: currentBodyLines.length > 0 ? lineIdx - currentBodyLines.length : lineIdx });
          }
        }
      }
    }

    // Start new entry
    currentHeader = headerMatch[1];
    currentHeaderLine = line;
    currentBodyLines = [];
    lineIdx++;
  } else if (currentHeader && line.match(/^\s{2}/)) {
    currentBodyLines.push(line);
    lineIdx++;
  } else {
    currentBodyLines = [];
    lineIdx++;
  }
}

// Flush last entry
if (currentHeader) {
  const bodyText = currentBodyLines.join('\n').replace(/^\s{2}/gm, '');
  const shippedMatch = currentHeaderLine.match(/shipped:(\d{4}-\d{2}-\d{2}|\d{8})/) || bodyText.match(/shipped:(\d{4}-\d{2}-\d{2}|\d{8})/);
  const killedMatch = currentHeaderLine.match(/killed:(\d{4}-\d{2}-\d{2}|\d{8})/) || bodyText.match(/killed:(\d{4}-\d{2}-\d{2}|\d{8})/);
  if (!shippedMatch && !killedMatch) {
    if (!sourceFilter || currentHeaderLine.includes(`[${sourceFilter}]`)) {
      const dateStr = currentHeader;
      if (daysLimit <= 0 || parseInt(dateStr.replace(/-/g, ''), 10) >= parseInt(new Date(Date.now() - daysLimit * 24 * 60 * 60 * 1000).toISOString().slice(0, 10).replace(/-/g, ''), 10)) {
        const approachMatch = bodyText.match(/\|?\s*approach:\s*(.+?)(?:\s*\| shipped:|\s*\| killed:|$)/s)
          || currentHeaderLine.match(/\| approach:\s*(.+?)(?:\s*\| shipped:|\s*\| killed:|$)/s);
        const approachText = approachMatch ? approachMatch[1].trim() : '';
        const stepPrefixPattern = /^(?:\d+\. |阶段[一二三四五六七八九]?(?:\([^)]+\))?：\s*)(.+?)(?:\n\s*(?:\d+\.|阶段[一二三四五六七八九]?(?:\([^)]+\))?：)|$)/s;
        const firstStepMatch = approachText.match(stepPrefixPattern);
        const firstStep = firstStepMatch ? firstStepMatch[1].replace(/；$/, '').trim() : approachText;
        const scoreMatch = currentHeaderLine.match(/\[score:(\d+)×(\d+)\]/);
        const benefit = scoreMatch ? parseInt(scoreMatch[1], 10) : 0;
        const feas = scoreMatch ? parseInt(scoreMatch[2], 10) : 0;
        const isExecutable = firstStep.length > 0 && (
          EXECUTABLE_PREFIXES.some(p => firstStep.startsWith(p) || firstStep.includes(p)) ||
          /^[a-zA-Z]:\\/.test(firstStep)
        );
        const angleMatch = currentHeaderLine.match(/\[angle:([^\]]+)\]/);
        const angle = angleMatch ? angleMatch[1] : 'unknown';
        results.push({ date: currentHeader, score: benefit * feas, feas, angle, firstStep, isExecutable, lineIdx });
      }
    }
  }
}

const invalid = results.filter(r => !r.isExecutable);
const valid = results.filter(r => r.isExecutable);

if (jsonMode) {
  console.log(JSON.stringify({ total: results.length, valid: valid.length, invalid: invalid.length, seeds: results }, null, 2));
  process.exit(0);
}

console.log(`\n=== Seed Quality Analysis ===`);
console.log(`Total unshipped: ${results.length} | Valid: ${valid.length} | Invalid: ${invalid.length}`);
console.log('');
if (invalid.length > 0) {
  console.log(`[INVALID] ${invalid.length} seeds with non-executable approach:`);
  for (const s of invalid) {
    console.log(`  score:${s.score} f:${s.feas} angle:${s.angle} [line ${s.lineIdx + 1}]`);
    console.log(`    approach: ${s.firstStep.slice(0, 60)}...`);
  }
  console.log('');
  if (autoKill) {
    console.log(`[AUTO-KILL] Note: --auto-kill requires full file rewrite; skipping for streaming mode.`);
    console.log(`[HINT] Review invalid seeds manually or use --json to process programmatically.`);
  } else {
    console.log(`Run with --auto-kill to mark these invalid seeds as killed.`);
  }
} else {
  console.log('[OK] All unshipped seeds have executable approaches.');
}

// Clean old shipped seeds (requires synchronous read — only when cleanDays > 0)
if (cleanDays > 0) {
  const { readFileSync } = await import('fs');
  const content = readFileSync(IDEAS_PATH, 'utf-8');
  const lines = content.split('\n');
  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - cleanDays);
  const cutoffNum = parseInt(cutoff.toISOString().slice(0, 10).replace(/-/g, ''), 10);
  let cleaned = 0;
  const newLines = lines.filter(line => {
    const m = line.match(/shipped:(\d{4}-\d{2}-\d{2}|\d{8})/);
    if (m) {
      const d = parseInt(m[1].replace(/-/g, ''), 10);
      if (d < cutoffNum) { cleaned++; return false; }
    }
    return true;
  });
  if (cleaned > 0) {
    writeFileSync(IDEAS_PATH, newLines.join('\n'), 'utf-8');
    console.log(`[CLEAN] Removed ${cleaned} shipped seeds older than ${cleanDays} days.`);
  } else {
    console.log(`[CLEAN] No shipped seeds older than ${cleanDays} days.`);
  }
}
