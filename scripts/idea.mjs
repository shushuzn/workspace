/**
 * idea.mjs — 创新想法池管理工具
 *
 * 用法:
 *   node scripts/idea.mjs list                    # 列出所有 idea
 *   node scripts/idea.mjs add STAGE description   # 新增 idea (STAGE: seed/proposal/running/shipped/killed/dormant)
 *   node scripts/idea.mjs advance ID [stage]     # 推进状态
 *   node scripts/idea.mjs kill ID reason        # 放弃 idea
 *   node scripts/idea.mjs prune                 # 自动清理过时 idea
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const IDEA_FILE = path.join(__dirname, '..', '.omc', 'innovation', 'ideas.md');

const STAGE_EMOJI = { seed: '💡', proposal: '📋', running: '🔬', shipped: '📦', killed: '💀', dormant: '⏸️' };
const STAGE_NAMES  = { seed: '闪念', proposal: '提案', running: '实验', shipped: '交付', killed: '放弃', dormant: '休眠' };
const TTL_DAYS     = { seed: 3, proposal: 7, running: 14, shipped: null, killed: null, dormant: 30 };
const STAGE_LIST   = ['seed', 'proposal', 'running', 'shipped', 'killed', 'dormant'];

function parseDate(str) {
  const s = String(str).replace(/-/g, '');
  return new Date(`${s.slice(0,4)}-${s.slice(4,6)}-${s.slice(6,8)}`);
}

function todayStr() {
  return new Date().toISOString().split('T')[0].replace(/-/g, '');
}

function getDaysOld(dateStr) {
  const d = parseDate(dateStr);
  return Math.floor((new Date() - d) / 86400000);
}

function readData() {
  if (!fs.existsSync(IDEA_FILE)) return [];
  const raw = fs.readFileSync(IDEA_FILE, 'utf8');
  const ideas = [];
  for (const line of raw.split('\n')) {
    const m = line.match(/^-\s*\[(\d{8})\]\s*(\w+)\s+(.*)/);
    if (!m) continue;
    ideas.push({ raw: line, date: m[1], stage: m[2], desc: m[3].trim() });
  }
  return ideas;
}

function writeData(ideas) {
  const header = `# Idea Pool

> 每个 session 产生的 idea 必须立即追加到此文件。
> 格式：\`- [DATE] STAGE description\`
> STAGE: seed=💡闪念 / proposal=📋提案 / running=🔬实验 / shipped=📦交付 / killed=💀放弃 / dormant=⏸️休眠

`;
  const body = ideas.map(i => `- [${i.date}] ${i.stage} ${i.desc}`).join('\n');
  fs.writeFileSync(IDEA_FILE, header + body + '\n', 'utf8');
}

function cmdList() {
  const ideas = readData();
  console.log('\n💡 创新想法池\n' + '═'.repeat(60));
  if (ideas.length === 0) { console.log('  (空)'); }
  ideas.forEach((idea, i) => {
    const age = getDaysOld(idea.date);
    const ttl = TTL_DAYS[idea.stage];
    const emoji = STAGE_EMOJI[idea.stage] || '?';
    const name  = STAGE_NAMES[idea.stage]  || idea.stage;
    const ageMark = ttl && age > ttl ? ' 🔴过时' : age > 0 ? ` (${age}d)` : '';
    console.log(`${i} ${emoji} [${name}] ${idea.desc}${ageMark}`);
  });
  console.log('═'.repeat(60));
}

function cmdAdd(args) {
  const stage = args[0] || 'seed';
  const desc  = args.slice(1).join(' ').trim() || '(无描述)';
  if (!STAGE_LIST.includes(stage)) {
    console.log(`❌ 未知 stage: ${stage}，可用: ${STAGE_LIST.join('/')}`);
    return;
  }
  const ideas = readData();
  ideas.push({ date: todayStr(), stage, desc });
  writeData(ideas);
  console.log(`✅ 已添加: ${STAGE_EMOJI[stage]} ${desc}`);
}

function cmdAdvance(args) {
  if (args.length < 1) { console.log('用法: advance ID [stage]'); return; }
  const idx = parseInt(args[0]);
  const ideas = readData();
  if (idx < 0 || idx >= ideas.length) { console.log('❌ 未找到 idea'); return; }
  const idea = ideas[idx];
  const curIdx = STAGE_LIST.indexOf(idea.stage);
  const target = args[1] || STAGE_LIST[curIdx + 1] || 'shipped';
  if (STAGE_LIST.indexOf(target) <= curIdx && !args[1]) {
    console.log(`❌ ${idea.stage} 已是最终状态`); return;
  }
  ideas[idx] = { ...idea, stage: target };
  writeData(ideas);
  console.log(`✅ ${STAGE_EMOJI[idea.stage]}→${STAGE_EMOJI[target]} ${idea.desc}`);
}

function cmdKill(args) {
  if (args.length < 2) { console.log('用法: kill ID reason'); return; }
  const idx = parseInt(args[0]);
  const reason = args.slice(1).join(' ');
  const ideas = readData();
  if (idx < 0 || idx >= ideas.length) { console.log('❌ 未找到 idea'); return; }
  const idea = ideas[idx];
  ideas[idx] = { ...idea, desc: `${idea.desc} | 💀 killed: ${reason}` };
  writeData(ideas);
  console.log(`💀 已放弃: ${idea.desc}`);
}

function cmdPrune() {
  const ideas = readData();
  let removed = 0;
  const kept = ideas.filter(idea => {
    if (idea.stage === 'shipped' || idea.stage === 'killed') return true;
    const ttl = TTL_DAYS[idea.stage];
    if (!ttl) return true;
    return getDaysOld(idea.date) <= ttl;
  });
  removed = ideas.length - kept.length;
  writeData(kept);
  console.log(`✅ 清理完成，移除 ${removed} 条过时 idea`);
}

const [cmd, ...args] = process.argv.slice(2);
switch (cmd) {
  case 'list':    cmdList();    break;
  case 'add':     cmdAdd(args); break;
  case 'advance': cmdAdvance(args); break;
  case 'kill':    cmdKill(args); break;
  case 'prune':   cmdPrune();   break;
  default:
    console.log('用法: idea.mjs list|add|advance|kill|prune');
    console.log('  add STAGE description  (STAGE: seed/proposal/running/shipped/killed/dormant)');
}
