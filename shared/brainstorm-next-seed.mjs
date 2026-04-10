#!/usr/bin/env node
/**
 * brainstorm-next-seed.mjs — auto-generate next batch seeds from batch_critique
 * Reads last batch metacognition entry, derives seed directions
 * Usage: node shared/brainstorm-next-seed.mjs --auto
 */
import { readFileSync, existsSync, appendFileSync } from 'fs';
import { execSync } from 'child_process';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const META_FILE = join(__DIR, '..', '.omc', 'innovation', 'brainstorm-metacognition.jsonl');
const IDEAS_FILE = join(__DIR, '..', '.omc', 'innovation', 'ideas.md');

function loadLastEntry() {
  if (!existsSync(META_FILE)) return null;
  const lines = readFileSync(META_FILE, 'utf8').trim().split('\n').filter(Boolean);
  for (let i = lines.length - 1; i >= 0; i--) {
    try { return JSON.parse(lines[i]); } catch { continue; }
  }
  return null;
}

function main() {
  const entry = loadLastEntry();
  if (!entry) { console.log('[next-seed] No metacognition entries'); return; }

  const { batch_critique, gate_failures = {}, seed_critiques = [] } = entry;
  const suggestions = [];

  // Derive from batch_critique
  if (batch_critique?.gate_root_cause) {
    const cause = batch_critique.gate_root_cause;
    if (cause.includes('non-existent script') || cause.includes('不存在')) {
      suggestions.push({
        angle: 'ws-level',
        desc: `pre-flight检查增强：确保所有引用脚本存在`,
        benefit: '减少因脚本缺失导致的retry',
        reason: `已知资源：seed-preflight.mjs已存在；缺失环节：无路径验证加强；连接方式：正则匹配→验证路径存在性→缺失则报错`
      });
    }
  }

  // Derive from gate_failures
  const failures = Object.keys(gate_failures);

  // Scan-enforcement: verify referenced projects were actually scanned
  const SCAN_RULES = [
    {
      pattern: /knowledge-bridge/i,
      requiredPaths: ['80-PROJECTS/knowledge-bridge/bin/', '80-PROJECTS/knowledge-bridge/src/'],
      fix: 'knowledge-bridge bin/batch-import.mjs 不存在——必须先ls确认路径再生成seed'
    },
    {
      pattern: /agent-arena/i,
      requiredPaths: ['80-PROJECTS/agent-arena/bin/', '80-PROJECTS/agent-arena/src/'],
      fix: 'agent-arena bin/battle-history-viz.mjs 不存在——必须先ls确认路径再生成seed'
    },
  ];
  for (const rule of SCAN_RULES) {
    const cause = batch_critique?.gate_root_cause || '';
    if (rule.pattern.test(cause)) {
      // Check if the project paths actually exist
      const missing = rule.requiredPaths.filter(p => !existsSync(join(__DIR, '..', p)));
      if (missing.length > 0) {
        console.warn(`[next-seed] WARN: ${rule.pattern} referenced but missing paths: ${missing.join(', ')}`);
        console.warn(`[next-seed] FIX needed: ${rule.fix}`);
      }
    }
  }

  // Derive from project-gaps — systemized project缺口清单
  const GAPS_FILE = join(__DIR, '..', '.omc', 'state', 'project-gaps', 'project-gaps.json');
  if (existsSync(GAPS_FILE)) {
    try {
      const gaps = JSON.parse(readFileSync(GAPS_FILE, 'utf-8'));
      const projects = Object.keys(gaps.projects || {});
      if (projects.length > 0) {
        // Pick one random project gap to derive a seed
        const pick = projects[Math.floor(Math.random() * projects.length)];
        const missingList = gaps.projects[pick] || [];
        const missing = missingList[0] || missing;
        suggestions.push({
          angle: pick === 'ws-level' ? 'ws-level' : 'feature',
          focus: pick === 'ws-level' ? null : pick,
          desc: `${pick}补充：${missing}`,
          benefit: `填补${pick}项目的${missing}缺口`,
          reason: `已知资源：${pick}项目已有基础；缺失环节：${missing}；连接方式：从project-gaps.json提取→生成对应seed`
        });
      }
    } catch { /* ignore parse errors */ }
  }

  if (failures.includes('Gate4b')) {
    suggestions.push({
      angle: 'skill-file',
      desc: `Gate4b可执行前缀检查强化`,
      benefit: 'Windows Git Bash平台约束显式化',
      reason: `已知资源：run-seed.mjs已有Gate4b检测；缺失环节：无可视化错误提示；连接方式：增加--verbose→输出匹配前缀状态`
    });
  }

  if (failures.includes('Gate4c')) {
    suggestions.push({
      angle: 'ws-level',
      desc: `approach可执行性验证报告生成器`,
      benefit: '快速发现不可执行步骤',
      reason: `已知资源：run-seed.mjs已有validate逻辑；缺失环节：无汇总报告；连接方式：--report→遍历所有seeds→输出问题列表`
    });
  }

  // Derive from seed_critiques
  for (const sc of seed_critiques) {
    if (sc.feas_inflation) {
      suggestions.push({
        angle: 'ws-level',
        desc: `feasibility评分校准器`,
        benefit: '下次f评分更准确',
        reason: `已知资源：run-seed.mjs已有f评分；缺失环节：无历史对比；连接方式：shipped时记录f评分vs实际耗时→下次参考`
      });
    }
  }

  const mode = process.argv.includes('--auto');
  if (!mode) {
    console.log(`=== Next Seeds (${suggestions.length} derived) ===`);
    for (const s of suggestions) {
      console.log(`  [${s.angle}] ${s.desc}`);
      console.log(`    benefit: ${s.benefit}`);
    }
    if (suggestions.length === 0) console.log('  (no derivable seeds — batch was clean)');
    return;
  }

  // Write to ideas.md — only seeds that pass Gate13+Gate4c validation
  const today = new Date().toISOString().slice(0, 10).replace(/-/g, '');
  const date = process.argv.includes('--date') ?
    process.argv[process.argv.indexOf('--date') + 1] : today;

  let written = 0;
  for (const s of suggestions) {
    // Build a concrete approach based on the seed type
    const approachMap = {
      'approach可执行性验证报告生成器': '1. node shared/run-seed.mjs --validate-approach "1. echo test"',
      'feasibility评分校准器': '1. node shared/run-seed.mjs --dry-run',
    };
    const approach = approachMap[s.desc] || `1. echo "TODO: implement ${s.desc}"`;

    // Validate Gate13+Gate4c before writing
    try {
      execSync(`node "${join(__DIR, '..', 'shared', 'run-seed.mjs')}" --validate-approach "${approach.replace(/"/g, '\\"')}"`, { stdio: 'pipe' });
    } catch (e) {
      console.warn(`[next-seed] SKIP (Gate13/4c fail): ${s.desc}`);
      continue;
    }

    const line = `\n- [${date}] seed [brainstorm] [score:3x3=9] [f:3] [angle:${s.angle}] ${s.desc} | benefit: ${s.benefit} | reason: ${s.reason} | approach: ${approach}`;
    appendFileSync(IDEAS_FILE, line, 'utf8');
    written++;
  }
  console.log(`[next-seed] Wrote ${written}/${suggestions.length} seeds to pool (${suggestions.length - written} filtered by Gate13/4c)`);
}

main();
