/**
 * wiki-hub-debate.mjs — Multi-agent Hub辩论结果沉淀到Wikipedia
 *
 * Usage:
 *   node wiki-hub-debate.mjs "<topic>" [--category C] [--rounds N]
 *
 * 调用multi-agent-hub进行辩论，将结果自动写入wikipedia条目
 */

import { spawn } from 'child_process';
import { readFileSync, existsSync, mkdirSync, readdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const HUB_DIR = join(__DIR, '..', '..', '80-PROJECTS', 'multi-agent-hub');
const DEBATES_DIR = join(HUB_DIR, 'debates');
const HUB_INDEX = join(DEBATES_DIR, 'index.json');

const topic = process.argv[2];
if (!topic) {
  console.log('Usage: node wiki-hub-debate.mjs "<topic>" [--category C] [--rounds N]');
  process.exit(1);
}

const catIdx = process.argv.indexOf('--category');
const roundsIdx = process.argv.indexOf('--rounds');
const category = catIdx > -1 ? process.argv[catIdx + 1] : '辩论';
const rounds = roundsIdx > -1 ? parseInt(process.argv[roundsIdx + 1]) : 3;

// ── 调用multi-agent-hub进行辩论 ──────────────────────────

async function runDebate() {
  return new Promise((resolve, reject) => {
    const startCount = readdirSync(DEBATES_DIR).filter(f => f.endsWith('.json')).length;
    console.log(`[wiki-hub] Starting debate on: ${topic}`);
    const p = spawn('node', [join(HUB_DIR, 'index.js'), '--topic', topic, '--mode', 'debate', '--rounds', String(rounds)], {
      stdio: 'inherit',
      cwd: HUB_DIR
    });
    p.on('close', (code) => {
      if (code !== 0) { reject(new Error(`Debate exited with code ${code}`)); return; }
      // 找到最新生成的辩论文件
      let attempts = 0;
      const findNew = () => {
        const files = readdirSync(DEBATES_DIR).filter(f => f.endsWith('.json'));
        const newFiles = files.filter(f => !f.includes('index'));
        if (newFiles.length > startCount) {
          const latest = newFiles.sort().reverse()[0];
          resolve(latest);
        } else if (++attempts < 10) {
          setTimeout(findNew, 1000);
        } else {
          reject(new Error('No new debate file found'));
        }
      };
      findNew();
    });
  });
}

// ── 从辩论JSON提取维基百科内容 ───────────────────────────

function extractWikiContent(debateFile) {
  const data = JSON.parse(readFileSync(debateFile, 'utf8'));

  // 提取各方立场
  const positions = {};
  for (const entry of (data.transcript || [])) {
    const name = entry.persona?.name || 'Unknown';
    if (!positions[name]) positions[name] = [];
    const text = entry.text || '';
    // 截取前200字作为立场摘要
    if (text.length > 20) positions[name].push(text.slice(0, 200));
  }

  const positionSummaries = Object.entries(positions)
    .map(([name, texts]) => `### ${name}\n\n${texts[0] || '（无立场摘要）'}`)
    .join('\n\n');

  const votes = data.votes || { pro: 0, con: 0, neutral: 0 };
  const voteResult = data.mode === 'DEBATE' || data.mode === 'debate'
    ? `正方 ${votes.pro} vs 反方 ${votes.con}（中立 ${votes.neutral}）`
    : '（非投票模式）';

  const body = `## 辩论主题\n\n${data.topic}\n\n## 辩论概要\n\n${data.summary || '（无摘要）'}\n\n## 投票结果\n\n${voteResult}\n\n## 各方立场\n\n${positionSummaries}\n\n## 退火统计\n\n${data.annealing ? `- 初始温度: ${data.annealing.initialTemp}\n- 最终温度: ${data.annealing.finalTemp}\n- 最大ΔS: ${data.annealing.peakDeltaS}\n- 辩论轮次: ${data.annealing.roundsRun}` : '（无退火统计）'}\n\n## 辩论时间\n\n${data.timestamp}\n\n## 相关条目\n\n[[multi-agent-hub]]`;

  return {
    title: `辩论：${data.topic}`,
    body,
    tags: ['辩论', 'multi-agent-hub', `轮次${rounds}`]
  };
}

// ── 主流程 ──────────────────────────────────────────────

async function main() {
  try {
    const debateFile = await runDebate();
    console.log(`[wiki-hub] Debate saved: ${debateFile}`);

    const { title, body, tags } = extractWikiContent(join(DEBATES_DIR, debateFile));

    // 调用wiki.mjs create写入wikipedia
    const wikiCreate = spawn('node', [join(__DIR, 'wiki.mjs'), 'create', title, '--category', category, '--tags', tags.join(',')], {
      stdio: 'inherit'
    });

  } catch (e) {
    console.error('[wiki-hub] Error:', e.message);
    process.exit(1);
  }
}

main();
