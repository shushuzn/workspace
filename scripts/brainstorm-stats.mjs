#!/usr/bin/env node
/**
 * scripts/brainstorm-stats.mjs
 * Visualizes brainstorm-metacognition.jsonl trends + outputs actionable recommendations.
 * Usage:
 *   node scripts/brainstorm-stats.mjs           # view trends
 *   node scripts/brainstorm-stats.mjs --recommend  # output actionable recommendations
 */
import { readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const META_PATH = join(__DIR, '..', '.omc', 'innovation', 'brainstorm-metacognition.jsonl');
// Fixed path: was incorrectly reading knowledge/wikipedia/.omc/... which was the old location

const recommendMode = process.argv.includes('--recommend');

const content = readFileSync(META_PATH, 'utf-8');
const lines = content.trim().split('\n').filter(Boolean);

const records = lines.map(l => {
  try { return JSON.parse(l); } catch { return null; }
}).filter(Boolean);

if (records.length === 0) {
  console.log('No metacognition data yet.');
  process.exit(0);
}

// ── Trend Table ────────────────────────────────────────────────────────────────
console.log('\n=== Brainstorm Metacognition Stats ===\n');
console.log('Batch Trend:');
console.log('Date       | Seeds | AvgScore | SelfAss | TopIssues');
console.log('-'.repeat(65));
records.forEach(r => {
  const issues = Object.entries(r.gate_failures || {}).slice(0, 2).map(([k, v]) => `${k}:${v}`).join(',') || '-';
  console.log(`${r.date} | ${String(r.batch_seed_count).padStart(5)} | ${String(r.batch_avg_score).padStart(8)} | ${String(r.self_assessment).padStart(8)} | ${issues}`);
});

// ── Gate Failure Frequency ───────────────────────────────────────────────────
const gateFreq = {};
records.forEach(r => {
  Object.entries(r.gate_failures || {}).forEach(([gate, count]) => {
    gateFreq[gate] = (gateFreq[gate] || 0) + count;
  });
});
const gateSorted = Object.entries(gateFreq).sort((a, b) => b[1] - a[1]);
console.log('\nGate Failure Frequency:');
gateSorted.forEach(([gate, count]) => {
  console.log(`  ${gate}: ${count}`);
});

// ── Self-Assessment Rate ──────────────────────────────────────────────────────
const passCount = records.filter(r => r.self_assessment === 'pass').length;
console.log(`\nSelf-Assessment Pass Rate: ${passCount}/${records.length} (${Math.round(passCount / records.length * 100)}%)`);

// ── --recommend: Actionable Recommendations ────────────────────────────────────
if (recommendMode) {
  console.log('\n=== Brainstorm Recommendations ===\n');

  const recent5 = records.slice(-5);
  const recent3 = records.slice(-3);

  // 1. Gate failure patterns
  const failingGates = new Set();
  recent5.forEach(r => {
    Object.keys(r.gate_failures || {}).forEach(g => failingGates.add(g));
  });

  // 2. Low-score angle detection
  const angleScoreSum = {};
  const angleCount = {};
  records.forEach(r => {
    (r.low_score_angles || []).forEach(a => {
      const score = parseFloat(r.batch_avg_score) || 0;
      angleScoreSum[a] = (angleScoreSum[a] || 0) + score;
      angleCount[a] = (angleCount[a] || 0) + 1;
    });
  });
  const lowAngles = Object.entries(angleScoreSum)
    .filter(([, sum]) => sum / angleCount[angleScoreSum] < 8)
    .map(([a]) => a);

  // 3. High-performing project detection
  const projectScoreSum = {};
  const projectCount = {};
  records.forEach(r => {
    (r.high_score_projects || []).forEach(p => {
      const score = parseFloat(r.batch_avg_score) || 0;
      if (score >= 12) {
        projectScoreSum[p] = (projectScoreSum[p] || 0) + score;
        projectCount[p] = (projectCount[p] || 0) + 1;
      }
    });
  });
  const hotProjects = Object.entries(projectScoreSum)
    .filter(([, sum]) => sum / projectCount[projectScoreSum] >= 14)
    .map(([p]) => p);

  // 4. Recommendations
  const recommendations = [];

  // Gate-based recommendations
  if (failingGates.has('Gate4b')) {
    recommendations.push({ gate: 'Gate4b', rec: 'approach 第1步仍含非shell-executable前缀 → 强化 Gate4b 白名单检查，在生成时即过滤' });
  }
  if (failingGates.has('Gate4c')) {
    recommendations.push({ gate: 'Gate4c', rec: 'inline node -e approach 仍通过验证 → 检查 --validate-approach 是否正确拦截 execSync 不兼容的命令' });
  }
  if (failingGates.has('Gate13')) {
    recommendations.push({ gate: 'Gate13', rec: '文件路径验证失败 → 检查被引用文件是否真实存在' });
  }

  // Angle adjustment recommendations
  if (lowAngles.length > 0) {
    lowAngles.forEach(a => {
      recommendations.push({ gate: 'angle', rec: `angle "${a}" 连续低分 → 下批次该 angle Benefit 评分自动降 1 档` });
    });
  }

  // Project priority recommendations
  if (hotProjects.length > 0) {
    recommendations.push({ gate: 'project', rec: `项目 ${hotProjects.join(', ')} 连续高分 → 下批次候选池优先增加这些项目的 seeds` });
  }

  // Self-assessment fail pattern
  const failCount = recent3.filter(r => r.self_assessment === 'fail').length;
  if (failCount >= 2) {
    recommendations.push({ gate: 'self_assess', rec: '连续批次 self_assessment=fail → 必须分析根因（见上条 gate failures），不可跳过' });
  }

  if (recommendations.length === 0) {
    console.log('No specific recommendations — system appears healthy.');
    console.log('Continue monitoring gate failures for emerging patterns.');
  } else {
    recommendations.forEach(({ gate, rec }, i) => {
      console.log(`${i + 1}. [${gate}] ${rec}`);
    });

    // Output seed-ready recommendations
    console.log('\n--- Executable Seed Candidates ---');
    const seedCandidates = recommendations.filter(r => r.gate === 'angle' || r.gate === 'project');
    if (seedCandidates.length > 0) {
      seedCandidates.forEach(({ gate, rec }, i) => {
        const today = new Date().toISOString().slice(0, 10).replace(/-/g, '');
        const angle = gate === 'angle' ? rec.match(/angle "([^"]+)"/)?.[1] || 'unknown' : null;
        const project = gate === 'project' ? (rec.match(/项目 ([^,，；]+)/) || ['',null])[1] : null;
        if (angle) {
          console.log(`- [${today}] seed [brainstorm] [score:2x3=6] [f:3] [angle:${angle}] 自动Benefit降档 | benefit: 防止低质量种子进入pool | reason: 已知资源=metacognition数据；缺失环节=无自动降档机制；连接方式=analyze-seed-quality.mjs按angle统计分数 | approach: 1. Edit scripts/analyze-seed-quality.mjs添加angle→avgScore映射；2. run-seed.mjs读取该映射自动降档 | killed:${today} 已合并到Gate规则`);
        }
        if (project) {
          console.log(`- [${today}] seed [brainstorm] [score:3x4=12] [f:4] [focus:${project}] 增加${project}候选池 | benefit: ${project}连续高分，增加曝光提升总batch分数 | reason: 已知资源=metacognition high_score_projects数据；缺失环节=候选池无项目优先级；连接方式=brainstorm候选池构建时加权 | killed:${today} 已有cross-batch learning规则`);
        }
      });
    } else {
      console.log('(No executable seed candidates — recommendations are rule-level, not code-level)');
    }
  }

  console.log('\nNote: Recommendation seeds above are marked killed — they reflect rules already captured in SKILL.md Gate 2 self-adjustment. Real seeds should be generated organically.');
}
