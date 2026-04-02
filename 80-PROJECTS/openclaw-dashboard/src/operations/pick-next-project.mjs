/**
 * pick-next-project.mjs
 * 权重衰减随机抽选下一个目标项目
 * 用法: node pick-next-project.mjs [gamma] [memoryPath]
 *   gamma       — 衰减系数，默认 0.5
 *   memoryPath  — MEMORY.md 绝对路径，默认从 workspace 内查找
 *
 * 输出示例:
 *   node pick-next-project.mjs
 *   node pick-next-project.mjs 0.7
 *   node pick-next-project.mjs 0.5 "C:/Users/adm/.claude/projects/xxx/memory/MEMORY.md"
 */

import { PickNextProject } from './productive-ops.mjs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
// pick-next-project.mjs 位于 src/operations/，workspace 在上三层
const workspaceRoot = path.join(__dirname, '..', '..', '..');
// MEMORY.md 位于 workspace 外的 oh-my-claudecode memory 目录
const DEFAULT_MEMORY = 'C:/Users/adm/.claude/projects/D--OpenClaw-workspace/memory/MEMORY.md';

const gamma = parseFloat(process.argv[2]) || 0.5;
// 默认 MEMORY.md 路径（openclaw-dashboard 在 workspace 内，MEMORY.md 在上级 .claude 目录）
const defaultMemoryPath = path.join(workspaceRoot, '.claude', 'projects', 'D--OpenClaw-workspace', 'memory', 'MEMORY.md');
const memoryPath = process.argv[3] || DEFAULT_MEMORY;

const picker = new PickNextProject(workspaceRoot, gamma, memoryPath);
const result = await picker.execute();

if (result.error) {
  console.error(`\n❌ Error: ${result.error}`);
  process.exit(1);
}

console.log(`\n🎯 本次抽选目标项目: ${result.picked}`);
console.log(`   路径: ${result.path}`);
console.log(`   距上次活跃: ${result.days} 天`);
console.log(`   权重: ${result.weight}`);
console.log(`   (γ=${result.gamma}, 共 ${result.totalProjects} 个项目参与抽选)\n`);

// Show top 5 by weight
if (result.allProjects && result.allProjects.length > 0) {
  console.log('权重排行榜 (Top 5):');
  result.allProjects.slice(0, 5).forEach((p, i) => {
    const bar = '█'.repeat(Math.round(p.weight * 5));
    console.log(`  ${i + 1}. ${p.name.padEnd(30)} ${p.days}d ${p.weight.toFixed(3)} ${bar}`);
  });
  console.log();
}
