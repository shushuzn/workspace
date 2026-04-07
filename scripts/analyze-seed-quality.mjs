#!/usr/bin/env node
/**
 * scripts/analyze-seed-quality.mjs
 * Scans ideas.md unshipped seeds, validates approach executability.
 * Usage:
 *   node scripts/analyze-seed-quality.mjs [--auto-kill] [--json]
 */
import { readFileSync, writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const IDEAS_PATH = join(__DIR, '..', 'knowledge', 'wikipedia', '.omc', 'innovation', 'ideas.md');

const autoKill = process.argv.includes('--auto-kill');
const jsonMode = process.argv.includes('--json');

const EXECUTABLE_PREFIXES = [
  'python ', 'node ', 'npx ', 'bun ', 'bash ', 'sh ',
  'Edit ', 'Read ', 'Write ', 'Create ', 'Delete ',
  'Grep ', 'Glob ', 'Bash ', 'Search ', 'List ', 'Sed ',
  'cd ', 'mkdir ', 'task ', '#', '/', '//',
  '读 ', '写 ', '创建 ', '删除 ', '搜索 ', '执行 '
];

const content = readFileSync(IDEAS_PATH, 'utf-8');
const lines = content.split('\n');

const results = [];
let i = 0;
while (i < lines.length) {
  const line = lines[i];
  const headerMatch = line.match(/^- \[(\d{8})\] seed \[brainstorm\]/);
  if (!headerMatch) { i++; continue; }

  // Collect body lines
  const bodyLines = [];
  let j = i + 1;
  while (j < lines.length && lines[j].match(/^\s{2}/)) {
    bodyLines.push(lines[j]);
    j++;
  }
  const bodyText = bodyLines.join('\n').replace(/^\s{2}/gm, '');

  const shippedMatch = line.match(/\| shipped:(\d{8})/) || bodyText.match(/\| shipped:(\d{8})/);
  const killedMatch = line.match(/killed:(\d{8})/) || bodyText.match(/killed:(\d{8})/);
  if (shippedMatch || killedMatch) { i = j; continue; }

  // Extract approach
  const approachMatch = bodyText.match(/\|?\s*approach:\s*(.+?)(?:\s*\| shipped:|\s*\| killed:|$)/s);
  const approachText = approachMatch ? approachMatch[1].trim() : '';

  // Extract first step (handles "1." / "阶段一：" / "阶段一(设计)：" prefixes)
  const stepPrefixPattern = /^(?:\d+\. |阶段[一二三四五六七八九]?(?:\([^)]+\))?：\s*)(.+?)(?:\n\s*(?:\d+\.|阶段[一二三四五六七八九]?(?:\([^)]+\))?：)|$)/s;
  const firstStepMatch = approachText.match(stepPrefixPattern);
  const firstStep = firstStepMatch ? firstStepMatch[1].replace(/；$/, '').trim() : approachText;

  const scoreMatch = line.match(/\[score:(\d+)x(\d+)\]/);
  const benefit = scoreMatch ? parseInt(scoreMatch[1], 10) : 0;
  const feas = scoreMatch ? parseInt(scoreMatch[2], 10) : 0;
  const score = benefit * feas;

  // Check executability: all seeds require executable prefix (Gate 4b)
  let isExecutable = false;
  if (firstStep.length === 0) {
    isExecutable = false;
  } else {
    isExecutable = EXECUTABLE_PREFIXES.some(p => firstStep.startsWith(p)) ||
      firstStep.match(/^[a-zA-Z]:\\/) !== null;
  }

  const angleMatch = line.match(/\[angle:([^\]]+)\]/);
  const angle = angleMatch ? angleMatch[1] : 'unknown';

  results.push({ date: headerMatch[1], score, feas, angle, firstStep, isExecutable, lineIdx: i, approachText: approachText.slice(0, 80) });

  i = j;
}

const invalid = results.filter(r => !r.isExecutable);
const valid = results.filter(r => r.isExecutable);

if (jsonMode) {
  console.log(JSON.stringify({ total: results.length, valid: valid.length, invalid: invalid.length, seeds: results }, null, 2));
} else {
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
      console.log(`[AUTO-KILL] Marking ${invalid.length} invalid seeds as killed...`);
      const newLines = [...lines];
      for (const s of invalid.reverse()) {
        const line = newLines[s.lineIdx];
        if (line.match(/killed:/)) continue;
        // Append killed tag to approach line
        const bodyLineIdx = s.lineIdx + 1;
        const currentBody = newLines[bodyLineIdx];
        if (currentBody.match(/\| approach:/)) {
          newLines[bodyLineIdx] = currentBody.replace(/(\s*)$/, ` | killed:20260407 non-executable approach`);
        }
      }
      writeFileSync(IDEAS_PATH, newLines.join('\n'), 'utf-8');
      console.log(`[DONE] ${invalid.length} seeds marked killed.`);
    } else {
      console.log(`Run with --auto-kill to mark these invalid seeds as killed.`);
    }
  } else {
    console.log('[OK] All unshipped seeds have executable approaches.');
  }
}
