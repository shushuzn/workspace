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
const newLines = [...lines];

let i = 0, revived = 0, killEmpty = 0, stillDead = 0;
while (i < lines.length) {
  const line = lines[i];
  const killedMatch = line.match(/killed:(\d{8}) non-executable/);
  if (!killedMatch) { i++; continue; }

  // Collect body lines (indented, until unindented)
  const bodyLines = [];
  let j = i + 1;
  while (j < lines.length && lines[j].match(/^\s{2}/)) bodyLines.push(lines[j++]);

  // Find approach line
  const approachLine = bodyLines.find(l => /\|?\s*approach:/.test(l));
  const approachText = approachLine ? approachLine.replace(/^\s*\|?\s*approach:\s*/, '').replace(/\s*\|.*$/, '').trim() : '';
  const firstStepMatch = approachText.match(stepPrefixPattern);
  const firstStep = firstStepMatch ? firstStepMatch[1].replace(/；$/, '').trim() : approachText;

  const isExecutable = firstStep.length > 0 && (
    EXECUTABLE_PREFIXES.some(p => firstStep.startsWith(p) || firstStep.includes(p)) ||
    firstStep.match(/^[a-zA-Z]:\\/) !== null
  );

  if (firstStep.length === 0) {
    killEmpty++;
    console.log(`STILL DEAD (empty) [line ${i+1}]: ${firstStep || '(no firstStep)'}`);
    stillDead++;
  } else if (isExecutable) {
    // Remove killed tag from header line
    newLines[i] = line.replace(/\s+killed:\d{8}\s+non-executable\s+approach\s*$/, '');
    revived++;
    console.log(`REVIVED [line ${i+1}]: firstStep="${firstStep.slice(0, 60)}"`);
  } else {
    stillDead++;
    console.log(`STILL DEAD [line ${i+1}]: firstStep="${firstStep.slice(0, 60)}"`);
  }
  i = j;
}

writeFileSync(IDEAS_PATH, newLines.join('\n'), 'utf-8');
console.log(`\nDone: revived=${revived}, stillDead=${stillDead}, killEmpty=${killEmpty}`);
