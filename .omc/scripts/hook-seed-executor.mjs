#!/usr/bin/env node
/**
 * OMC Seed Executor
 * Spawned by hook-auto-seed.mjs when threshold fires.
 * Picks highest-score un-shipped seed from ideas.md, executes its approach, marks shipped.
 *
 * Usage:
 *   node hook-seed-executor.mjs [--dry-run]
 *
 * Detached execution: sets OMC_SKIP_HOOKS to prevent re-triggering hook-auto-seed.
 */
import { existsSync, readFileSync, writeFileSync, appendFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const IDEAS_FILE = resolve(__dirname, '../innovation/ideas.md');
const SEEDS_MARKER = '## Seeds';
const STATE_FILE = resolve(__dirname, '../state/seed-executor.json');

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i++) {
    if (argv[i].startsWith('--')) {
      const key = argv[i].slice(2);
      args[key] = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : true;
    }
  }
  return args;
}

// ── Parse seeds from ideas.md ──────────────────────────────────────────────
function parseSeeds(content) {
  const lines = content.split('\n');
  const seeds = [];
  let inSeeds = false;

  for (const line of lines) {
    if (line.startsWith(SEEDS_MARKER) || line.startsWith('## Seeds')) {
      inSeeds = true;
      continue;
    }
    if (inSeeds && line.startsWith('## ')) break; // Next section
    if (line.startsWith('- [')) {
      const seed = parseSeedLine(line);
      if (seed) seeds.push(seed);
    }
  }
  return seeds;
}

function parseSeedLine(line) {
  // Format: - [DATE] STAGE [source] [score:B×F=X] [f:F] description | benefit: ... | reason: ... | approach: ... [shipped:DATE]
  const dateMatch = line.match(/^\- \[(\d{4}-\d{2}-\d{2})\]/);
  const stageMatch = line.match(/STAGE \[([^\]]+)\]/);
  const scoreMatch = line.match(/\[score:(\d+)×(\d+)=(\d+)\]/);
  const fMatch = line.match(/\[f:(\d+)\]/);
  const benefitMatch = line.match(/benefit:\s*([^|]+)/);
  const reasonMatch = line.match(/reason:\s*([^|]+)/);
  const approachMatch = line.match(/approach:\s*([^|]+)/);
  const shippedMatch = line.match(/shipped:(\d{4}-\d{2}-\d{2})/);
  const killedMatch = line.match(/killed:/);

  // Extract description (between f:X] and | benefit:)
  const afterF = line.match(/\] (.+?)(?:\s*\| benefit:)/);
  const description = afterF ? afterF[1].trim() : null;

  if (!dateMatch || !scoreMatch || !approachMatch) return null;

  return {
    raw: line,
    date: dateMatch[1],
    stage: stageMatch ? stageMatch[1] : 'unknown',
    benefit: parseInt(scoreMatch[1]),
    feasibility: parseInt(scoreMatch[2]),
    score: parseInt(scoreMatch[3]),
    fValue: fMatch ? parseInt(fMatch[1]) : null,
    description: description,
    benefitDesc: benefitMatch ? benefitMatch[1].trim() : null,
    reason: reasonMatch ? reasonMatch[1].trim() : null,
    approach: approachMatch[1].trim(),
    shipped: shippedMatch ? shippedMatch[1] : null,
    killed: !!killedMatch,
    // Extract AUTO: marker for management seeds
    isAuto: line.includes('[AUTO:') || stageMatch?.[1]?.startsWith('AUTO:'),
    autoMarker: line.match(/AUTO:([\w-]+)/)?.[1] || null,
  };
}

function getUnshipedSeeds(seeds) {
  return seeds.filter(s => !s.shipped && !s.killed);
}

function pickHighestScore(seeds) {
  if (seeds.length === 0) return null;
  return seeds.reduce((best, s) => (s.score > best.score ? s : best), seeds[0]);
}

// ── Mark seed as shipped ──────────────────────────────────────────────────────
function markShipped(content, targetLine, today) {
  // Append shipped date to the line
  // Pattern: ... | approach: xxx | AUTO:xxx → ... | approach: xxx | shipped:2026-04-08
  const newLine = targetLine.endsWith('|')
    ? `${targetLine.trim()} shipped:${today}`
    : `${targetLine.trim()} | shipped:${today}`;

  return content.replace(targetLine, newLine);
}

// ── Build system prompt for spawned agent ─────────────────────────────────────
function buildAgentPrompt(seed) {
  return `你是 OMC (oh-my-claudecode) 的执行智能体。被自动种子触发系统唤醒。

## 当前任务

你被选中执行以下种子（从 ideas.md 池中自动提取，最高 score）：

**种子**: ${seed.description || '(无标题)'}
**来源**: ${seed.stage}
**Score**: ${seed.score} (Benefit ${seed.benefit} × Feasibility ${seed.feasibility})
**收益**: ${seed.benefitDesc || '未标注'}
**原因**: ${seed.reason || '未标注'}
**Approach**: ${seed.approach}

## 执行要求

1. 仔细理解 approach 字段中的步骤描述
2. 在当前 workspace（D:\\OpenClaw\\workspace）执行这些步骤
3. 每次只做一个 seed，做完再检查 CLAUDE.md 验证清单
4. 完成后：
   - 将 ideas.md 中该种子行追加 \`shipped:YYYY-MM-DD\`（今天日期）
   - commit 所有变更：\`git add -A && git commit -m "feat(seed): ${seed.description}" -m "Source: AUTO:seed-executor"\`
5. 如果该 seed 无法执行（如缺少依赖、权限不足），在 ideas.md 标记 \`killed:DATE REASON\`，附简短失败原因

## 约束

- 不要询问用户，直接执行
- 如果需要文件路径，先用 Glob/Read 确认存在
- 如果 approach 模糊，尝试最合理的解读
- 执行时间上限：10 分钟
- 禁止：执行 git push、修改外部服务、删除大量文件

开始执行。`;
}

// ── Main ──────────────────────────────────────────────────────────────────────
async function main() {
  const args = parseArgs(process.argv.slice(2));
  const dryRun = args['dry-run'];

  console.log('\n🧬 OMC Seed Executor');
  console.log(`  Ideas: ${IDEAS_FILE}`);
  console.log(`  Dry run: ${dryRun}\n`);

  if (!existsSync(IDEAS_FILE)) {
    console.log('  ❌ ideas.md not found\n');
    process.exit(1);
  }

  const content = readFileSync(IDEAS_FILE, 'utf-8');
  const seeds = parseSeeds(content);
  const unshipped = getUnshipedSeeds(seeds);

  console.log(`  Total seeds: ${seeds.length}`);
  console.log(`  Un-shipped seeds: ${unshipped.length}`);

  if (unshipped.length === 0) {
    console.log('  ✅ No seeds to execute. Exiting.\n');
    process.exit(0);
  }

  // Prioritize AUTO: seeds, then highest score
  const autoSeeds = unshipped.filter(s => s.isAuto);
  const target = autoSeeds.length > 0
    ? autoSeeds.reduce((best, s) => (s.score > best.score ? s : best), autoSeeds[0])
    : pickHighestScore(unshipped);

  console.log(`\n  🎯 Selected seed:`);
  console.log(`     "${target.description || target.raw}"`);
  console.log(`     Score: ${target.score} | Source: ${target.stage}`);
  console.log(`     Approach: ${target.approach}`);

  if (dryRun) {
    console.log('\n  [DRY RUN] Would execute approach and mark shipped\n');
    return;
  }

  // Write executor state
  const today = new Date().toISOString().split('T')[0];
  const state = {
    seed: {
      description: target.description,
      stage: target.stage,
      score: target.score,
      approach: target.approach,
      rawLine: target.raw,
    },
    startedAt: new Date().toISOString(),
    targetDate: today,
  };
  writeFileSync(STATE_FILE, JSON.stringify(state, null, 2), 'utf-8');

  // If OMC_SEED_PROMPT_FILE is set (from hook-auto-seed.mjs), write prompt there
  const promptFile = process.env.OMC_SEED_PROMPT_FILE;
  const prompt = buildAgentPrompt(target);
  if (promptFile) {
    writeFileSync(promptFile, prompt, 'utf-8');
    console.log(`\n  ✅ Seed selected (agent will mark shipped after execution)`);
    console.log(`  Prompt written: ${promptFile}`);
    console.log(`  State: ${STATE_FILE}\n`);
  } else {
    console.log('\n---AGENT-PROMPT-BEGIN---');
    console.log(prompt);
    console.log('---AGENT-PROMPT-END---');
    console.log(`\n  ✅ Seed selected (agent will mark shipped after execution)\n`);
  }
}

main().catch(e => { console.error('seed-executor error:', e.message); process.exit(1); });
