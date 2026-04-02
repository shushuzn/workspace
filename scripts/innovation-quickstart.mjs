/**
 * innovation-quickstart.mjs — §10 创新管道一站式工具
 *
 * 用法:
 *   node scripts/innovation-quickstart.mjs status                    # 仪表盘
 *   node scripts/innovation-quickstart.mjs idea "描述"               # 新增 idea
 *   node scripts/innovation-quickstart.mjs score ID impact effort     # 打分 (1-3, 1-3)
 *   node scripts/innovation-quickstart.mjs review                    # brainstorm 复盘
 *   node scripts/innovation-quickstart.mjs prune                    # 清理过时 idea
 *   node scripts/innovation-quickstart.mjs radar                   # 技术雷达评估
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const WORKSPACE = path.join(__dirname, '..');
const IDEA_FILE = path.join(WORKSPACE, '.omc', 'innovation', 'ideas.md');
const MEMORY_FILE = 'C:/Users/adm/.claude/projects/D--OpenClaw-workspace/memory/MEMORY.md';

const STAGE_EMOJI = { seed: '💡', proposal: '📋', running: '🔬', shipped: '📦', killed: '💀', dormant: '⏸️' };

function today() {
  return new Date().toISOString().split('T')[0].replace(/-/g, '');
}

function readIdeas() {
  if (!fs.existsSync(IDEA_FILE)) return [];
  const raw = fs.readFileSync(IDEA_FILE, 'utf8');
  const ideas = [];
  for (const line of raw.split('\n')) {
    const m = line.match(/^-\s*\[(\d{8})\]\s*(\w+)(?:\s*\[(\w+)\])?\s+(.*)/);
    if (!m) continue;
    ideas.push({ date: m[1], stage: m[2], source: m[3] || 'manual', desc: m[4].trim() });
  }
  return ideas;
}

function writeIdeas(ideas) {
  const header = `# Idea Pool

> 每个 session 产生的 idea 必须立即追加到此文件。
> 格式：\`- [DATE] STAGE [source] description\`
> STAGE: seed=💡闪念 / proposal=📋提案 / running=🔬实验 / shipped=📦交付 / killed=💀放弃 / dormant=⏸️休眠
> SOURCE: brainstorm / suggest / manual（默认 manual）

`;
  const body = ideas.map(i => {
    const src = i.source ? ` [${i.source}]` : '';
    return `- [${i.date}] ${i.stage}${src} ${i.desc}`;
  }).join('\n');
  const dir = path.dirname(IDEA_FILE);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  const tmp = IDEA_FILE + '.tmp';
  fs.writeFileSync(tmp, header + body + '\n', 'utf8');
  fs.renameSync(tmp, IDEA_FILE);
}

function cmdStatus() {
  // 内联输出仪表盘信息
  const ideas = readIdeas();
  const stageCounts = { seed: 0, proposal: 0, running: 0, shipped: 0, killed: 0, dormant: 0 };
  for (const idea of ideas) stageCounts[idea.stage]++;
  console.log('\n💡 创新管道状态');
  console.log('═'.repeat(42));
  const bar = Object.entries(stageCounts).filter(([,n]) => n > 0).map(([s,n]) => `${STAGE_EMOJI[s]} ${n}`).join('   ');
  console.log('  ' + (bar || '(空)'));
  console.log('═'.repeat(42));
  console.log(`  共 ${ideas.length} 条 idea  |  用法: idea / review / prune / radar`);
}

function cmdIdea(args) {
  const desc = args.join(' ');
  if (!desc) { console.log('用法: idea "描述"'); return; }
  const ideas = readIdeas();
  ideas.push({ date: today(), stage: 'seed', source: 'manual', desc });
  writeIdeas(ideas);
  console.log(`✅ 已添加 💡 ${desc}`);
}

async function cmdReview() {
  try {
    const { BrainstormReview, InnovationReview } = await import('../80-PROJECTS/openclaw-dashboard/src/operations/detection-ops.mjs');
    const [brainstormRes, innovRes] = await Promise.all([
      new BrainstormReview(WORKSPACE).execute(),
      new InnovationReview(WORKSPACE).execute(),
    ]);
    console.log(brainstormRes.message);
    console.log(innovRes.message);
    if (brainstormRes.cleaned > 0) console.log(`已清理 ${brainstormRes.cleaned} 个过期 brainstorm 文件`);
  } catch (e) {
    console.log('Review: ' + e.message);
  }
}

function cmdPrune() {
  const TTL = { seed: 3, proposal: 7, running: 14, shipped: null, killed: null, dormant: 30 };
  const todayStr = today();
  const ideas = readIdeas();
  const now = new Date();

  function daysOld(dateStr) {
    const s = String(dateStr).replace(/-/g, '');
    const d = new Date(`${s.slice(0,4)}-${s.slice(4,6)}-${s.slice(6,8)}`);
    return Math.floor((now - d) / 86400000);
  }

  const before = ideas.length;
  const kept = ideas.filter(idea => {
    if (idea.stage === 'shipped' || idea.stage === 'killed') return true;
    const ttl = TTL[idea.stage];
    if (!ttl) return true;
    return daysOld(idea.date) <= ttl;
  });
  writeIdeas(kept);
  console.log(`✅ 清理完成，移除 ${before - kept.length} 条过时 idea`);
}

function cmdRadar() {
  // 技术雷达：读取 MEMORY.md 检查上次技术跟进日期
  if (!fs.existsSync(MEMORY_FILE)) { console.log('❌ MEMORY.md 未找到'); return; }
  const memory = fs.readFileSync(MEMORY_FILE, 'utf8');

  // 查找技术跟进区域
  const techSection = memory.match(/### 技术跟进\n([\s\S]*?)(?=\n## |$)/);
  const lastEntry = techSection
    ? techSection[1].match(/-\s*\[(\d{4}-\d{2}-\d{2})\]/)?.[1]
    : null;

  console.log(`\n⚡ 技术雷达`);
  console.log('═'.repeat(40));
  console.log(`  上次评估: ${lastEntry || '(无记录)'}`);
  console.log(`  今天: ${new Date().toISOString().split('T')[0]}`);
  console.log('─'.repeat(40));
  console.log('  请评估：LLM/Rust/新框架/新工具 是否值得在现有项目中试点？');
  console.log('  结果已写入 MEMORY.md "技术跟进" 区域');
  console.log('═'.repeat(40));
}

function cmdScore(args) {
  const idx = parseInt(args[0]);
  const impact = parseInt(args[1]);
  const effort = parseInt(args[2]);
  if (!args[0] || isNaN(impact) || isNaN(effort)) {
    console.log('用法: score ID impact effort  (1-3, 1-3)'); return;
  }
  if (![1,2,3].includes(impact) || ![1,2,3].includes(effort)) {
    console.log('❌ impact 和 effort 必须为 1-3'); return;
  }
  const score = impact * effort;
  const scoreMark = `[score:${impact}x${effort}]`;
  const ideas = readIdeas();
  if (idx < 0 || idx >= ideas.length) { console.log('❌ 未找到 idea'); return; }
  const idea = ideas[idx];
  const cleanDesc = (idea.desc || '').replace(/\s*\[score:\d+x\d+\]/g, '');
  ideas[idx] = { ...idea, impact, effort, desc: `${cleanDesc} ${scoreMark}` };
  writeIdeas(ideas);
  console.log(`✅ ★${score} (${impact}×${effort}) — ${cleanDesc.trim()}`);
}

const [cmd, ...args] = process.argv.slice(2);
switch (cmd) {
  case 'status': cmdStatus(); break;
  case 'idea':    cmdIdea(args); break;
  case 'score':   cmdScore(args); break;
  case 'review':  await cmdReview(); break;
  case 'prune':   cmdPrune(); break;
  case 'radar':   cmdRadar(); break;
  default:
    console.log('用法: innovation-quickstart.mjs status|idea|score|review|prune|radar');
    console.log('  status  — 创新管道仪表盘');
    console.log('  idea "描述" — 新增 idea（自动 stage=seed）');
    console.log('  score ID impact effort — ★impact×effort (1-3, 1-3)');
    console.log('  review  — brainstorm 复盘 + 采纳率统计');
    console.log('  prune   — 清理过时 idea');
    console.log('  radar   — 技术雷达评估');
}
