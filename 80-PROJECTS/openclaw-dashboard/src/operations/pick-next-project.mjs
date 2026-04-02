/**
 * pick-next-project.mjs
 * 权重衰减随机抽选下一个目标项目
 *
 * 用法:
 *   node pick-next-project.mjs [gamma] [memoryPath] [--health-check]
 *
 * 参数:
 *   gamma       — 衰减系数，默认 0.5
 *   memoryPath  — MEMORY.md 绝对路径
 *   --health-check — 自动体检抽中的项目（尝试启动，3分钟超时）
 *
 * 输出:
 *   抽选结果 + 权重排行榜 + 体检结果
 *
 * 验收:
 *   体检完成后必须更新 MEMORY.md Last Active 和 .omc/state/pick-next-project.json
 */

import { PickNextProject } from './productive-ops.mjs';
import { SuggestProjectIdeas } from './detection-ops.mjs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
// pick-next-project.mjs 位于 src/operations/，workspace 在上 4 层
const workspaceRoot = path.join(__dirname, '..', '..', '..', '..');
// MEMORY.md 位于 workspace 外的 oh-my-claude code memory 目录
const DEFAULT_MEMORY = 'C:/Users/adm/.claude/projects/D--OpenClaw-workspace/memory/MEMORY.md';

const doHealthCheck = process.argv.includes('--health-check');
const gamma = parseFloat(process.argv[2]) || 0.5;
const memoryPath = process.argv.find((a, i) => i > 2 && !a.startsWith('--')) || DEFAULT_MEMORY;

const picker = new PickNextProject(workspaceRoot, gamma, memoryPath);
const result = await picker.execute();

// 技术雷达检查：超过1天未检查则强制触发
const today = new Date().toISOString().split('T')[0].replace(/-/g, '');
const radarDay = result.state?.last_radar_check ? String(result.state.last_radar_check).replace(/-/g, '') : today;
if (radarDay !== today) {
  console.log(`\n⚡ 技术雷达触发（距上次检查已过 ${Math.floor((new Date(today) - new Date(radarDay)) / 86400000)} 天）`);
  console.log('   请评估：LLM/Rust/新框架/新工具 是否值得在现有项目中试点？');
  console.log('   结果请写入 MEMORY.md "技术跟进" 区域');
  picker._saveState({ ...result.state, last_radar_check: today.replace(/-/g, '') });
}

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

if (result.pair && result.bridge) {
  console.log(`\n🌉 意外相似: ${result.picked} ↔ ${result.pair.name}`);
  console.log(`   共享依赖: ${result.bridge.shared}`);
  console.log(`   候选列表: ${result.bridge.allShared.join(', ')}`);
} else if (result.pair) {
  console.log(`\n🌉 意外相似: ${result.picked} ↔ ${result.pair.name}（无共享依赖）`);
}

// 抽中后自动生成项目优化建议并写入 idea 池
const suggester = new SuggestProjectIdeas(path.join(workspaceRoot, '80-PROJECTS'));
const sugg = await suggester.execute(result.path);
if (sugg.ideas > 0) {
  console.log(`\n💡 生成 ${sugg.ideas} 条优化建议，已写入 idea 池`);
  sugg.suggestions.forEach(s => console.log(`   • ${s}`));
}

if (doHealthCheck) {
  console.log('\n🔍 自动体检中（最多3分钟）...');
  const health = await picker._runHealthCheck(result.path);
  if (health.status === 'skip') {
    console.log(`\n⏭️  跳过: ${health.reason}`);
  } else if (health.status === 'ok') {
    console.log(`\n✅ 体检通过: ${health.reason}`);
    picker.recordHealthSuccess(result.picked);
  } else if (health.status === 'timeout') {
    console.log(`\n⏰ 体检超时: ${health.reason}`);
    picker.recordHealthFailure(result.picked);
  } else {
    console.log(`\n❌ 体检失败: ${health.reason}`);
    picker.recordHealthFailure(result.picked);
    if (health.output) console.log(`   ${health.output.split('\n').slice(-2).join(' | ')}`);
  }
} else {
  console.log('\n【验收】请选择体检类型：');
  console.log('  A — 检查能否正常启动运行（3 分钟内验证）');
  console.log('  B — 修 1 个小 bug 或补 1 条注释/文档');
  console.log('  C — 更新 MEMORY.md 中该项目价值记录');
  console.log('\n完成后：');
  console.log('  1. 更新 MEMORY.md 的 Last Active 为今天');
  console.log('  2. 确认本次抽选已完成\n');
}
