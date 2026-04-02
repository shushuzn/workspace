/**
 * pick-next-project.mjs
 * 权重衰减随机抽选下一个目标项目
 *
 * 用法:
 *   node pick-next-project.mjs [gamma] [memoryPath]
 *
 * 参数:
 *   gamma       — 衰减系数，默认 0.5
 *   memoryPath  — MEMORY.md 绝对路径
 *
 * 输出:
 *   抽选结果 + 权重排行榜 + 抽选ID（用于回溯）
 *
 * 验收:
 *   体检完成后必须更新 MEMORY.md Last Active 和 .omc/state/pick-next-project.json
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
console.log(`   (γ=${result.gamma}, 共 ${result.totalProjects} 个项目参与抽选)`);
if (result.seed) {
  console.log(`   抽选ID: ${result.seed}`);
}

if (result.allProjects && result.allProjects.length > 0) {
  console.log('\n权重排行榜 (Top 5):');
  result.allProjects.slice(0, 5).forEach((p, i) => {
    // bar = 该项目权重占总权重的比例（相对于 totalWeight）
    const totalWeight = result.allProjects.reduce((s, x) => s + x.weight, 0);
    const barLen = Math.max(1, Math.round((p.weight / totalWeight) * 12));
    const bar = '█'.repeat(barLen);
    console.log(`  ${i + 1}. ${p.name.padEnd(30)} ${p.days}d ${p.weight.toFixed(3)} ${bar}`);
  });
}

console.log('\n【验收】请选择体检类型：');
console.log('  A — 检查能否正常启动运行（3 分钟内验证）');
console.log('  B — 修 1 个小 bug 或补 1 条注释/文档');
console.log('  C — 更新 MEMORY.md 中该项目价值记录');
console.log('\n完成后：');
console.log('  1. 更新 MEMORY.md 的 Last Active 为今天');
console.log('  2. 确认本次抽选已完成\n');
