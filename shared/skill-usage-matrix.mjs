#!/usr/bin/env node
/**
 * skill-usage-matrix.mjs
 * 扫描 ideas.md 中 skill 被引用情况，输出使用矩阵
 */
import { readFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const IDEAS = resolve(__dirname, '../.omc/innovation/ideas.md');

const content = readFileSync(IDEAS, 'utf-8');

// 提取所有 skill 引用
const skillRe = /skill-[a-z][a-z0-9-]*/g;
const skillCounts = {};
for (const match of content.matchAll(skillRe)) {
  const s = match[0];
  skillCounts[s] = (skillCounts[s] || 0) + 1;
}

// 按引用次数排序
const sorted = Object.entries(skillCounts).sort((a, b) => b[1] - a[1]);

console.log('=== Skill Usage Matrix ===\n');
console.log('| Skill | 引用次数 |');
console.log('|-------|----------|');
for (const [skill, count] of sorted) {
  console.log(`| ${skill} | ${count} |`);
}
console.log(`\nTotal: ${sorted.length} skills, ${Object.values(skillCounts).reduce((a, b) => a + b, 0)} references`);
