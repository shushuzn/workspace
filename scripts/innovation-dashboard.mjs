/**
 * innovation-dashboard.mjs — 创新管道仪表盘
 *
 * 用法:
 *   node scripts/innovation-dashboard.mjs
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const IDEA_FILE = path.join(__dirname, '..', '.omc', 'innovation', 'ideas.md');

const STAGE_EMOJI = { seed: '💡', proposal: '📋', running: '🔬', shipped: '📦', killed: '💀', dormant: '⏸️' };
const TTL_DAYS = { seed: 3, proposal: 7, running: 14, shipped: null, killed: null, dormant: 30 };

function parseDate(str) {
  const s = String(str).replace(/-/g, '');
  return new Date(`${s.slice(0,4)}-${s.slice(4,6)}-${s.slice(6,8)}`);
}

function daysOld(dateStr) {
  const d = parseDate(dateStr);
  return Math.floor((new Date() - d) / 86400000);
}

function readIdeas() {
  if (!fs.existsSync(IDEA_FILE)) return [];
  const raw = fs.readFileSync(IDEA_FILE, 'utf8');
  const ideas = [];
  for (const line of raw.split('\n')) {
    const m = line.match(/^-\s*\[(\d{8})\]\s*(\w+)(?:\s*\[(\w+)\])?\s*(?:\[score:\d+x\d+\]\s*)?(.*)/);
    if (!m) continue;
    ideas.push({ date: m[1], stage: m[2], source: m[3] || 'manual', desc: m[5].trim() });
  }
  return ideas;
}

function main() {
  const ideas = readIdeas();

  // Stage counts
  const stageCounts = { seed: 0, proposal: 0, running: 0, shipped: 0, killed: 0, dormant: 0 };
  const sourceCounts = { brainstorm: 0, suggest: 0, manual: 0 };
  const overdue = [];

  for (const idea of ideas) {
    stageCounts[idea.stage] = (stageCounts[idea.stage] || 0) + 1;
    sourceCounts[idea.source] = (sourceCounts[idea.source] || 0) + 1;

    const ttl = TTL_DAYS[idea.stage];
    if (ttl && idea.stage !== 'shipped' && idea.stage !== 'killed') {
      const age = daysOld(idea.date);
      if (age > ttl) {
        overdue.push({ ...idea, overdueDays: age - ttl });
      }
    }
  }

  console.log('\n💡 创新管道状态');
  console.log('═'.repeat(42));
  const stageBar = Object.entries(stageCounts)
    .map(([s, n]) => n > 0 ? `${STAGE_EMOJI[s]} ${n}` : null)
    .filter(Boolean)
    .join('   ');
  console.log('  ' + stageBar || '(空)');

  console.log('─'.repeat(42));
  const srcLine = Object.entries(sourceCounts)
    .map(([s, n]) => n > 0 ? `${s} ${n}` : null)
    .filter(Boolean)
    .join(' | ');
  console.log('  来源: ' + srcLine);

  if (overdue.length > 0) {
    console.log('─'.repeat(42));
    console.log('  🔴 超时预警:');
    for (const o of overdue.slice(0, 5)) {
      console.log(`    ${STAGE_EMOJI[o.stage]} ${o.desc.substring(0, 40)} (+${o.overdueDays}d)`);
    }
  }

  console.log('─'.repeat(42));
  console.log('  最近活动:');
  const sorted = [...ideas].sort((a, b) => b.date.localeCompare(a.date));
  for (const idea of sorted.slice(0, 5)) {
    const emoji = STAGE_EMOJI[idea.stage] || '?';
    const src = idea.source !== 'manual' ? ` [${idea.source}]` : '';
    console.log(`    ${idea.date} ${emoji} ${idea.desc.substring(0, 35)}${src}`);
  }

  console.log('═'.repeat(42));
  console.log(`  共 ${ideas.length} 条 idea`);
  console.log('');
}

main();
