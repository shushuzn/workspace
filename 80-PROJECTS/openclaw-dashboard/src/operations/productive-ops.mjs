/**
 * Productive Operations
 * Operations that make changes to the workspace
 */

import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { execSync } from 'child_process';
import { ProductiveOperation } from './base.mjs';

export class GenDashboardData extends ProductiveOperation {
  constructor(workspace) {
    super('gen_dashboard_data', '生成 dashboard 数据');
    this.workspace = workspace;
  }

  async execute() {
    const dataFile = path.join(this.workspace, 'dashboard-data.json');
    try {
      const before = fs.existsSync(dataFile)
        ? crypto.createHash('sha1').update(fs.readFileSync(dataFile)).digest('hex')
        : '';

      execSync('node generate-dashboard-data.js', {
        cwd: process.cwd(),
        encoding: 'utf8',
        timeout: 30000
      });

      const after = fs.existsSync(dataFile)
        ? crypto.createHash('sha1').update(fs.readFileSync(dataFile)).digest('hex')
        : '';

      return { success: before !== after };
    } catch (e) {
      return { success: false, error: e.message };
    }
  }
}

export class WorkspaceAutoCommit extends ProductiveOperation {
  constructor(workspace) {
    super('workspace_auto_commit', '检查并自动提交 workspace git 变更');
    this.workspace = workspace;
  }

  canImprove() {
    try {
      const out = execSync('git status --porcelain', {
        cwd: this.workspace,
        encoding: 'utf8',
        timeout: 5000
      }).trim();
      return out.length > 0;
    } catch { return false; }
  }

  async execute() {
    try {
      const status = execSync('git status --porcelain', {
        cwd: this.workspace,
        encoding: 'utf8',
        timeout: 5000
      }).trim();

      if (!status) return { committed: 0, message: '无变更' };

      const lines = status.split('\n').map(l => l.trim()).filter(Boolean);

      const meaningful = lines.filter(l => {
        const file = l.replace(/^[ A-Z?]{2,3}\s*/, '');
        return !file.includes('loop-history.json') && !file.includes('dashboard-data.json');
      });

      if (meaningful.length === 0) {
        return { committed: 0, message: '无变更（仅 loop 文件）' };
      }

      const changed = meaningful.length;
      const hasDeleted = meaningful.some(l => l.startsWith('D '));
      const hasNew = meaningful.some(l => l.startsWith('?? '));
      const hasModified = meaningful.some(l => l.startsWith(' M') || l.startsWith('M '));
      const hasAdded = meaningful.some(l => l.startsWith('A '));

      let msg = '';
      if (hasNew && hasAdded) {
        msg = `feat: 新增 ${meaningful.filter(l => l.startsWith('?? ') || l.startsWith('A ')).length} 个文件`;
      } else if (hasModified) {
        msg = `chore: 更新 ${meaningful.filter(l => l.startsWith(' M') || l.startsWith('M ')).length} 个文件`;
      } else if (hasDeleted) {
        msg = `chore: 删除 ${meaningful.filter(l => l.startsWith('D ')).length} 个文件`;
      } else {
        msg = `chore: 同步 ${changed} 个文件`;
      }

      execSync('git add -A', { cwd: this.workspace, encoding: 'utf8', timeout: 5000 });
      execSync(`git commit -m "${msg}"`, { cwd: this.workspace, encoding: 'utf8', timeout: 5000 });

      return { committed: changed, message: msg };
    } catch (e) {
      return { committed: 0, message: `提交失败: ${e.message}` };
    }
  }
}

export class CreateMissingReadme extends ProductiveOperation {
  constructor(workspace) {
    super('create_missing_readme', '为缺失项目创建基础README');
    this.workspace = workspace;
  }

  canImprove() {
    const projectsDir = this.workspace;
    if (!fs.existsSync(projectsDir)) return false;

    const dirs = fs.readdirSync(projectsDir).filter(f => {
      try {
        const stat = fs.statSync(path.join(projectsDir, f));
        return stat.isDirectory() && !f.startsWith('10-') && !f.startsWith('.');
      } catch { return false; }
    });

    return dirs.some(d => !fs.existsSync(path.join(projectsDir, d, 'README.md')));
  }

  async execute() {
    const projectsDir = this.workspace;
    if (!fs.existsSync(projectsDir)) return { created: 0 };

    const dirs = fs.readdirSync(projectsDir).filter(f => {
      try {
        const stat = fs.statSync(path.join(projectsDir, f));
        return stat.isDirectory() && !f.startsWith('10-') && !f.startsWith('.');
      } catch { return false; }
    });

    const missingReadmes = dirs.filter(d =>
      !fs.existsSync(path.join(projectsDir, d, 'README.md'))
    );

    if (missingReadmes.length === 0) {
      return { created: 0, message: '所有项目已有README' };
    }

    const target = missingReadmes[Math.floor(Math.random() * missingReadmes.length)];
    const projectPath = path.join(projectsDir, target);
    const readmePath = path.join(projectPath, 'README.md');

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
npm install
npm run dev
\`\`\`
`;

    fs.writeFileSync(readmePath, readmeContent);
    return { created: 1, project: target, path: readmePath };
  }
}

export class FindWorkspaceIssues extends ProductiveOperation {
  constructor(workspace) {
    super('find_workspace_issues', '扫描并记录工作区问题');
    this.workspace = workspace;
  }

  async execute() {
    const issues = [];
    const omcDir = path.join(this.workspace, '..', '.omc');

    // Check for temp files
    if (fs.existsSync(omcDir)) {
      const entries = fs.readdirSync(omcDir, { withFileTypes: true });
      for (const entry of entries) {
        const fullPath = path.join(omcDir, entry.name);
        if (['sessions', 'brainstorm', 'state', 'plans', 'research', 'logs'].includes(entry.name)) continue;
        if (entry.name.endsWith('~') || entry.name.endsWith('.tmp') || entry.name.endsWith('.bak')) {
          issues.push({ type: 'temp_file', path: fullPath, size: entry.size });
        }
        if (entry.isFile() && !entry.name.endsWith('.json') && !entry.name.endsWith('.md')) {
          issues.push({ type: 'unknown_file', path: fullPath, size: entry.size });
        }
      }
    }

    // Check stale sessions
    const sessionsDir = path.join(omcDir, 'sessions');
    if (fs.existsSync(sessionsDir)) {
      const cutoff = Date.now() - 30 * 24 * 60 * 60 * 1000;
      const files = fs.readdirSync(sessionsDir).filter(f => f.endsWith('.json'));
      for (const f of files) {
        const fullPath = path.join(sessionsDir, f);
        const mtime = fs.statSync(fullPath).mtimeMs;
        if (mtime < cutoff) {
          const age = Math.floor((Date.now() - mtime) / 86400000);
          issues.push({ type: 'stale_session', path: fullPath, age_days: age });
        }
      }
    }

    // Check orphan checkpoints
    const checkpointsDir = path.join(omcDir, 'state', 'checkpoints');
    if (fs.existsSync(checkpointsDir)) {
      const sessionFiles = fs.existsSync(sessionsDir)
        ? fs.readdirSync(sessionsDir).map(f => f.replace('.json', ''))
        : [];
      const cpFiles = fs.readdirSync(checkpointsDir).filter(f => f.endsWith('.json'));
      for (const f of cpFiles) {
        const base = f.replace('.json', '');
        if (!sessionFiles.includes(base)) {
          issues.push({ type: 'orphan_checkpoint', path: path.join(checkpointsDir, f) });
        }
      }
    }

    if (issues.length === 0) return { success: true, found: 0, issues: [] };

    // Write to dashboard data
    const dataFile = path.join(this.workspace, 'dashboard-data.json');
    let data = {};
    if (fs.existsSync(dataFile)) {
      try { data = JSON.parse(fs.readFileSync(dataFile, 'utf8')); } catch { /* ignore */ }
    }
    if (!data.issues) data.issues = [];
    for (const issue of issues) {
      if (!data.issues.some(i => i.path === issue.path)) {
        data.issues.push({ ...issue, found_at: new Date().toISOString(), resolved: false });
      }
    }
    fs.writeFileSync(dataFile, JSON.stringify(data, null, 2));

    return { success: true, found: issues.length, issues };
  }
}

export class CleanRecordedIssues extends ProductiveOperation {
  constructor(workspace) {
    super('clean_recorded_issues', '修复已记录的工作区问题');
    this.workspace = workspace;
    // Note: only cleans synthetic internal files (orphan checkpoints, stale sessions)
    // NOT user data - but still deletes files, so mark as destructive per Constitution
    this.destructive = true;
  }

  async execute() {
    const dataFile = path.join(this.workspace, 'dashboard-data.json');
    if (!fs.existsSync(dataFile)) return { cleaned: 0, message: '无问题报告' };

    let data;
    try { data = JSON.parse(fs.readFileSync(dataFile, 'utf8')); }
    catch { return { cleaned: 0, message: '无法读取数据' }; }

    const issues = data.issues || [];
    const unresolved = issues.filter(i => !i.resolved);
    if (unresolved.length === 0) return { cleaned: 0, message: '无未解决问题' };

    let cleaned = 0;
    for (const issue of unresolved) {
      if (!fs.existsSync(issue.path)) {
        issue.resolved = true;
        cleaned++;
        continue;
      }
      try {
        if (issue.type === 'orphan_checkpoint' || issue.type === 'stale_session') {
          fs.unlinkSync(issue.path);
          issue.resolved = true;
          cleaned++;
        }
      } catch { /* ignore delete failures */ }
    }

    if (cleaned > 0) {
      fs.writeFileSync(dataFile, JSON.stringify(data, null, 2));
    }
    return { cleaned };
  }
}

export class SyncProjectMarkers extends ProductiveOperation {
  constructor(workspace) {
    super('sync_project_markers', '同步项目活跃时间戳到记忆');
    this.workspace = workspace;
  }

  async execute() {
    const memoryFile = path.join(this.workspace, 'MEMORY.md');
    if (!fs.existsSync(memoryFile)) return { synced: 0 };

    const content = fs.readFileSync(memoryFile, 'utf8');
    const projectsDir = this.workspace;
    if (!fs.existsSync(projectsDir)) return { synced: 0 };

    const dirMatch = content.match(/\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|/g);
    if (!dirMatch) return { synced: 0 };

    let synced = 0;
    let newContent = content;

    for (const row of dirMatch) {
      const cols = row.split('|').map(c => c.trim()).filter(Boolean);
      if (cols.length < 3) continue;
      const name = cols[1];
      const rest = cols.slice(2).join('|');
      if (rest.includes('Last Active') || rest.includes('last-active')) continue;

      const projectPath = path.join(projectsDir, name);
      if (!fs.existsSync(projectPath)) continue;

      try {
        const log = execSync(`git log --format="%ai" --max-count=1`, {
          cwd: projectPath,
          encoding: 'utf8',
          timeout: 5000
        }).trim();
        if (!log) continue;

        const date = new Date(log).toISOString().split('T')[0];
        const lineIndex = newContent.split('\n').findIndex(l => l.includes(`| ${name} |`));
        if (lineIndex !== -1) {
          const line = newContent.split('\n')[lineIndex];
          const lastPipe = line.lastIndexOf('|');
          const before = line.slice(0, lastPipe);
          const after = line.slice(lastPipe);
          const lines = newContent.split('\n');
          lines[lineIndex] = before + ` ${date}` + after;
          newContent = lines.join('\n');
          synced++;
        }
      } catch { /* not a git repo */ }
    }

    if (synced > 0) {
      fs.writeFileSync(memoryFile, newContent);
    }
    return { synced };
  }
}

export class PickNextProject extends ProductiveOperation {
  /**
   * 权重衰减随机抽选下一个目标项目
   * 公式: weight = (days_since_last_active + 1)^γ
   * days=0（今天刚更新）权重为 1^γ=1，最不优先；久未更新的项目权重更高
   */
  constructor(workspace, gamma = 0.5, memoryPath = null) {
    super('pick_next_project', '权重衰减随机抽选下一个目标项目');
    this.workspace = workspace;
    this.gamma = gamma;
    this.memoryPath = memoryPath;
    // 持久化状态路径：.omc/state/pick-next-project.json
    this._stateFile = path.join(workspace, '.omc', 'state', 'pick-next-project.json');
  }

  _loadState() {
    try {
      if (fs.existsSync(this._stateFile)) {
        return JSON.parse(fs.readFileSync(this._stateFile, 'utf8'));
      }
    } catch { /* ignore */ }
    return { pickedThisSession: [], lastPick: null };
  }

  _saveState(state) {
    try {
      const dir = path.dirname(this._stateFile);
      if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
      // 原子写入：先写临时文件再 rename
      const tmp = this._stateFile + '.tmp';
      fs.writeFileSync(tmp, JSON.stringify(state, null, 2), 'utf8');
      fs.renameSync(tmp, this._stateFile);
    } catch { /* ignore */ }
  }

  async execute() {
    let memoryFile;
    if (this.memoryPath) {
      memoryFile = this.memoryPath.startsWith('/') || /^[A-Za-z]:/.test(this.memoryPath)
        ? this.memoryPath
        : path.join(this.workspace, this.memoryPath);
    } else {
      memoryFile = path.join(this.workspace, 'MEMORY.md');
    }
    if (!fs.existsSync(memoryFile)) {
      return { picked: null, error: 'MEMORY.md not found', projects: [] };
    }
    if (!fs.existsSync(this.workspace)) {
      return { picked: null, error: 'projects dir not found', projects: [] };
    }

    const content = fs.readFileSync(memoryFile, 'utf8');
    const projectRows = this._parseProjectTable(content);
    if (projectRows.length === 0) {
      return { picked: null, error: 'no projects found', projects: [] };
    }

    const today = new Date().toISOString().split('T')[0];
    const state = this._loadState();
    const todayStr = today.replace(/-/g, '');

    // 判断是否是新的 session（按日期）
    const isNewSession = !state.lastPick || state.lastPick.date !== todayStr;
    const pickedSet = new Set(isNewSession ? [] : (state.pickedThisSession || []));

    // 并行追溯所有"近期"或无效日期的项目（限并发 5 个）
    const CONCURRENCY = 5;
    const toResolve = projectRows.filter(row =>
      !row.lastActive ||
      row.lastActive === '近期' ||
      !/^\d{4}-\d{2}-\d{2}$/.test(row.lastActive)
    );

    const resolvedMap = new Map();
    for (let i = 0; i < toResolve.length; i += CONCURRENCY) {
      const batch = toResolve.slice(i, i + CONCURRENCY);
      const promises = batch.map(row =>
        this._getGitLastActive(row.path).then(date => ({ row, date }))
      );
      const batchResults = await Promise.all(promises);
      for (const { row, date } of batchResults) {
        if (date) resolvedMap.set(row.name, date);
      }
    }

    // 将追溯到的日期写回 MEMORY.md（避免重复追溯）
    if (resolvedMap.size > 0) {
      this._updateMemoryDates(memoryFile, resolvedMap, projectRows);
    }

    const results = [];
    for (const row of projectRows) {
      if (pickedSet.has(row.name)) continue;
      let lastActive = resolvedMap.get(row.name) || row.lastActive;
      if (!lastActive || !/^\d{4}-\d{2}-\d{2}$/.test(lastActive)) continue;
      const days = Math.floor((new Date(today) - new Date(lastActive)) / 86400000);
      const weight = Math.pow(days + 1, this.gamma);
      results.push({
        name: row.name,
        path: row.path,
        lastActive,
        days,
        weight: Math.round(weight * 1000) / 1000,
      });
    }

    if (results.length === 0) {
      return { picked: null, error: 'no valid projects remaining', projects: [] };
    }

    // 加权随机
    const totalWeight = results.reduce((s, r) => s + r.weight, 0);
    const seed = Date.now();
    let random;
    try { random = Math.random() * totalWeight; } catch { random = (seed % 1000) / 1000 * totalWeight; }

    let picked = results[0];
    for (const r of results) {
      random -= r.weight;
      if (random <= 0) { picked = r; break; }
    }

    // 持久化记录
    pickedSet.add(picked.name);
    this._saveState({
      pickedThisSession: Array.from(pickedSet),
      lastPick: { date: todayStr, project: picked.name, days: picked.days },
    });

    results.sort((a, b) => b.weight - a.weight);
    const maxWeight = results[0].weight;
    return {
      picked: picked.name,
      path: picked.path,
      days: picked.days,
      weight: picked.weight,
      gamma: this.gamma,
      totalProjects: results.length,
      allProjects: results,
      maxWeight,
      seed,
    };
  }

  _parseProjectTable(content) {
    const rows = [];
    const lines = content.split('\n');
    let inActiveTable = false;

    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed === '### Active Projects') { inActiveTable = true; continue; }
      if (trimmed.startsWith('### ')) { inActiveTable = false; continue; }
      if (!inActiveTable) continue;
      if (!trimmed.startsWith('|')) continue;
      if (trimmed.includes('---')) continue; // separator line

      // Split by | and filter empty
      const cells = trimmed.split('|').map(c => c.trim()).filter(Boolean);
      if (cells.length < 4) continue;

      const name = cells[0];
      const path = cells[1].replace(/^80-PROJECTS\//, '');
      let lastActive = cells[3] || '近期';

      // Normalize "近期" or malformed dates
      if (!/^\d{4}-\d{2}-\d{2}$/.test(lastActive)) lastActive = '近期';

      if (name && !name.startsWith('#') && !name.startsWith('-')) {
        rows.push({ name, path, lastActive });
      }
    }
    return rows;
  }

  async _getGitLastActive(projectName) {
    const projectPath = path.join(this.workspace, projectName);
    if (!fs.existsSync(projectPath)) return null;
    try {
      const log = execSync(`git log --format="%ai" --max-count=1`, {
        cwd: projectPath,
        encoding: 'utf8',
        timeout: 5000
      }).trim();
      return log ? new Date(log).toISOString().split('T')[0] : null;
    } catch { return null; }
  }

  /**
   * 将追溯到的真实日期写回 MEMORY.md，避免重复追溯
   * 找到包含项目名的行，将"近期"替换为真实日期
   */
  _updateMemoryDates(memoryFile, resolvedMap, projectRows) {
    try {
      let lines = fs.readFileSync(memoryFile, 'utf8').split('\n');
      let updated = false;

      lines = lines.map(line => {
        for (const row of projectRows) {
          const resolvedDate = resolvedMap.get(row.name);
          if (!resolvedDate) continue;
          if (line.includes(`| ${row.name} |`) && line.includes('近期')) {
            // 把" 近期 "替换为" YYYY-MM-DD "
            line = line.replace(/\s+近期\s+/, ` ${resolvedDate} `);
            updated = true;
          }
        }
        return line;
      });

      if (updated) {
        const tmp = memoryFile + '.tmp';
        fs.writeFileSync(tmp, lines.join('\n'), 'utf8');
        fs.renameSync(tmp, memoryFile);
      }
    } catch { /* ignore */ }
  }
}
