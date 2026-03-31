#!/usr/bin/env node
/**
 * Self-Evolving Workspace Optimizer
 *
 * Uses epsilon-greedy algorithm to explore and exploit optimization strategies.
 * Each iteration learns from history to improve future decisions.
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const WORKSPACE = path.join(__dirname, '..', '..');
const HISTORY_FILE = path.join(WORKSPACE, '.omc', 'loop-history.json');

const EPSILON_MIN_BASE = 0.1;  // 基础最低探索率 10%
const EPSILON_MAX = 0.5;   // 最高探索率 50%
const EPSILON_INIT = 0.3;   // 初始探索率 30%
const COOLDOWN = 5;         // 冷却期：最近 5 次执行过的操作不立即重选（原3，过短）

// 差异化冷却期
const COOLDOWN_PRODUCTIVE = 3;  // productive ops: clean_*, create_missing_readme, workspace_auto_commit, gen_dashboard_data
const COOLDOWN_DETECTION = 1;   // detection ops: check_*, count_*, brainstorm_projects, find_large_files

// 全局检测 op 列表（exploit 模式排除检测 ops）
const DETECTION_OPS = ['count_projects', 'count_sessions', 'check_memory_size',
  'check_project_readmes', 'brainstorm_projects', 'find_large_files'];
const isDetectionOp = (id) => DETECTION_OPS.includes(id);

function getCooldown(opId) {
  return DETECTION_OPS.includes(opId) ? COOLDOWN_DETECTION : COOLDOWN_PRODUCTIVE;
}

// 大文件白名单：这些文件是正常的，不计入大文件检测
const LARGE_FILES_WHITELIST = [
  '80-PROJECTS/idle-empire/butler',
  '80-PROJECTS/multi-agent-discuss/bin/agent.exe'
];

function getEpsilonMin(score) {
  return score > 90 ? 0.05 : EPSILON_MIN_BASE; // 健康度>90时降至5%
}

// 新操作（从未被选中过）给予更高的探索优先权
function isNewOp(history, opId) {
  return !history.records.some(r => r.opId === opId);
}

// 操作候选池
const OPERATIONS = [
  {
    id: 'gen_dashboard_data',
    name: '生成 dashboard 数据',
    weight: 1.0,
    action: async () => {
      const { execSync } = await import('child_process');
      try {
        execSync('node generate-dashboard-data.js', {
          cwd: __dirname,
          encoding: 'utf8',
          timeout: 30000
        });
        return { success: true };
      } catch (e) {
        return { success: false, error: e.message };
      }
    }
  },
  {
    id: 'workspace_auto_commit',
    name: '检查并自动提交 workspace git 变更',
    weight: 1.0,
    action: async () => {
      const { execSync } = await import('child_process');
      // 检查是否有变更（排除 loop-history.json 和 dashboard-data.json）
      try {
        const status = execSync('git status --porcelain', {
          cwd: WORKSPACE,
          encoding: 'utf8',
          timeout: 5000
        }).trim();

        if (!status) return { committed: 0, message: '无变更' };

        const lines = status.split('\n').filter(l => {
          const trimmed = l.trim();
          return trimmed && !trimmed.includes('loop-history.json') && !trimmed.includes('dashboard-data.json');
        });

        if (lines.length === 0) return { committed: 0, message: '无变更（仅 loop 文件）' };

        const changed = lines.length;
        const hasDeleted = lines.some(l => l.startsWith('D '));
        const hasNew = lines.some(l => l.startsWith('?? '));
        const hasModified = lines.some(l => l.startsWith(' M') || l.startsWith('M '));
        const hasAdded = lines.some(l => l.startsWith('A '));

        let msg = '';
        if (hasNew && hasAdded) msg = `feat: 新增 ${lines.filter(l => l.startsWith('?? ') || l.startsWith('A ')).length} 个文件`;
        else if (hasModified) msg = `chore: 更新 ${lines.filter(l => l.startsWith(' M') || l.startsWith('M ')).length} 个文件`;
        else if (hasDeleted) msg = `chore: 删除 ${lines.filter(l => l.startsWith('D ')).length} 个文件`;
        else msg = `chore: 同步 ${changed} 个文件`;

        execSync('git add -A', { cwd: WORKSPACE, encoding: 'utf8', timeout: 5000 });
        execSync(`git commit -m "${msg}"`, { cwd: WORKSPACE, encoding: 'utf8', timeout: 5000 });

        return { committed: changed, message: msg };
      } catch (e) {
        return { committed: 0, message: `提交失败: ${e.message}` };
      }
    }
  },
  {
    id: 'check_project_readmes',
    name: '检查项目 README 完整性',
    weight: 1.0,
    action: async () => {
      const projectsDir = path.join(WORKSPACE, '80-PROJECTS');
      if (!fs.existsSync(projectsDir)) return { total: 0, missing: 0 };

      const dirs = fs.readdirSync(projectsDir).filter(f => {
        const stat = fs.statSync(path.join(projectsDir, f));
        return stat.isDirectory() && !f.startsWith('10-') && !f.startsWith('.');
      });

      let missing = 0;
      for (const d of dirs.slice(0, 10)) {
        const readmePath = path.join(projectsDir, d, 'README.md');
        if (!fs.existsSync(readmePath)) missing++;
      }

      return { checked: Math.min(dirs.length, 10), missing };
    }
  },
  {
    id: 'check_memory_size',
    name: '检查记忆文件大小',
    weight: 1.0,
    action: async () => {
      const memoryPath = path.join(WORKSPACE, '.omc', 'memory', 'MEMORY.md');
      if (!fs.existsSync(memoryPath)) {
        const globalMem = path.join(process.env.HOME || '', '.claude', 'projects', 'D--OpenClaw-workspace', 'memory', 'MEMORY.md');
        if (fs.existsSync(globalMem)) {
          const content = fs.readFileSync(globalMem, 'utf8');
          const sizeKB = Math.round(Buffer.byteLength(content, 'utf8') / 1024);
          return { sizeKB, lines: content.split('\n').length, global: true };
        }
        return { sizeKB: 0 };
      }

      const content = fs.readFileSync(memoryPath, 'utf8');
      const sizeKB = Math.round(Buffer.byteLength(content, 'utf8') / 1024);
      return { sizeKB, lines: content.split('\n').length };
    }
  },
  {
    id: 'brainstorm_projects',
    name: '头脑风暴项目优化建议',
    weight: 1.0,
    action: async () => {
      const projectsDir = path.join(WORKSPACE, '80-PROJECTS');
      if (!fs.existsSync(projectsDir)) return { ideas: 0 };

      const dirs = fs.readdirSync(projectsDir).filter(f => {
        const stat = fs.statSync(path.join(projectsDir, f));
        return stat.isDirectory() && !f.startsWith('10-') && !f.startsWith('.');
      });

      if (dirs.length === 0) return { ideas: 0 };

      // 随机选一个项目
      const target = dirs[Math.floor(Math.random() * dirs.length)];
      const projectPath = path.join(projectsDir, target);

      // 检查项目类型并生成建议
      const suggestions = [];
      const readmePath = path.join(projectPath, 'README.md');
      const packagePath = path.join(projectPath, 'package.json');
      const srcPath = path.join(projectPath, 'src');

      if (!fs.existsSync(readmePath)) {
        suggestions.push('缺少 README.md - 建议添加项目说明文档');
      }
      if (fs.existsSync(packagePath)) {
        const pkg = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
        if (!pkg.scripts?.dev && !pkg.scripts?.start) {
          suggestions.push('缺少启动脚本 - 建议添加 dev 或 start 命令');
        }
        if (!pkg.keywords || pkg.keywords.length < 3) {
          suggestions.push('关键词不足 - 建议添加更多关键词提升可发现性');
        }
      }
      if (fs.existsSync(srcPath)) {
        const srcFiles = fs.readdirSync(srcPath).filter(f => f.endsWith('.ts') || f.endsWith('.js'));
        if (srcFiles.length > 10) {
          suggestions.push(`src 目录有 ${srcFiles.length} 个文件 - 考虑模块化拆分`);
        }
      }

      // 只在有建议时才写入文件，避免积累无意义的brainstorm文件
      if (suggestions.length === 0) {
        return { project: target, ideas: 0, message: '项目状态良好' };
      }

      const brainstormDir = path.join(WORKSPACE, '.omc', 'brainstorm');
      if (!fs.existsSync(brainstormDir)) fs.mkdirSync(brainstormDir, { recursive: true });

      const timestamp = new Date().toISOString().slice(0, 10);
      const outputPath = path.join(brainstormDir, `${target}-${timestamp}.md`);
      const content = `# ${target} 优化建议\n\n**生成时间**: ${new Date().toLocaleString()}\n\n## 项目信息\n- **路径**: ${projectPath}\n- **建议数量**: ${suggestions.length}\n\n## 优化建议\n${suggestions.map((s, i) => `${i + 1}. ${s}`).join('\n')}\n\n## 评分\n- 评分: ★★☆☆☆ (需改进)\n`;
      fs.writeFileSync(outputPath, content);

      return { project: target, ideas: suggestions.length, suggestions, output: outputPath };
    }
  },
  {
    id: 'create_missing_readme',
    name: '为缺失项目创建基础README',
    weight: 1.0,
    action: async () => {
      const projectsDir = path.join(WORKSPACE, '80-PROJECTS');
      if (!fs.existsSync(projectsDir)) return { created: 0 };

      // 找所有没有README的项目
      const dirs = fs.readdirSync(projectsDir).filter(f => {
        const stat = fs.statSync(path.join(projectsDir, f));
        return stat.isDirectory() && !f.startsWith('10-') && !f.startsWith('.');
      });

      const missingReadmes = [];
      for (const d of dirs) {
        const readmePath = path.join(projectsDir, d, 'README.md');
        if (!fs.existsSync(readmePath)) {
          missingReadmes.push(d);
        }
      }

      if (missingReadmes.length === 0) return { created: 0, message: '所有项目已有README' };

      // 随机选一个项目创建README
      const target = missingReadmes[Math.floor(Math.random() * missingReadmes.length)];
      const projectPath = path.join(projectsDir, target);
      const readmePath = path.join(projectPath, 'README.md');

      // 检查是否有package.json来获取项目信息
      const packagePath = path.join(projectPath, 'package.json');
      let description = '项目描述暂无';
      let version = '0.0.1';

      if (fs.existsSync(packagePath)) {
        try {
          const pkg = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
          description = pkg.description || description;
          version = pkg.version || version;
        } catch { /* ignore */ }
      }

      const readmeContent = `# ${target}

${description}

## 项目信息

- **版本**: ${version}
- **路径**: ${projectPath}

## 快速开始

\`\`\`bash
# 安装依赖
npm install

# 启动开发
npm run dev
\`\`\`

## 项目结构

\`\`\`
${target}/
├── src/          # 源代码
├── README.md     # 本文档
└── package.json  # 项目配置
\`\`\`
`;

      fs.writeFileSync(readmePath, readmeContent);
      return { created: 1, project: target, path: readmePath };
    }
  },
  {
    id: 'find_large_files',
    name: '查找大文件（仅报告）',
    weight: 1.0,
    action: async () => {
      const projectsDir = path.join(WORKSPACE, '80-PROJECTS');
      if (!fs.existsSync(projectsDir)) return { found: 0 };

      const limitMB = 5;
      const largeFiles = [];
      // 只扫描已知安全的缓存/临时目录
      const safePatterns = ['.cache', 'cache', 'temp', 'tmp', '.tmp', 'dist', 'build', 'output', '.log', 'logs'];

      function scanDir(dir, depth = 0) {
        if (depth > 3) return;
        try {
          const entries = fs.readdirSync(dir, { withFileTypes: true });
          for (const entry of entries.slice(0, 50)) {
            if (entry.name.startsWith('.')) continue; // 跳过隐藏目录
            const fullPath = path.join(dir, entry.name);
            if (entry.isDirectory()) {
              // 只深入扫描安全的子目录
              const isSafe = safePatterns.some(p => entry.name.includes(p));
              if (isSafe || depth < 2) scanDir(fullPath, depth + 1);
            } else if (entry.isFile()) {
              const size = fs.statSync(fullPath).size;
              const sizeMB = size / (1024 * 1024);
              if (sizeMB > limitMB) {
                const relPath = fullPath.replace(WORKSPACE, '').replace(/\\/g, '/');
                // 跳过白名单中的文件
                if (LARGE_FILES_WHITELIST.some(w => relPath.includes(w))) return;
                largeFiles.push({ path: relPath, sizeMB: sizeMB.toFixed(2) });
              }
            }
          }
        } catch { /* ignore */ }
      }

      scanDir(projectsDir);
      return { found: largeFiles.length, files: largeFiles.slice(0, 5) };
    }
  },
  {
    id: 'clean_brainstorm',
    name: '清理过期的 brainstorm 文件',
    weight: 1.0,
    action: async () => {
      const brainstormDir = path.join(WORKSPACE, '.omc', 'brainstorm');
      if (!fs.existsSync(brainstormDir)) return { total: 0, cleaned: 0 };

      const files = fs.readdirSync(brainstormDir).filter(f => f.endsWith('.md'));
      if (files.length <= 10) return { total: files.length, cleaned: 0, message: '文件不多，无需清理' };

      // 删除超过 30 天的文件
      const cutoff = Date.now() - (30 * 24 * 60 * 60 * 1000);
      let cleaned = 0;
      for (const f of files) {
        const stat = fs.statSync(path.join(brainstormDir, f));
        if (stat.mtimeMs < cutoff) {
          try {
            fs.unlinkSync(path.join(brainstormDir, f));
            cleaned++;
          } catch { /* ignore */ }
        }
      }
      return { total: files.length, cleaned };
    }
  }
];

// 健康度评分函数（动态评分）
function calculateHealthScore() {
  let score = 50; // 基础分 50

  try {
    // 项目数评分
    const projectsDir = path.join(WORKSPACE, '80-PROJECTS');
    if (fs.existsSync(projectsDir)) {
      const dirs = fs.readdirSync(projectsDir).filter(f => {
        const stat = fs.statSync(path.join(projectsDir, f));
        return stat.isDirectory() && !f.startsWith('10-') && !f.startsWith('.');
      });
      score += Math.min(dirs.length, 30); // 最多 +30

      // 项目 README 完整性
      const readmeCheck = dirs.filter(d => fs.existsSync(path.join(projectsDir, d, 'README.md')));
      const readmeRatio = readmeCheck.length / dirs.length;
      score += Math.round(readmeRatio * 10); // 0-10 分
    }

    // 记忆健康度
    const memoryPath = path.join(WORKSPACE, '.omc', 'memory', 'MEMORY.md');
    if (fs.existsSync(memoryPath)) {
      const content = fs.readFileSync(memoryPath, 'utf8');
      const sizeKB = Buffer.byteLength(content, 'utf8') / 1024;
      if (sizeKB < 150) score += 10;
      else score -= 10;
    }

    // OMC state 清洁度（sessions 和 checkpoints）
    const sessionsDir = path.join(WORKSPACE, '.omc', 'sessions');
    const checkpointsDir = path.join(WORKSPACE, '.omc', 'state', 'checkpoints');
    let totalFiles = 0;
    if (fs.existsSync(sessionsDir)) {
      totalFiles += fs.readdirSync(sessionsDir).filter(f => f.endsWith('.json')).length;
    }
    if (fs.existsSync(checkpointsDir)) {
      totalFiles += fs.readdirSync(checkpointsDir).filter(f => f.endsWith('.json')).length;
    }
    // 滑动评分
    if (totalFiles < 5) score += 10;
    else if (totalFiles < 20) score += 8;
    else if (totalFiles < 40) score += 6;
    else if (totalFiles < 60) score += 4;
    else if (totalFiles < 100) score += 2;

    // Git 状态：未提交文件越多越不健康（排除 loop-history.json）
    try {
      const out = execSync('git status --porcelain', {
        cwd: WORKSPACE,
        encoding: 'utf8',
        timeout: 5000
      }).trim();
      const changed = out ? out.split('\n').filter(l => {
        const trimmed = l.trim();
        // 排除 loop-history.json 和 dashboard-data.json（loop 自己产生，不算工作区问题）
        return trimmed && !trimmed.includes('loop-history.json') && !trimmed.includes('dashboard-data.json');
      }).length : 0;
      if (changed === 0) score += 10;
      else if (changed <= 3) score += 5;
      else if (changed <= 10) score += 2;
      else score -= Math.min(changed - 10, 10); // 最多扣 10 分
    } catch { /* ignore */ }

    // brainstorm 目录清理度（防止无限积累）
    const brainstormDir = path.join(WORKSPACE, '.omc', 'brainstorm');
    if (fs.existsSync(brainstormDir)) {
      const brainstormFiles = fs.readdirSync(brainstormDir).filter(f => f.endsWith('.md'));
      // 超过 20 个文件开始扣分，每多 10 个扣 1 分
      if (brainstormFiles.length > 20) {
        score -= Math.floor((brainstormFiles.length - 20) / 10);
      }
    }

  } catch (e) {
    console.error('[Health] Score calculation error:', e.message);
  }

  return Math.max(0, score);
}

// 加载历史
function loadHistory() {
  if (!fs.existsSync(HISTORY_FILE)) {
    return { epsilon: EPSILON_INIT, streak: { success: 0, fail: 0 }, records: [] };
  }
  try {
    return JSON.parse(fs.readFileSync(HISTORY_FILE, 'utf8'));
  } catch {
    return { epsilon: EPSILON_INIT, streak: { success: 0, fail: 0 }, records: [] };
  }
}

// 保存历史
function saveHistory(history) {
  const dir = path.dirname(HISTORY_FILE);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(HISTORY_FILE, JSON.stringify(history, null, 2));
}

// 选择操作 (epsilon-greedy)
function selectOperation(history) {
  const { epsilon } = history;

  // 冷却期：最近 N 次执行过的操作不立即重选
  // 检查当前是否还有改善空间
  const sessionsDir = path.join(WORKSPACE, '.omc', 'sessions');
  const checkpointsDir = path.join(WORKSPACE, '.omc', 'state', 'checkpoints');
  let totalFiles = 0;
  if (fs.existsSync(sessionsDir)) totalFiles += fs.readdirSync(sessionsDir).filter(f => f.endsWith('.json')).length;
  if (fs.existsSync(checkpointsDir)) totalFiles += fs.readdirSync(checkpointsDir).filter(f => f.endsWith('.json')).length;

  const canImprove = (op) => {
    if (op.id === 'clean_brainstorm') {
      const bmDir = path.join(WORKSPACE, '.omc', 'brainstorm');
      if (!fs.existsSync(bmDir)) return false;
      const bmFiles = fs.readdirSync(bmDir).filter(f => f.endsWith('.md')).length;
      return bmFiles > 10; // 只在文件超过10个时有清理价值
    }
    if (op.id === 'brainstorm_projects') {
      // 只在超过14天没有头脑风暴时才值得做（避免随机选中却无事可做）
      const bmDir = path.join(WORKSPACE, '.omc', 'brainstorm');
      if (!fs.existsSync(bmDir)) return true;
      const files = fs.readdirSync(bmDir).filter(f => f.endsWith('.md'));
      if (files.length === 0) return true;
      const latest = files.sort().pop();
      const age = Date.now() - fs.statSync(path.join(bmDir, latest)).mtimeMs;
      return age > 14 * 24 * 60 * 60 * 1000;
    }
    // 检测类操作：必须真的有东西可检测才可选
    if (['workspace_auto_commit'].includes(op.id)) {
      try {
        const out = execSync('git status --porcelain', { cwd: WORKSPACE, encoding: 'utf8', timeout: 5000 }).trim();
        const changed = out ? out.split('\n').filter(l => l.trim()).length : 0;
        return changed > 0;
      } catch { return false; }
    }
    if (['count_projects', 'count_sessions', 'check_memory_size'].includes(op.id)) return false;
    if (['check_project_readmes', 'find_large_files'].includes(op.id)) return true;
    return true;
  };

  if (Math.random() < epsilon) {
    const candidates = OPERATIONS.filter(op => {
      const cd = getCooldown(op.id);
      const recent = history.records.slice(-cd).map(r => r.opId);
      return !recent.includes(op.id);
    });
    if (candidates.length === 0) candidates.push(OPERATIONS[Math.floor(Math.random() * OPERATIONS.length)]);
    // 探索模式：优先选从未执行过的新操作，确保所有操作都有被尝试的机会
    const newCandidates = candidates.filter(op => isNewOp(history, op.id));
    const pickFrom = newCandidates.length > 0 ? newCandidates : candidates;
    const op = pickFrom[Math.floor(Math.random() * pickFrom.length)];
    if (newCandidates.length > 0) {
      console.log(`[Select] 探索模式: ${op.name} [新操作优先]`);
    } else {
      console.log(`[Select] 探索模式: ${op.name}`);
    }
    return { op, mode: 'explore' };
  }

  // 利用模式：基于历史成功率
  const successRates = {};
  for (const record of history.records) {
    if (!successRates[record.opId]) successRates[record.opId] = { success: 0, total: 0 };
    successRates[record.opId].total++;
    if (record.improved) successRates[record.opId].success++;
  }

  let bestOp = null;
  let bestRate = -1;

  for (const op of OPERATIONS) {
    if (isDetectionOp(op.id)) continue; // 检测 ops 不参与 exploit 选择
    const cd = getCooldown(op.id);
    const recent = history.records.slice(-cd).map(r => r.opId);
    if (recent.includes(op.id)) continue;
    const rate = successRates[op.id];
    // 新操作给予 +0.1 探索加成，确保从未执行过的操作能被优先尝试
    const noveltyBonus = isNewOp(history, op.id) ? 0.1 : 0;
    if (rate && rate.total >= 1) {
      const r = rate.success / rate.total + noveltyBonus;
      if (r > bestRate) { bestRate = r; bestOp = op; }
    } else if (isNewOp(history, op.id)) {
      // 新操作（无历史）：默认 0.1 基础分 + 新操作加成
      const r = 0.1 + noveltyBonus;
      if (r > bestRate) { bestRate = r; bestOp = op; }
    }
  }

  if (!bestOp || bestRate <= 0) {
    // 无历史/全失败：优先选当前有实际工作可做的操作
    const usefulCandidates = OPERATIONS.filter(op => {
      const cd = getCooldown(op.id);
      const recent = history.records.slice(-cd).map(r => r.opId);
      return !recent.includes(op.id) && canImprove(op);
    });
    const candidates = usefulCandidates.length > 0 ? usefulCandidates : OPERATIONS.filter(op => {
      const cd = getCooldown(op.id);
      const recent = history.records.slice(-cd).map(r => r.opId);
      return !recent.includes(op.id);
    });
    if (candidates.length === 0) candidates.push(OPERATIONS[Math.floor(Math.random() * OPERATIONS.length)]);
    const op = candidates[Math.floor(Math.random() * candidates.length)];
    console.log(`[Select] 无历史/全失败，强制探索: ${op.name}`);
    return { op, mode: 'explore' };
  }

  if (!canImprove(bestOp)) {
    const improvable = OPERATIONS.filter(op => {
      if (isDetectionOp(op.id)) return false;
      const cd = getCooldown(op.id);
      const recent = history.records.slice(-cd).map(r => r.opId);
      return !recent.includes(op.id) && successRates[op.id] && (successRates[op.id].success / successRates[op.id].total) > 0 && canImprove(op);
    });
    if (improvable.length > 0) {
      improvable.sort((a, b) => (successRates[b.id].success / successRates[b.id].total) - (successRates[a.id].success / successRates[a.id].total));
      const nextBest = improvable[0];
      console.log(`[Select] 利用模式: ${nextBest.name} (成功率: ${(successRates[nextBest.id].success / successRates[nextBest.id].total * 100).toFixed(0)}%) [最佳操作无可改善空间，降级]`);
      return { op: nextBest, mode: 'exploit' };
    }
    const candidates = OPERATIONS.filter(op => {
      const cd = getCooldown(op.id);
      const recent = history.records.slice(-cd).map(r => r.opId);
      return !recent.includes(op.id);
    });
    if (candidates.length === 0) candidates.push(OPERATIONS[Math.floor(Math.random() * OPERATIONS.length)]);
    const op = candidates[Math.floor(Math.random() * candidates.length)];
    console.log(`[Select] 全部操作无可改善，强制探索: ${op.name}`);
    return { op, mode: 'explore' };
  }

  console.log(`[Select] 利用模式: ${bestOp.name} (成功率: ${(bestRate * 100).toFixed(0)}%)`);
  return { op: bestOp, mode: 'exploit' };
}

// 执行主循环
async function runIteration() {
  const history = loadHistory();
  const beforeScore = calculateHealthScore();

  console.log('\n' + '='.repeat(50));
  console.log(`[Loop] 迭代开始 | 健康度: ${beforeScore} | ε: ${(history.epsilon * 100).toFixed(0)}%`);

  const { op, mode } = selectOperation(history);

  let result;
  try {
    result = await op.action();
    console.log(`[Result]`, result);
  } catch (e) {
    console.error(`[Error] 操作失败: ${e.message}`);
    result = { error: e.message };
  }

  const afterScore = calculateHealthScore();
  const delta = afterScore - beforeScore;

  let improved = delta > 0;
  let noOp = false; // 无事可做，不算失败也不算成功

  if (!improved && result) {
    if (isDetectionOp(op.id)) {
      // 检测类：发现问题（missing/changed/ideas/found > 0）才算成功
      // outdated 不算：松散版本 ^/~ 通常是故意的，检测到不代表有问题
      // checked=0 也不算：说明没有可检测的项目
      const found = (result.missing > 0) || (result.changed > 0) || (result.ideas > 0) || (result.found > 0) || (result.committed > 0);
      if (!found) noOp = true;
      else improved = true;
    } else {
      // 生产类：明确无事可做（created:0 且有message）不算失败
      // 或者 cleaned=0 且 total > 0 但没满足条件（不是真正失败）
      if ((result.created === 0 && result.message) ||
          (result.cleaned === 0 && result.total > 0)) {
        noOp = true;
      } else {
        improved = (result.created > 0) || (result.cleaned > 0) || (result.deleted > 0) || (result.found > 0) || (result.success === true) || (result.committed > 0);
      }
    }
  }

  const record = { opId: op.id, opName: op.name, mode, beforeScore, afterScore, delta, improved, timestamp: Date.now() };
  history.records.push(record);
  if (history.records.length > 100) history.records = history.records.slice(-100);

  if (improved) {
    history.streak.success++;
    history.streak.fail = 0;
    if (history.streak.success >= 3) {
      history.epsilon = Math.max(getEpsilonMin(afterScore), history.epsilon - 0.05);
      history.streak.success = 0;
      console.log(`[Epsilon] 连续成功，ε 降低到 ${(history.epsilon * 100).toFixed(0)}%`);
    }
  } else if (!noOp) {
    // 仅真正的失败计入失败 streak，无事可做不计入
    history.streak.fail++;
    history.streak.success = 0;
    if (history.streak.fail >= 3) {
      history.epsilon = Math.min(EPSILON_MAX, history.epsilon + 0.1);
      history.streak.fail = 0;
      console.log(`[Epsilon] 连续失败，ε 升高到 ${(history.epsilon * 100).toFixed(0)}%`);
    }
  } else {
    // 无事可做：双方 streak 都清零，重置学习状态
    history.streak.success = 0;
    history.streak.fail = 0;
  }

  saveHistory(history);
  console.log(`[Loop] 健康度: ${beforeScore} → ${afterScore} (${delta > 0 ? '+' : ''}${delta}) | ${noOp ? '无操作' : improved ? '✓' : '❌'}`);
  console.log('='.repeat(50));
  return record;
}

// 主入口
async function main() {
  const args = process.argv.slice(2);

  if (args.includes('--status')) {
    const history = loadHistory();
    const score = calculateHealthScore();

    console.log('\n╔══════════════════════════════════════╗');
    console.log('║     自我进化 Loop - 状态报告       ║');
    console.log('╠══════════════════════════════════════╣');
    console.log(`║  健康度: ${score}/100`);
    console.log(`║  探索率 (ε): ${(history.epsilon * 100).toFixed(0)}%`);
    console.log(`║  历史记录: ${history.records.length} 条`);
    console.log(`║  连续成功: ${history.streak.success} 次`);
    console.log(`║  连续失败: ${history.streak.fail} 次`);
    console.log('╠══════════════════════════════════════╣');
    console.log('║     TOP 5 最有效操作               ║');

    const successRates = {};
    for (const record of history.records) {
      if (!successRates[record.opId]) successRates[record.opId] = { name: record.opName, success: 0, total: 0 };
      successRates[record.opId].total++;
      if (record.improved) successRates[record.opId].success++;
    }

    const sorted = Object.values(successRates).filter(r => r.total >= 1)
      .sort((a, b) => (b.success / b.total) - (a.success / a.total)).slice(0, 5);
    for (const r of sorted) {
      const rate = ((r.success / r.total) * 100).toFixed(0);
      console.log(`║  • ${r.name}: ${rate}% (${r.success}/${r.total})`);
    }
    console.log('╚══════════════════════════════════════╝');
    return;
  }

  await runIteration();
}

main().catch(console.error);
