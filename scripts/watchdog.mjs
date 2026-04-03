/**
 * watchdog.mjs — OMC 主动执行 watchdog
 *
 * 功能：session 开始时自动扫描 idea 池，识别可自动推进的条目
 * 用法：
 *   node scripts/watchdog.mjs              # 扫描并报告
 *   node scripts/watchdog.mjs --execute   # 执行可自动推进的条目
 *   node scripts/watchdog.mjs --json       # JSON 输出（供 hooks 调用）
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const IDEA_FILE = path.join(__dirname, '..', '.omc', 'innovation', 'ideas.md');

const AUTO_STAGES = ['seed', 'proposal'];
const NEEDS_CONFIRM = ['新增依赖', '跨项目', '§1', '影响未知'];

// 解析 [score:BxF] 格式
function parseScore(line) {
  const m = line.match(/\[score:(\d+)x(\d+)\]/);
  if (!m) return null;
  return { benefit: parseInt(m[1]), feasibility: parseInt(m[2]), total: parseInt(m[1]) * parseInt(m[2]) };
}

// 判断是否需要确认
function needsConfirmation(desc) {
  return NEEDS_CONFIRM.some(k => desc.includes(k));
}

// 判断是否可自动执行
function isAutoExecutable(stage, score, desc) {
  if (!AUTO_STAGES.includes(stage)) return false;
  if (!score) return false;
  if (score.total < 4) return false;
  if (score.feasibility < 3) return false; // §10: Feasibility=3 才自动
  if (needsConfirmation(desc)) return false;
  return true;
}

function scanIdeas() {
  if (!fs.existsSync(IDEA_FILE)) {
    return { ideas: [], summary: { total: 0, autoExecutable: 0, needsConfirm: 0 } };
  }

  const content = fs.readFileSync(IDEA_FILE, 'utf-8');
  const lines = content.split('\n').filter(l => l.startsWith('- ['));
  const today = new Date().toISOString().split('T')[0].replace(/-/g, '');

  const ideas = lines.map(line => {
    // 解析: - [DATE] STAGE [source] [score:BxF] description
    const dateMatch = line.match(/^\- \[(\d+)\] (\w+)/);
    const scoreMatch = parseScore(line);
    const rest = line.replace(/^\- \[\d+\] \w+(?:\s+\[\w+\])?\s+/, '').replace(/\s*\|.*$/, '');
    const desc = rest.replace(/\s*\|.*$/, '').trim();

    return {
      raw: line,
      date: dateMatch ? dateMatch[1] : null,
      stage: dateMatch ? dateMatch[2] : null,
      score: scoreMatch,
      description: desc,
      auto: dateMatch && scoreMatch ? isAutoExecutable(dateMatch[2], scoreMatch, desc) : false,
      needsConfirm: dateMatch && scoreMatch ? (scoreMatch.total >= 4 && needsConfirmation(desc)) : false,
    };
  });

  const autoIdeas = ideas.filter(i => i.auto);
  const confirmIdeas = ideas.filter(i => i.needsConfirm && !i.auto);
  const summary = {
    total: ideas.length,
    autoExecutable: autoIdeas.length,
    needsConfirm: confirmIdeas.length,
    ideas: ideas.slice(0, 20), // 最近20条
  };

  return { ideas, autoIdeas, confirmIdeas, summary };
}

function printReport(result, mode) {
  const { autoIdeas, confirmIdeas, summary } = result;

  if (mode === 'json') {
    console.log(JSON.stringify(result, null, 2));
    return;
  }

  console.log(`\n[Watchdog] ${summary.total} 个 idea 中：`);
  console.log(`  → ${summary.autoExecutable} 个可自动推进 (score≥4, Feasibility=3, 无需确认)`);
  console.log(`  → ${summary.needsConfirm} 个需你确认`);

  if (autoIdeas.length > 0) {
    console.log('\n可自动执行：');
    autoIdeas.forEach((idea, i) => {
      console.log(`  ${i + 1}. [${idea.stage}] ${idea.description.slice(0, 60)}... (score: ${idea.score.total})`);
    });
  }

  if (confirmIdeas.length > 0) {
    console.log('\n需确认：');
    confirmIdeas.forEach((idea, i) => {
      console.log(`  ${i + 1}. [${idea.stage}] ${idea.description.slice(0, 60)}... (score: ${idea.score.total})`);
    });
  }

  if (autoIdeas.length === 0 && confirmIdeas.length === 0) {
    console.log('\n无待推进 idea，idea 池健康。');
  }
}

// 简单评分建议
function suggestScores() {
  const { ideas } = scanIdeas();
  const unscored = ideas.filter(i => i.stage === 'seed' && !i.score);
  if (unscored.length > 0) {
    console.log(`\n⚠ ${unscored.length} 个 seed idea 缺少 score，建议补充 [score:BxF] 格式`);
    unscored.slice(0, 3).forEach(i => {
      console.log(`  - ${i.description.slice(0, 50)}...`);
    });
  }
}

// Main
const mode = process.argv.includes('--json') ? 'json' : process.argv.includes('--execute') ? 'execute' : 'report';
const result = scanIdeas();

if (mode === 'report') {
  printReport(result, 'report');
  suggestScores();
} else if (mode === 'json') {
  printReport(result, 'json');
} else {
  console.log('[Watchdog] execute 模式: 需要上层 agent 驱动执行');
  console.log(JSON.stringify(result.autoIdeas.map(i => ({ stage: i.stage, desc: i.description, score: i.score })), null, 2));
}
