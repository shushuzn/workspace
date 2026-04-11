#!/usr/bin/env node
/**
 * brainstorm-next-seed.mjs — auto-generate next batch seeds from batch_critique + external sources
 * Reads last 5 metacognition entries + session-insights + GitHub Trending, derives seed directions
 * Usage: node shared/brainstorm-next-seed.mjs --auto
 *
 * Tasks #12/#8/#11: replaced hardcoded suggestions with dynamic derivation:
 * - Task #12: scan last 5 metacognition entries for gate_failures + seed_critiques patterns
 * - Task #8: parse feas_inflation + reason_discrepancy + approach_drift → specific seeds
 * - Task #11: external innovation sources (GitHub Trending, session-insights Fix entries)
 */
import { readFileSync, existsSync, appendFileSync } from 'fs';
import { execSync } from 'child_process';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const META_FILE = join(__DIR, '..', '.omc', 'innovation', 'brainstorm-metacognition.jsonl');
const SESSION_INSIGHTS = join(__DIR, '..', '.omc', 'state', 'session-insights.md');
const GAPS_FILE = join(__DIR, '..', '.omc', 'state', 'project-gaps', 'project-gaps.json');
const IDEAS_FILE = join(__DIR, '..', '.omc', 'innovation', 'ideas.md');

// ─── Core loading ───────────────────────────────────────────────────────────────

function loadRecentMetaEntries(count = 5) {
  if (!existsSync(META_FILE)) return [];
  const lines = readFileSync(META_FILE, 'utf8').trim().split('\n').filter(Boolean);
  const entries = [];
  for (let i = lines.length - 1; i >= 0 && entries.length < count; i--) {
    try { entries.push(JSON.parse(lines[i])); } catch { /* skip malformed */ }
  }
  return entries; // newest first
}

function loadSessionInsightsFixEntries() {
  // Extract Fix lines where Fix != N/A from session-insights.md
  if (!existsSync(SESSION_INSIGHTS)) return [];
  const content = readFileSync(SESSION_INSIGHTS, 'utf8');
  const fixes = [];
  // Match lines like "**Fix**: some text" that are not "N/A"
  const re = /^\*\*Fix\*\*:\s*(.+)/gm;
  let m;
  while ((m = re.exec(content)) !== null) {
    const val = m[1].trim();
    if (val && val !== 'N/A' && !val.startsWith('N/A')) {
      fixes.push(val);
    }
  }
  return fixes;
}

function projectExists(relativePath) {
  return existsSync(join(__DIR, '..', relativePath));
}

// ─── Source 1: metacognition — gate failure patterns ──────────────────────────

function deriveFromGateFailures(entries) {
  const suggestions = [];
  const failureTally = {};
  for (const entry of entries) {
    const failures = entry.gate_failures || {};
    for (const [gate, count] of Object.entries(failures)) {
      failureTally[gate] = (failureTally[gate] || 0) + count;
    }
  }

  // Gate4b failures → skill-file enforcement seed
  if (failureTally['Gate4b']) {
    suggestions.push({
      angle: 'skill-file',
      desc: 'Gate4b可执行前缀检查强化',
      benefit: 'Windows Git Bash平台约束显式化，减少approach预验证失败',
      reason: '已知资源：run-seed.mjs已有Gate4b检测；缺失环节：无可视化错误提示和预检查；连接方式：增加--verbose→输出匹配前缀状态，ship前强制检查'
    });
  }

  // Gate4c failures → approach validation reporter
  if (failureTally['Gate4c']) {
    suggestions.push({
      angle: 'ws-level',
      desc: 'approach可执行性验证报告生成器',
      benefit: '快速发现不可执行步骤，减少Gate4c失败率',
      reason: '已知资源：run-seed.mjs已有validate逻辑；缺失环节：无汇总报告；连接方式：--report→遍历所有seeds→输出问题列表'
    });
  }

  // Gate13 failures → project scan enforcement
  if (failureTally['Gate13']) {
    suggestions.push({
      angle: 'ws-level',
      desc: 'Gate13项目路径预扫描',
      benefit: '避免seed引用不存在的脚本路径，消灭Gate13失败',
      reason: '已知资源：brainstorm-metacognition记录了Gate13失败；缺失环节：无项目文件预扫描；连接方式：seed生成前扫描目标项目目录结构，验证引用路径'
    });
  }

  return suggestions;
}

// ─── Source 2: seed_critiques — three failure modes ───────────────────────────

function deriveFromSeedCritiques(entries) {
  const suggestions = [];
  const seen = new Set();

  for (const entry of entries) {
    const critiques = entry.seed_critiques || [];
    for (const sc of critiques) {
      // feas_inflation: f:4→actual failure(Gate4c) → feasibility calibrator
      if (sc.feas_inflation && !seen.has('feas_inflation')) {
        seen.add('feas_inflation');
        suggestions.push({
          angle: 'ws-level',
          desc: 'feasibility评分校准器',
          benefit: '下次f评分更准确，减少Gate4c/failure因预估过高',
          reason: '已知资源：run-seed.mjs已有f评分；缺失环节：无历史对比校准；连接方式：shipped时记录f评分vs实际耗时→下次参考调整'
        });
      }

      // reason_discrepancy: script path fabricated → reason accuracy checker
      if (sc.reason_discrepancy && !seen.has('reason_discrepancy')) {
        seen.add('reason_discrepancy');
        suggestions.push({
          angle: 'ws-level',
          desc: 'reason准确性检查器',
          benefit: '防止reason描述与实际不符，减少误导性seed',
          reason: '已知资源：metacognition记录了reason_discrepancy（如bin/xxx.mjs不存在）；缺失环节：无reason与实际文件对比验证；连接方式：seed生成时验证reason中引用的文件/路径是否真实存在'
        });
      }

      // approach_drift: script path fabricated → approach drift detector
      if (sc.approach_drift && !seen.has('approach_drift')) {
        seen.add('approach_drift');
        suggestions.push({
          angle: 'ws-level',
          desc: 'approach drift检测器',
          benefit: '检测seed实现与原始描述的偏离，保证shipped内容与desc一致',
          reason: '已知资源：metacognition记录了approach_drift（如只运行了测试未实际集成）；缺失环节：无drift对比验证；连接方式：ship前对比approach步骤vs实际实现的文件变更'
        });
      }
    }
  }

  return suggestions;
}

// ─── Source 3: session-insights Fix entries ────────────────────────────────────

function deriveFromSessionInsights() {
  const fixes = loadSessionInsightsFixEntries();
  const suggestions = [];

  // Group fixes by theme (simple keyword clustering)
  const themes = {
    'hook-state-inspection': fixes.filter(f => /hook.*stat|状态.*检查|inspection.*loop/i.test(f)),
    'bash-dominance': fixes.filter(f => /bash.*domin|自我检查循环|状态巡查/i.test(f)),
    'seed-generation': fixes.filter(f => /seed.*zero|0.*seed|insight.*pipeline/i.test(f)),
    'task-tracking': fixes.filter(f => /task.*track|TaskCreate|零.*task/i.test(f)),
    'workflow-consolidation': fixes.filter(f => /consolidat|dashboard|hook-stats/i.test(f)),
  };

  for (const [theme, items] of Object.entries(themes)) {
    if (items.length >= 2) {
      if (theme === 'hook-state-inspection' || theme === 'bash-dominance') {
        suggestions.push({
          angle: 'ws-level',
          desc: 'OMC状态检查统一入口',
          benefit: '消灭重复状态巡查命令，用1个脚本替代10个手动bash',
          reason: '已知资源：session-insights记录了多次重复状态检查模式；缺失环节：无统一入口；连接方式：扩展hook-stats.mjs覆盖所有状态文件，替代topBash中的ls/wc/tail链'
        });
      } else if (theme === 'seed-generation') {
        suggestions.push({
          angle: 'ws-level',
          desc: 'brainstorm种子枯竭应对：外部来源扩展',
          benefit: '打破executor.mjs扫描的种子来源垄断，补充外部创新',
          reason: '已知资源：session-insights多次记录0 seeds产出；缺失环节：种子来源单一（仅executor.mjs扫描）；连接方式：从GitHub Trending和session-insights Fix条目派生种子'
        });
      } else if (theme === 'task-tracking') {
        suggestions.push({
          angle: 'ws-level',
          desc: 'OMC任务追踪集成',
          benefit: '让高工具调用量session留下可审计的进度记录',
          reason: '已知资源：session-insights记录了零TaskCreate的high-activity session；缺失环节：任务系统未被使用；连接方式：在hook-auto-seed.mjs中当count>阈值时自动创建Task'
        });
      }
    }
  }

  return suggestions;
}

// ─── Source 4: GitHub Trending ───────────────────────────────────────────────

function deriveFromGitHubTrending() {
  // Fetch GitHub Trending (top 3 projects for novelty extraction)
  // Returns seed suggestions based on novel patterns observed
  try {
    const url = 'https://api.github.com/search/repositories?q=stars:>1000+pushed:>2026-01-01&sort=stars&order=desc&per_page=10';
    const raw = execSync(
      'curl -s --max-time 10 -H "Accept: application/vnd.github.v3+json" "' + url + '"',
      { stdio: 'pipe', windowsHide: true }
    ).toString('utf8');
    const data = JSON.parse(raw);
    const repos = (data.items || []).slice(0, 5);
    const suggestions = [];

    for (const repo of repos) {
      const name = repo.full_name;
      const desc = repo.description || '';
      // Detect novel patterns from description
      if (/agent|coding.*agent|autonomous.*coding/i.test(desc)) {
        suggestions.push({
          angle: 'skill-file',
          desc: name + '模式迁移：' + name.split('/')[1].slice(0, 30),
          benefit: '将' + name + '的novel模式迁移到workspace',
          reason: '已知资源：GitHub Trending ' + name + '；novel点：' + desc.slice(0, 60) + '；缺失环节：workspace无此模式；连接方式：扫描' + name + '的skill文件→提取可迁移的pattern'
        });
      }
    }

    return suggestions;
  } catch {
    return []; // Network failure → skip
  }
}

// ─── Source 5: project-gaps ───────────────────────────────────────────────────

function deriveFromProjectGaps() {
  if (!existsSync(GAPS_FILE)) return [];
  try {
    const gaps = JSON.parse(readFileSync(GAPS_FILE, 'utf-8'));
    const projects = Object.keys(gaps.projects || {});
    const suggestions = [];
    let gapCount = 0;

    for (const pick of projects) {
      if (gapCount >= 1) break;
      const missingList = gaps.projects[pick] || [];
      for (const item of missingList) {
        if (gapCount >= 1) break;
        const filePathMatch = item.match(/([A-Z]:[\\\/][^\s；;]+)/);
        if (!filePathMatch) continue;
        const missing = item.split('→')[0].trim();
        const connection = item.includes('→') ? item.split('→')[1].trim() : '';
        const desc = pick + '补充：' + missing;
        suggestions.push({
          angle: pick === 'ws-level' ? 'ws-level' : 'feature',
          focus: pick === 'ws-level' ? null : pick,
          desc,
          benefit: '填补' + pick + '项目的' + missing + '缺口',
          reason: '已知资源：' + pick + '已有基础；缺失环节：' + missing + '；连接方式：' + (connection || '创建' + filePathMatch[1])
        });
        gapCount++;
      }
    }
    return suggestions;
  } catch {
    return [];
  }
}

// ─── Source 6a: shared-scripts real feature scan ────────────────────────────────

function deriveFromSharedScriptsReal() {
  const suggestions = [];
  try {
    const { readdirSync } = require('fs');
    const sharedDir = join(__DIR, '..', 'shared');
    if (!existsSync(sharedDir)) return [];
    const files = readdirSync(sharedDir).filter(f => f.endsWith('.mjs') && !f.includes('patch') && !f.includes('run-seed') && !f.includes('brainstorm'));

    // Loop to find a script with missing flags
    for (const targetFile of files) {
      try {
        const helpOut = execSync(`node "${join(sharedDir, targetFile)}" --help 2>/dev/null || true`, { stdio: 'pipe', windowsHide: true }).toString();
        const hasHelp = helpOut.includes('--help') || helpOut.includes('usage') || helpOut.includes('Usage');
        // Only consider scripts that have --help (interactive scripts don't count)
        if (!hasHelp) continue;

        const missingFlags = [];
        if (!helpOut.includes('--json')) missingFlags.push('--json');
        if (!helpOut.includes('--watch')) missingFlags.push('--watch');
        if (!helpOut.includes('--quiet')) missingFlags.push('--quiet');

        if (missingFlags.length > 0) {
          const flag = missingFlags[0];
          suggestions.push({
            angle: 'ws-level',
            desc: `shared/${targetFile} 增加${flag}输出模式`,
            benefit: `让脚本支持结构化输出，便于集成到CI/CD pipeline`,
            reason: `已知资源：shared/${targetFile} 存在并有--help；缺失环节：无${flag}模式；连接方式：解析命令行参数→增加${flag}分支→输出结构化数据`,
            focus: null,
          });
          break; // only one suggestion per batch
        }
      } catch { continue; }
    }
  } catch { /* skip */ }
  return suggestions;
}

// ─── Source 6b: 80-PROJECTS bin scripts scan ──────────────────────────────────

function deriveFromProjectBins() {
  const suggestions = [];
  try {
    const { readdirSync } = require('fs');
    const projectsDir = join(__DIR, '..', '80-PROJECTS');
    if (!existsSync(projectsDir)) return [];
    const projects = readdirSync(projectsDir).filter(f => existsSync(join(projectsDir, f, 'bin')));
    if (projects.length === 0) return [];
    // Pick one project with bin/
    const pick = projects[0];
    const binDir = join(projectsDir, pick, 'bin');
    const bins = readdirSync(binDir).filter(f => f.endsWith('.mjs') || f.endsWith('.js'));
    if (bins.length === 0) return [];
    const target = bins[0];

    // Check for missing --json or --watch
    let missingFlags = [];
    try {
      const helpOut = execSync(`node "${join(binDir, target)}" --help 2>/dev/null || true`, { stdio: 'pipe', windowsHide: true }).toString();
      if (!helpOut.includes('--json')) missingFlags.push('--json');
      if (!helpOut.includes('--watch')) missingFlags.push('--watch');
      if (!helpOut.includes('--quiet')) missingFlags.push('--quiet');
    } catch { /* skip */ }

    if (missingFlags.length > 0) {
      const flag = missingFlags[0];
      suggestions.push({
        angle: 'feature',
        focus: pick,
        desc: `${target} 增加${flag}模式`,
        benefit: `让${pick}支持结构化输出，便于监控集成`,
        reason: `已知资源：${pick}/bin/${target} 存在并有--help；缺失环节：无${flag}模式；连接方式：解析命令行→增加${flag}分支→输出结构化数据`,
      });
    }
  } catch { /* skip */ }
  return suggestions;
}

// ─── Source 6: shared-scripts syntax scan ──────────────────────────────────────

function deriveFromSharedScripts() {
  const suggestions = [];
  try {
    const { execSync } = require('child_process');
    const sharedDir = join(__DIR, '..', 'shared');
    const files = readdirSync(sharedDir).filter(f => f.endsWith('.mjs') && !f.includes('patch'));
    for (const file of files) {
      const path = join(sharedDir, file);
      try {
        execSync(`node --check "${path}"`, { stdio: 'pipe', windowsHide: true });
      } catch (e) {
        const err = e.stderr?.toString() || '';
        const match = err.match(/SyntaxError: (.+)/);
        const reason = match ? match[1].trim() : 'unknown syntax error';
        suggestions.push({
          angle: 'ws-level',
          desc: `${file} 语法错误修复 — ${reason.slice(0, 50)}`,
          benefit: `修复 shared/${file} 的语法错误，恢复脚本可用性`,
          reason: `已知资源：shared/${file} 存在；缺失环节：SyntaxError 导致脚本无法运行；连接方式：检查错误位置→修复语法问题→通过 node --check`
        });
        break; // one at a time
      }
    }
  } catch { /* skip on failure */ }
  return suggestions;
}

// ─── Source 7: scan executors for inefficient patterns ─────────────────────────

function deriveFromCodeScan() {
  const suggestions = [];
  try {
    const { execSync } = require('child_process');
    const dirs = [
      '80-PROJECTS/task-orchestrator/src',
      '80-PROJECTS/task-orchestrator/bin',
    ];
    for (const dir of dirs) {
      const fullPath = join(__DIR, '..', dir);
      if (!existsSync(fullPath)) continue;
      const files = readdirSync(fullPath).filter(f => f.endsWith('.mjs'));
      for (const file of files) {
        const path = join(fullPath, file);
        // Check for TODO comments that indicate missing implementation
        const content = readFileSync(path, 'utf8');
        const todos = [];
        const re = /\/\/\s*(TODO|FIXME|HACK|XXX):\s*(.+)/g;
        let m;
        while ((m = re.exec(content)) !== null) {
          todos.push({ line: content.slice(0, m.index).split('\n').length, note: m[2].slice(0, 60) });
        }
        if (todos.length > 0) {
          const t = todos[0];
          suggestions.push({
            angle: 'feature',
            focus: 'task-orchestrator',
            desc: `${file} TODO注释实现 — ${t.note}`,
            benefit: `消除 TODO 注释，推动真实功能落地`,
            reason: `已知资源：${dir}/${file} 存在；缺失环节：${t.note}；连接方式：读取TODO内容→实现对应功能→删除TODO注释`
          });
        }
        // Check for inefficient O(n²) patterns in executor
        if (file === 'executor.mjs' && content.includes('for (const ')) {
          const nestedFor = content.match(/for\s*\(\s*const\s+\w+\s+of\s+[^}]+\)\s*\{[\s\S]*?for\s*\(\s*const\s+/g);
          if (nestedFor && nestedFor.length > 0) {
            suggestions.push({
              angle: 'feature',
              focus: 'task-orchestrator',
              desc: `executor.mjs 嵌套循环优化 — ${nestedFor.length}处嵌套for-of`,
              benefit: `减少嵌套循环次数，提升大chain执行性能`,
              reason: `已知资源：executor.mjs 存在嵌套for-of；缺失环节：无复杂度控制；连接方式：识别嵌套模式→用Map/Set去重→O(n²)→O(n)`
            });
          }
        }
      }
      if (suggestions.length > 0) break;
    }
  } catch { /* skip */ }
  return suggestions;
}

// ─── Source 8: hookify broken rules scan ────────────────────────────────────

function deriveFromHookifyScan() {
  const suggestions = [];
  try {
    const hookifyDir = join(__DIR, '..', '.claude');
    if (!existsSync(hookifyDir)) return [];
    const files = readdirSync(hookifyDir).filter(f => f.startsWith('hookify.') && f.endsWith('.local.md'));
    for (const file of files) {
      const path = join(hookifyDir, file);
      const content = readFileSync(path, 'utf8');
      // Check for deprecated/broken markers
      if (/⚠️|❌|deprecated|broken/i.test(content)) {
        const ruleName = file.replace('hookify.', '').replace('.local.md', '');
        suggestions.push({
          angle: 'hookify',
          desc: `hookify规则 ${ruleName} 修复或移除`,
          benefit: `清理失效规则，保持hookify警觉性准确`,
          reason: `已知资源：.claude/${file} 存在并标记为失效；缺失环节：失效规则产生噪声；连接方式：读取规则内容→判断可修复或移除→更新规则`
        });
      }
    }
  } catch { /* skip */ }
  return suggestions;
}

// ─── Main ─────────────────────────────────────────────────────────────────────

function main() {
  const entries = loadRecentMetaEntries(5);
  if (entries.length === 0) {
    console.log('[next-seed] No metacognition entries found');
    return;
  }

  const suggestions = [];
  const seen = new Set();

  function add(s) {
    const key = s.angle + '|' + s.desc;
    if (!seen.has(key)) {
      seen.add(key);
      suggestions.push(s);
    }
  }

  // Task #12: derive from gate failures across recent entries
  for (const s of deriveFromGateFailures(entries)) add(s);

  // Task #8: derive from seed_critiques three failure modes
  for (const s of deriveFromSeedCritiques(entries)) add(s);

  // Task #11: external innovation sources
  for (const s of deriveFromSessionInsights()) add(s);
  for (const s of deriveFromGitHubTrending()) add(s);
  for (const s of deriveFromProjectGaps()) add(s);
  for (const s of deriveFromSharedScripts()) add(s);
  for (const s of deriveFromSharedScriptsReal()) add(s);
  for (const s of deriveFromProjectBins()) add(s);
  for (const s of deriveFromCodeScan()) add(s);
  for (const s of deriveFromHookifyScan()) add(s);

  // Fallback: only if pool is completely empty
  if (suggestions.length === 0) {
    add({
      angle: 'ws-level',
      desc: 'run-seed --explain 增加step输出变量追踪',
      benefit: 'executor执行时显示每个step的输出变量传递，便于调试长chain',
      reason: '已知资源：run-seed.mjs已有--explain模式；缺失环节：无变量追踪输出；连接方式：--explain模式下输出每个step的outputSlots值'
    });
  }

  const mode = process.argv.includes('--auto');
  if (!mode) {
    console.log('=== Next Seeds (' + suggestions.length + ' derived from ' + entries.length + ' metacognition entries) ===');
    for (const s of suggestions) {
      console.log('  [' + s.angle + '] ' + s.desc);
      console.log('    benefit: ' + s.benefit);
    }
    if (suggestions.length === 0) console.log('  (no derivable seeds — batch was clean)');
    return;
  }

  const today = new Date().toISOString().slice(0, 10).replace(/-/g, '');
  const date = process.argv.includes('--date') ? process.argv[process.argv.indexOf('--date') + 1] : today;

  let written = 0;
  const existingContent = existsSync(IDEAS_FILE) ? readFileSync(IDEAS_FILE, 'utf-8') : '';
  const existingSeeds = new Set();
  for (const line of existingContent.split('\n')) {
    const m = line.match(/^\- \[[\d]+\] seed \[([^\]]+)\] \[score:[^\]]+\] \[f:\d+\] \[angle:([^\]]+)\] ([^|]+)/);
    if (m) existingSeeds.add(m[2] + '|' + m[3].trim());
  }

  const approachMap = {
    'approach可执行性验证报告生成器': '1. node shared/run-seed.mjs --warm-all',
    'feasibility评分校准器': '1. node shared/run-seed.mjs --warm-all',
    'reason准确性检查器': '1. node shared/run-seed.mjs --warm-all',
    'approach drift检测器': '1. node shared/run-seed.mjs --warm-all',
    'Gate13项目路径预扫描': '1. node shared/run-seed.mjs --warm-all',
    'OMC状态检查统一入口': '1. node shared/run-seed.mjs --warm-all',
    'brainstorm种子枯竭应对：外部来源扩展': '1. node shared/run-seed.mjs --warm-all',
    'OMC任务追踪集成': '1. node shared/run-seed.mjs --warm-all',
    'run-seed --explain 增加step输出变量追踪': '1. node shared/run-seed.mjs --explain --pool-status',
  };

  for (const s of suggestions) {
    const seedKey = s.angle + '|' + s.desc;
    if (existingSeeds.has(seedKey)) {
      console.warn('[next-seed] SKIP (already in pool): ' + s.desc);
      continue;
    }

    // Use mapped approach or generate one based on desc
    let approach = approachMap[s.desc];
    if (!approach) {
      // For dynamic seeds (shared/xxx.mjs or project/xxx), generate real approach
      const descLower = s.desc.toLowerCase();
      const isFeatureSeed = /增加--(\w+)/.test(s.desc);
      if (descLower.includes('shared/') || descLower.includes('.mjs')) {
        const scriptMatch = s.desc.match(/(shared\/[^\s]+(?:\.mjs)?)/);
        if (scriptMatch) {
          const script = scriptMatch[1].replace('.mjs', '') + '.mjs';
          const flagMatch = s.desc.match(/增加--(\w+)/);
          const flag = flagMatch ? '--' + flagMatch[1] : '--help';
          // P3 fix: feature seeds with "增加--flag" must use python patch for implementation
          if (isFeatureSeed && flagMatch) {
            const patchName = 'patch-' + script.replace('shared/', '');
            approach = '1. python shared/' + patchName + '.py && node ' + script + ' ' + flag;
          } else {
            approach = '1. node ' + script + ' ' + flag;
          }
        }
      }
      if (descLower.includes('/bin/') || descLower.includes('task-orchestrator') || descLower.includes('opencli')) {
        const projectMatch = s.desc.match(/(task-orchestrator|opencli|CLI-Anything)/);
        const scriptMatch = s.desc.match(/([\w-]+\.(?:mjs|js))(?:\s|$)/);
        if (projectMatch && scriptMatch) {
          const flagMatch = s.desc.match(/增加--(\w+)/);
          const flag = flagMatch ? '--' + flagMatch[1] : '--help';
          // P3 fix: feature seeds with "增加--flag" must use python patch for implementation
          if (isFeatureSeed && flagMatch) {
            const patchName = 'patch-' + scriptMatch[1].replace('.mjs', '');
            approach = '1. python shared/' + patchName + '.py && node 80-PROJECTS/' + projectMatch[1] + '/bin/' + scriptMatch[1] + ' ' + flag;
          } else {
            approach = '1. node 80-PROJECTS/' + projectMatch[1] + '/bin/' + scriptMatch[1] + ' ' + flag;
          }
        }
      }
    }
    // Fallback for truly generic seeds
    if (!approach) {
      approach = '1. node shared/run-seed.mjs --warm-all';
    }

    let validApproach = false;
    try {
      const reasonArg = (s.reason || '').replace(/"/g, '\\"');
      const validationCmd = 'node "' + join(__DIR, '..', 'shared', 'run-seed.mjs') + '" --validate-approach "' + approach.replace(/"/g, '\\"') + '" --reason "' + reasonArg + '"';
      execSync(validationCmd, { stdio: 'pipe', windowsHide: true });
      validApproach = true;
    } catch (e) {
      console.warn('[next-seed] SKIP (Gate13/4c fail): ' + s.desc + ' — approach not valid: ' + approach);
      continue;
    }

    const focusStr = s.focus ? ' [focus:' + s.focus + ']' : '';
    const line = '- [' + date + '] seed [brainstorm] [score:3x3=9] [f:3] [angle:' + s.angle + ']' + focusStr + ' ' + s.desc + ' | benefit: ' + s.benefit + ' | reason: ' + s.reason + ' | approach: ' + approach + '\n';
    appendFileSync(IDEAS_FILE, line, 'utf8');
    written++;
  }
  console.log('[next-seed] Wrote ' + written + '/' + suggestions.length + ' seeds to pool');
}

main();
