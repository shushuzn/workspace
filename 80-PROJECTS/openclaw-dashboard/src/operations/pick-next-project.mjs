/**
 * pick-next-project.mjs
 * 权重衰减随机抽选下一个目标项目
 *
 * 用法:
 *   node pick-next-project.mjs [gamma] [memoryPath] [--health-check] [--continue]
 *
 * 参数:
 *   gamma       — 衰减系数，默认 0.5
 *   memoryPath  — MEMORY.md 绝对路径
 *   --health-check — 自动体检抽中的项目（尝试启动，3分钟超时）
 *   --continue   — 跳过抽选，复用上次选中的项目（继续当前工作）
 *
 * 输出:
 *   抽选结果 + 权重排行榜 + 体检结果
 *
 * 验收:
 *   体检完成后必须更新 MEMORY.md Last Active 和 .omc/state/pick-next-project.json
 */

import { PickNextProject, IdeaPool } from './productive-ops.mjs';
import { SuggestProjectIdeas } from './detection-ops.mjs';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
// pick-next-project.mjs 位于 src/operations/，workspace 在上 4 层
const workspaceRoot = path.join(__dirname, '..', '..', '..', '..');
// MEMORY.md 位于 workspace 外的 oh-my-claude code memory 目录
const DEFAULT_MEMORY = 'C:/Users/adm/.claude/projects/D--OpenClaw-workspace/memory/MEMORY.md';

const doHealthCheck = process.argv.includes('--health-check');
const doContinue = process.argv.includes('--continue');
// gamma 从 argv 解析（跳过所有 -- 开头的 flag）
const rawGamma = (() => {
  for (let i = 2; i < process.argv.length; i++) {
    if (!process.argv[i].startsWith('--')) return process.argv[i];
  }
  return undefined;
})();
if (rawGamma !== undefined && !isNaN(parseFloat(rawGamma))) {
  const parsed = parseFloat(rawGamma);
  if (parsed <= 0 || parsed > 2) {
    console.warn(`⚠️ gamma 非法值 (${rawGamma})，已使用 fallback 0.5。请检查 MEMORY.md 项目表。`);
    const evFile = path.join(workspaceRoot, '.omc', 'state', 'CLAUDE.md-evolution.json');
    const ev = fs.existsSync(evFile) ? JSON.parse(fs.readFileSync(evFile, 'utf8')) : { lastSessionChecked: '', clauseLastExecuted: {}, gammaWarnings: [] };
    ev.gammaWarnings = ev.gammaWarnings || [];
    ev.gammaWarnings.push({ date: new Date().toISOString().split('T')[0], value: rawGamma });
    fs.writeFileSync(evFile, JSON.stringify(ev, null, 2), 'utf8');
  }
}
const gamma = parseFloat(rawGamma) || 0.5;
const memoryPath = process.argv.find((a, i) => {
  if (i <= 2) return false;
  if (a.startsWith('--')) return false;
  return true;
}) || DEFAULT_MEMORY;

const picker = new PickNextProject(workspaceRoot, gamma, memoryPath);

// --continue 模式：跳过抽选，直接复用上次结果
if (doContinue) {
  const state = picker._loadState();
  const last = state.lastPick;
  if (!last) {
    console.log('\n⏭️  无上次项目记录，请先运行 pick-next-project 不带 --continue');
    process.exit(0);
  }
  const memoryContent = fs.readFileSync(memoryPath, 'utf8');
  const projectRow = picker._parseProjectTable(memoryContent).find(r => r.name === last.project);
  const projPath = projectRow ? projectRow.path : last.project;
  console.log(`\n🔄 继续上次项目: ${last.project}`);
  console.log(`   路径: ${projPath}`);
  console.log(`   距上次活跃: ${last.days} 天`);
  console.log(`\n⏹️  退出。等你说"工作"才继续下一个项目。`);
  process.exit(0);
}

// PROJECT 参数：手动指定当前项目（跳过抽选，直接设置 lastPick）
const projectArg = (() => {
  for (let i = 2; i < process.argv.length; i++) {
    const a = process.argv[i];
    if (!a.startsWith('--') && a !== gamma) return a;
  }
  return null;
})();
if (projectArg) {
  const state = picker._loadState();
  const today = new Date().toISOString().split('T')[0].replace(/-/g, '');
  const todayDate = new Date().toISOString().split('T')[0];
  const memoryContent = fs.readFileSync(memoryPath, 'utf8');
  const projectRow = picker._parseProjectTable(memoryContent).find(r => r.name === projectArg);
  if (!projectRow) {
    console.log(`\n❌ 项目不存在: ${projectArg}`);
    process.exit(1);
  }
  // 计算 days
  let days = 0;
  if (projectRow.lastActive && /^\d{4}-\d{2}-\d{2}$/.test(projectRow.lastActive)) {
    days = Math.floor((new Date(todayDate) - new Date(projectRow.lastActive)) / 86400000);
  }
  const newState = {
    ...state,
    lastPick: { date: today, project: projectArg, days },
    last_radar_check: state.last_radar_check || today,
  };
  picker._saveState(newState);
  console.log(`\n🎯 当前项目: ${projectArg}`);
  console.log(`   路径: ${projectRow.path}`);
  console.log(`   距上次活跃: ${days} 天`);
  process.exit(0);
}

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

if (result.reused) {
  console.log(`\n🔄 复用上次项目: ${result.picked}`);
  console.log(`   路径: ${result.path}`);
  console.log(`   距上次活跃: ${result.days} 天`);
} else {
  console.log(`\n🎯 本次抽选目标项目: ${result.picked}`);
  console.log(`   路径: ${result.path}`);
  console.log(`   距上次活跃: ${result.days} 天`);
  console.log(`   权重: ${result.weight}`);
  console.log(`   (γ=${result.gamma}, 共 ${result.totalProjects} 个项目参与抽选)`);
  if (result.seed) {
    console.log(`   抽选ID: ${result.seed}`);
  }
}

if (result.allProjects && result.allProjects.length > 0) {
  console.log('\n权重排行榜 (Top 5):');
  const totalWeight = result.allProjects.reduce((s, x) => s + x.weight, 0);
  const ideaPool = new (await import('./productive-ops.mjs')).IdeaPool(workspaceRoot);
  result.allProjects.slice(0, 5).forEach((p, i) => {
    const b = picker.healthScoreBreakdown(p.name, p.days, ideaPool);
    const composite = picker.compositeHealthScore(p.name, p.days, ideaPool);
    const barLen = Math.max(1, Math.round((p.weight / totalWeight) * 12));
    const bar = '█'.repeat(barLen);
    const healthInfo = b.fail > 0 || b.succ > 0 ? `成功${b.succ}·失败${b.fail}` : '无体检记录';
    console.log(`  ${i + 1}. ${p.name.padEnd(28)} ${p.days}d`);
    console.log(`     γ权重 ${p.weight.toFixed(2)} | 活跃度 ${b.recencyNorm} | 健康 ${b.health} (${healthInfo}) | 质量 ${b.quality}`);
    console.log(`     综合 ${composite} ${bar}`);
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
const suggester = new SuggestProjectIdeas(workspaceRoot);
const sugg = await suggester.execute(result.path);
if (sugg.ideas > 0) {
  console.log(`\n💡 生成 ${sugg.ideas} 条优化建议，已写入 idea 池`);
  sugg.suggestions.forEach(s => console.log(`   • ${s}`));
}

// 项目积压 ideas 审计
const pool = new IdeaPool(workspaceRoot);
const projectIdeas = pool.getByProject(result.picked);
const activeProjectIdeas = projectIdeas.filter(i => !['shipped','killed'].includes(i.stage));
if (activeProjectIdeas.length > 0) {
  console.log(`\n📋 ${result.picked} 积压 ideas（共 ${activeProjectIdeas.length} 条活跃）`);
  activeProjectIdeas.forEach(i => {
    const sc = (i.impact && i.effort) ? `★${i.impact}x${i.effort}` : '未评分';
    console.log(`   [${i.stage}] ${sc} ${i.desc.replace(/\|.*/, '').trim().substring(0, 40)}`);
  });
}

// 全局创新待办统计
const allIdeas = pool.list().filter(i => !['shipped','killed'].includes(i.stage));
const hiScore = allIdeas.filter(i => (i.impact || 0) * (i.effort || 0) >= 6);
const midScore = allIdeas.filter(i => {
  const s = (i.impact || 0) * (i.effort || 0);
  return s >= 4 && s < 6;
});
const noScore = allIdeas.filter(i => !(i.impact && i.effort));
if (allIdeas.length > 0) {
  console.log(`\n📊 创新待办（共 ${allIdeas.length} 条）`);
  console.log(`   ★6-9: ${hiScore.length}条  ★4-5: ${midScore.length}条  未评分: ${noScore.length}条`);
  const top = [...hiScore, ...midScore].slice(0, 3);
  top.forEach(i => {
    const sc = (i.impact && i.effort) ? `★${i.impact}x${i.effort}` : '';
    console.log(`   • ${sc} ${i.desc.replace(/\|.*/, '').trim().substring(0, 40)}`);
  });
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
  picker.recordHealthSuccess(result.picked);
  console.log('\n✅ brainstorm + ideas 执行完成，已标记活跃');
  console.log('\n⏹️ 退出。等你说"工作"才继续下一个项目。');
  process.exit(0);
}
