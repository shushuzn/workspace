#!/usr/bin/env node
import { readFileSync, writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const IDEAS_PATH = join(__DIR, '..', 'knowledge', 'wikipedia', '.omc', 'innovation', 'ideas.md');

const EXECUTABLE_PREFIXES = [
  'python ', 'node ', 'npx ', 'bun ', 'bash ', 'sh ',
  'Edit ', 'Read ', 'Write ', 'Create ', 'Delete ',
  'Grep ', 'Glob ', 'Bash ', 'Search ', 'List ', 'Sed ',
  'cd ', 'mkdir ', 'task ', '#', '/', '//',
  '读 ', '写 ', '创建 ', '删除 ', '搜索 ', '执行 ',
  '修改 ', '在 ', '调研 ', '设计 ', '规划 ', '分析 ', '运行 ', '编译 ', '打包 '
];

const stepPrefixPattern = /^(?:\d+\. |阶段[一二三四五六七八九]?(?:\([^)]+\))?：\s*)(.+?)(?:\n\s*(?:\d+\.|阶段[一二三四五六七八九]?(?:\([^)]+\))?：)|$)/s;

const content = readFileSync(IDEAS_PATH, 'utf-8');
const lines = content.split('\n');

const results = [];
let i = 0;
while (i < lines.length) {
  const line = lines[i];
  const killedMatch = line.match(/killed:(\d{8}) non-executable/);
  if (!killedMatch) { i++; continue; }

  const bodyLines = [];
  let j = i + 1;
  while (j < lines.length && lines[j].match(/^\s{2}/)) bodyLines.push(lines[j++]);
  const bodyText = bodyLines.join(' ').replace(/^\s{2}/gm, '');

  const approachMatch = bodyText.match(/\|?\s*approach:\s*(.+?)(?:\s*\| shipped:|\s*\| killed:|$)/s);
  const approachText = approachMatch ? approachMatch[1].trim() : '';
  const firstStepMatch = approachText.match(stepPrefixPattern);
  const firstStep = firstStepMatch ? firstStepMatch[1].replace(/；$/, '').trim() : approachText;

  const scoreMatch = line.match(/\[score:(\d+)x(\d+)\]/);
  const feas = scoreMatch ? parseInt(scoreMatch[2], 10) : 0;
  const score = scoreMatch ? parseInt(scoreMatch[1], 10) * feas : 0;

  const isExecutable = firstStep.length > 0 && (
    EXECUTABLE_PREFIXES.some(p => firstStep.startsWith(p) || firstStep.includes(p)) ||
    firstStep.match(/^[a-zA-Z]:\\/) !== null
  );

  results.push({ lineIdx: i, score, feas, firstStep: firstStep.slice(0, 80), isExecutable });
  i = j;
}

const revived = results.filter(r => r.isExecutable);
const stillDead = results.filter(r => !r.isExecutable);

console.log(`=== Killed Seeds Backcheck ===`);
console.log(`Total killed(non-executable): ${results.length}`);
console.log(`Revived (valid firstStep): ${revived.length}`);
console.log(`Still dead: ${stillDead.length}`);
console.log('');
if (revived.length > 0) {
  console.log('[REVIVED - should remove killed tag]');
  revived.forEach(r => console.log(`  score:${r.score}x${r.feas} [line ${r.lineIdx+1}] firstStep: ${r.firstStep}`));
}
if (stillDead.length > 0) {
  console.log('\n[STILL DEAD - valid kill]');
  stillDead.forEach(r => console.log(`  score:${r.score}x${r.feas} [line ${r.lineIdx+1}] firstStep: ${r.firstStep}`));
}
