/**
 * Productive Operations
 * Operations that make changes to the workspace
 */

import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { execSync, exec } from 'child_process';
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
    // γ 必须在 (0, 2] 区间（0.3~0.7 为推荐范围，见 CLAUDE.md §9）
    const validGamma = (typeof gamma === 'number' && isFinite(gamma) && gamma > 0 && gamma <= 2);
    this.gamma = validGamma ? gamma : 0.5;
    this.memoryPath = memoryPath;
    // 持久化状态路径：.omc/state/pick-next-project.json
    this._stateFile = path.join(workspace, '.omc', 'state', 'pick-next-project.json');
  }

  _lockFile() { return this._stateFile + '.lock'; }

  async _acquireLock(maxRetries = 3, intervalMs = 50) {
    const lockPath = this._lockFile();
    for (let i = 0; i < maxRetries; i++) {
      try {
        fs.writeFileSync(lockPath, String(process.pid), { flag: 'wx' });
        return true;
      } catch (e) {
        if (e.code !== 'EEXIST') return false;
        // 检测是否是陈腐锁（持有进程已退出），直接删除后重试
        let stale = false;
        try {
          const pid = parseInt(fs.readFileSync(lockPath, 'utf8'), 10);
          // PID <= 0 说明锁已损坏，视为陈腐
          if (pid <= 0 || !this._isRunningPid(pid)) stale = true;
        } catch { stale = true; }
        if (stale) {
          try { fs.unlinkSync(lockPath); } catch { /* ignore */ }
          continue;
        }
        // 非陈腐锁，等待后重试
        await new Promise(resolve => setTimeout(resolve, intervalMs));
      }
    }
    return false;
  }

  _isRunningPid(pid) {
    try {
      // Windows: process.kill(pid, 0) 会失败如果进程不存在
      process.kill(pid, 0);
      return true;
    } catch { return false; }
  }

  _releaseLock() {
    try { fs.unlinkSync(this._lockFile()); } catch { /* ignore */ }
  }

  /**
   * 记录项目体检失败（公开方法，供 CLI 在 _runHealthCheck 失败后调用）
   * @param {string} projectName
   */
  /**
   * 记录项目体检成功，自动更新 MEMORY.md Last Active 为今天
   * @param {string} projectName
   */
  recordHealthSuccess(projectName) {
    if (!projectName) return;
    const today = new Date().toISOString().split('T')[0];
    const memoryFile = this.memoryPath;
    if (memoryFile && fs.existsSync(memoryFile)) {
      this._updateProjectLastActive(memoryFile, projectName, today);
    }
  }

  recordHealthFailure(projectName) {
    if (!projectName) return;
    // 直接写文件，不加锁（execute 已释放锁后才调用此方法，并发风险可忽略）
    try {
      const state = this._loadState();
      const today = new Date().toISOString().split('T')[0].replace(/-/g, '');
      if (!state.healthFailures) state.healthFailures = {};
      if (!state.healthFailures[projectName]) {
        state.healthFailures[projectName] = { count: 0, lastFail: null };
      }
      state.healthFailures[projectName].count++;
      state.healthFailures[projectName].lastFail = today;
      this._saveState(state);
    } catch { /* ignore */ }
  }

  _loadState() {
    if (!fs.existsSync(this._stateFile)) {
      return { pickedThisSession: [], lastPick: null, healthFailures: {} };
    }
    try {
      const raw = fs.readFileSync(this._stateFile, 'utf8');
      const state = JSON.parse(raw);
      // 清理超过 7 天的历史 lastPick（只保留最近一条作为参考）
      const cutoff = new Date();
      cutoff.setDate(cutoff.getDate() - 7);
      const cutoffStr = cutoff.toISOString().split('T')[0].replace(/-/g, '');
      const recentLastPick = state.lastPick && state.lastPick.date >= cutoffStr
        ? state.lastPick : (state.lastPick || null);
      // 清理超过 30 天的健康失败记录
      const healthCutoff = new Date();
      healthCutoff.setDate(healthCutoff.getDate() - 30);
      const healthCutoffStr = healthCutoff.toISOString().split('T')[0].replace(/-/g, '');
      const healthFailures = {};
      if (state.healthFailures) {
        for (const [name, record] of Object.entries(state.healthFailures)) {
          if (record.lastFail && record.lastFail >= healthCutoffStr) {
            healthFailures[name] = record;
          }
        }
      }
      return {
        pickedThisSession: Array.isArray(state.pickedThisSession) ? state.pickedThisSession : [],
        lastPick: recentLastPick,
        healthFailures,
        last_radar_check: state.last_radar_check || null,
      };
    } catch { /* ignore */ }
    return { pickedThisSession: [], lastPick: null, healthFailures: {}, last_radar_check: null };
  }

  _saveState(state) {
    try {
      const dir = path.dirname(this._stateFile);
      if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
      // 原子写入：先写临时文件再 rename
      const tmp = this._stateFile + '.tmp';
      // last_radar_check 统一存为 YYYYMMDD 格式
      const toSave = { ...state, last_radar_check: state.last_radar_check ? String(state.last_radar_check).replace(/-/g, '') : undefined };
      fs.writeFileSync(tmp, JSON.stringify(toSave, null, 2), 'utf8');
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

    // 加锁，防止并发调用导致状态文件损坏
    if (!this._acquireLock()) {
      return { picked: null, error: '无法获取锁，并发调用冲突', projects: [] };
    }
    try {
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
    // pickedThisSession 按 date 分组，避免项目更名导致去重失效
    const pickedByDate = state.pickedThisSession || [];
    const todayPicked = Array.isArray(pickedByDate) && !isNewSession
      ? pickedByDate.filter(p => p.date === todayStr).map(p => p.name)
      : [];
    const pickedSet = new Set(todayPicked);

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
      // 重新读取更新后的 MEMORY.md，确保后续计算用的是最新数据
      const updatedContent = fs.readFileSync(memoryFile, 'utf8');
      projectRows = this._parseProjectTable(updatedContent);
    }

    const results = [];
    const healthFailures = state.healthFailures || {};
    for (const row of projectRows) {
      if (pickedSet.has(row.name)) continue;
      let lastActive = resolvedMap.get(row.name) || row.lastActive;
      if (!lastActive || !/^\d{4}-\d{2}-\d{2}$/.test(lastActive)) continue;
      const days = Math.floor((new Date(today) - new Date(lastActive)) / 86400000);
      // 健康失败加权：失败过的项目额外获得 boost，每次失败 +50% weight
      const failRecord = healthFailures[row.name];
      const failBoost = failRecord ? 1 + (failRecord.count || 1) * 0.5 : 1;
      const weight = Math.pow(days + 1, this.gamma) * failBoost;
      results.push({
        name: row.name,
        path: row.path,
        lastActive,
        days,
        weight: Math.round(weight * 1000) / 1000,
        failCount: failRecord ? failRecord.count : 0,
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
    const newPicked = Array.from(pickedSet).map(name => ({ name, date: todayStr }));
    this._saveState({
      pickedThisSession: newPicked,
      lastPick: { date: todayStr, project: picked.name, days: picked.days },
      healthFailures: state.healthFailures || {},
      last_radar_check: state.last_radar_check || todayStr,
    });

    results.sort((a, b) => b.weight - a.weight);
    const maxWeight = results[0].weight;

    // 随机选一个配对项目
    const remaining = results.filter(r => r.name !== picked.name);
    const pair = remaining.length > 0
      ? remaining[Math.floor(Math.random() * remaining.length)]
      : null;

    // 找共享依赖，如有则写入 MEMORY.md 交叉链接表
    const bridge = pair ? this._findBridgeConcepts(picked.path, pair.path) : null;
    if (bridge) {
      this._appendCrossLink(memoryFile, picked.name, pair.name, bridge.shared);
    }

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
      pair: pair ? { name: pair.name, path: pair.path } : null,
      bridge,
      state,
    };
    } finally { this._releaseLock(); }
  }

  /**
   * 找两个项目之间的桥接依赖
   * 读取各自的 package.json，取 dependencies + devDependencies 的交集
   */
  _findBridgeConcepts(pathA, pathB) {
    const depsA = this._getPackageDeps(pathA);
    const depsB = this._getPackageDeps(pathB);
    if (!depsA || !depsB) return null;

    const shared = [...depsA].filter(d => depsB.has(d));
    if (shared.length === 0) return null;

    return { shared: shared[0], allShared: shared.slice(0, 5) };
  }

  _getPackageDeps(projectPath) {
    const pkgPath = path.join(this.workspace, projectPath, 'package.json');
    try {
      if (!fs.existsSync(pkgPath)) return null;
      const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
      const deps = new Set([
        ...Object.keys(pkg.dependencies || {}),
        ...Object.keys(pkg.devDependencies || {}),
      ]);
      return deps;
    } catch { return null; }
  }

  /**
   * 将共享依赖配对追加到 MEMORY.md 交叉链接表（幂等）
   */
  _appendCrossLink(memoryFile, nameA, nameB, sharedDep) {
    const MAX_ENTRIES = 100;
    try {
      if (!fs.existsSync(memoryFile)) return;
      const lines = fs.readFileSync(memoryFile, 'utf8').split('\n');
      const marker = '## 交叉链接';
      let markerIdx = -1;
      let insertIdx = lines.length;

      for (let i = 0; i < lines.length; i++) {
        if (lines[i].includes(marker)) { markerIdx = i; continue; }
        if (markerIdx >= 0 && !lines[i].startsWith('|')) {
          insertIdx = i;
          break;
        }
      }

      // 幂等检查：已存在则不重复写入
      for (let i = markerIdx >= 0 ? markerIdx : 0; i < lines.length; i++) {
        if (lines[i].includes(`↔`) && lines[i].includes(nameA) && lines[i].includes(nameB)) {
          return;
        }
      }

      const newLine = `| ${nameA} ↔ ${nameB} | 关联 | 共享依赖: ${sharedDep} |`;
      lines.splice(insertIdx, 0, newLine);

      // 限制条目数量不超过 MAX_ENTRIES（从最后往前数，删除超出的旧条目）
      const tableLines = lines.filter(l => l.startsWith('|') && l.includes('↔'));
      if (tableLines.length > MAX_ENTRIES) {
        const excess = tableLines.length - MAX_ENTRIES;
        // 从后往前删
        let removed = 0;
        for (let i = lines.length - 1; i >= 0 && removed < excess; i--) {
          if (lines[i].startsWith('|') && lines[i].includes('↔')) {
            lines.splice(i, 1);
            removed++;
          }
        }
      }

      const tmp = memoryFile + '.tmp';
      fs.writeFileSync(tmp, lines.join('\n'), 'utf8');
      fs.renameSync(tmp, memoryFile);
    } catch { /* ignore */ }
  }

  _extractKeywords(text) {
    const stopWords = new Set([
      'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her',
      'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how',
      'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 'did',
      'she', 'use', 'way', 'will', 'with', 'your', 'from', 'have', 'this', 'that',
      '的', '了', '是', '在', '和', '有', '我', '你', '他', '她', '它',
      '这', '那', '就', '也', '都', '会', '能', '要', '可以', '一个',
      '什么', '怎么', '为什么', '如果', '因为', '所以', '但是', '而且',
    ]);
    const words = new Map();
    // 提取 2-4 字的中文词
    for (const w of (text.match(/[\u4e00-\u9fa5]{2,4}/g) || [])) {
      if (!stopWords.has(w) && !/^\d+$/.test(w)) {
        words.set(w, (words.get(w) || 0) + 1);
      }
    }
    // 提取英文词（3词以上），统一小写避免重复
    for (const w of (text.match(/[a-zA-Z]{3,}/g) || [])) {
      const lower = w.toLowerCase();
      if (!stopWords.has(lower)) {
        words.set(lower, (words.get(lower) || 0) + 1);
      }
    }
    // 按频次降序，返回 Set
    return new Set(
      [...words.entries()]
        .sort((a, b) => b[1] - a[1])
        .slice(0, 80)
        .map(([w]) => w)
    );
  }

  /**
   * 自动体检：尝试启动项目并验证是否正常运行
   * 检测 package.json / requirements.txt / go.mod，执行对应启动命令
   */
  async _runHealthCheck(projectPath) {
    // 兼容：路径可能是 'ai-roundtable' 或 '80-PROJECTS/ai-roundtable'
    const fullPath = fs.existsSync(path.join(this.workspace, projectPath))
      ? path.join(this.workspace, projectPath)
      : path.join(this.workspace, '80-PROJECTS', projectPath);
    const pkg = path.join(fullPath, 'package.json');
    const req = path.join(fullPath, 'requirements.txt');
    const goMod = path.join(fullPath, 'go.mod');

    let cmd = null;
    let type = null;

    if (fs.existsSync(pkg)) {
      try {
        const scripts = JSON.parse(fs.readFileSync(pkg, 'utf8')).scripts || {};
        if (scripts['dev']) { cmd = 'npm run dev'; type = 'npm'; }
        else if (scripts['start']) { cmd = 'npm start'; type = 'npm'; }
        else if (scripts['preview']) { cmd = 'npm run preview'; type = 'npm'; }
      } catch { /* ignore */ }
    } else if (fs.existsSync(goMod)) {
      cmd = 'go run .';
      type = 'go';
    } else if (fs.existsSync(req)) {
      cmd = 'python main.py';
      type = 'python';
    }

    if (!cmd) return { status: 'skip', reason: '无可执行的启动命令' };

    return new Promise(resolve => {
      const timeout = setTimeout(() => {
        proc.kill();
        resolve({ status: 'timeout', reason: '启动超时（3分钟）' });
      }, 180000);

      let output = '';
      const proc = exec(cmd, { cwd: fullPath, timeout: 185000 }, (err, stdout, stderr) => {
        clearTimeout(timeout);
        if (err) {
          output += stderr;
          // 识别常见启动失败模式
          if (output.includes('EADDRINUSE') || output.includes('port')) {
            resolve({ status: 'fail', reason: '端口被占用', output: output.slice(-500) });
          } else if (output.includes('MODULE_NOT_FOUND') || output.includes('Cannot find')) {
            resolve({ status: 'fail', reason: '依赖缺失', output: output.slice(-500) });
          } else {
            resolve({ status: 'fail', reason: '启动失败', output: output.slice(-500) });
          }
        } else {
          resolve({ status: 'ok', reason: '正常启动', output: stdout.slice(-200) });
        }
      });

      proc.stderr.on('data', d => { output += d; });
      proc.stdout.on('data', d => { output += d; });
    });
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
   * 将指定项目的 Last Active 更新为指定日期（原子写入）
   */
  _updateProjectLastActive(memoryFile, projectName, date) {
    try {
      const today = date || new Date().toISOString().split('T')[0];
      const lines = fs.readFileSync(memoryFile, 'utf8').split('\n');
      const idx = lines.findIndex(l => l.startsWith('| ' + projectName + ' |'));
      if (idx < 0) return;
      const updated = lines[idx].replace(/\d{4}-\d{2}-\d{2}/, today);
      if (updated === lines[idx]) return; // 日期未变
      lines[idx] = updated;
      const tmp = memoryFile + '.tmp';
      fs.writeFileSync(tmp, lines.join('\n'), 'utf8');
      fs.renameSync(tmp, memoryFile);
    } catch { /* ignore */ }
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

/**
 * IdeaPool — 创新想法池管理
 * 负责 .omc/innovation/ideas.md 的读写和生命周期维护
 */
export class IdeaPool {
  constructor(workspace) {
    this.workspace = workspace;
    this.file = path.join(workspace, '.omc', 'innovation', 'ideas.md');
  }

  _today() {
    return new Date().toISOString().split('T')[0].replace(/-/g, '');
  }

  _daysOld(dateStr) {
    const s = String(dateStr).replace(/-/g, '');
    const d = new Date(`${s.slice(0,4)}-${s.slice(4,6)}-${s.slice(6,8)}`);
    return Math.floor((new Date() - d) / 86400000);
  }

  /** 追加一条 idea，source: brainstorm/suggest/manual */
  add(stage, desc, source = 'manual') {
    const ideas = this._read();
    ideas.push({ date: this._today(), stage, desc, source });
    this._write(ideas);
    return ideas.length - 1;
  }

  /** 推进 idea 状态，shipped 时自动记录交付时间戳 */
  advance(idx, targetStage) {
    const ideas = this._read();
    if (idx < 0 || idx >= ideas.length) return false;
    let desc = ideas[idx].desc;
    if (targetStage === 'shipped') {
      desc = `${desc} | shipped:${this._today()}`;
    }
    ideas[idx] = { ...ideas[idx], stage: targetStage, desc };
    this._write(ideas);
    return true;
  }

  /** 放弃 idea */
  kill(idx, reason) {
    const ideas = this._read();
    if (idx < 0 || idx >= ideas.length) return false;
    const desc = `${ideas[idx].desc} | killed:${this._today()} ${reason}`;
    ideas[idx] = { ...ideas[idx], stage: 'killed', desc };
    this._write(ideas);
    return true;
  }

  /** 给 idea 打分: impact(1-3) × effort(1-3) */
  score(idx, impact, effort) {
    const ideas = this._read();
    if (idx < 0 || idx >= ideas.length) return false;
    ideas[idx] = { ...ideas[idx], impact, effort };
    this._write(ideas);
    return true;
  }

  /** 给 idea 添加收益描述 */
  benefit(idx, desc) {
    const ideas = this._read();
    if (idx < 0 || idx >= ideas.length) return false;
    const cleanDesc = (ideas[idx].desc || '').replace(/\s*\| benefit:.*$/, '');
    ideas[idx] = { ...ideas[idx], desc: `${cleanDesc} | benefit:${desc}` };
    this._write(ideas);
    return true;
  }

  /** 自动清理过时 idea（返回清理数量） */
  prune() {
    const TTL_BASE = { seed: 3, proposal: 7, running: 14, shipped: null, killed: null, dormant: 30 };
    const ideas = this._read();
    const before = ideas.length;
    this._write(ideas.filter(idea => {
      if (idea.stage === 'shipped' || idea.stage === 'killed') return true;
      let ttl = TTL_BASE[idea.stage];
      if (!ttl) return true;
      // 高分 seed 获得延长保鲜期
      if (idea.stage === 'seed' && idea.impact && idea.effort) {
        const s = idea.impact * idea.effort;
        if (s >= 6) ttl = 7;
        else if (s >= 4) ttl = 5;
      }
      return this._daysOld(idea.date) <= ttl;
    }));
    return before - ideas.length;
  }

  /** 列出所有 idea */
  list() {
    return this._read().map((idea, i) => ({ idx: i, ...idea }));
  }

  _read() {
    if (!fs.existsSync(this.file)) return [];
    const raw = fs.readFileSync(this.file, 'utf8');
    const ideas = [];
    for (const line of raw.split('\n')) {
      // 支持: - [DATE] stage [source] [score:3x2] description [| shipped:DATE | killed:DATE REASON | benefit:描述]
      const m = line.match(/^-\s*\[(\d{8})\]\s*(\w+)(?:\s*\[(\w+)\])?\s*(?:\[score:(\d+)x(\d+)\]\s*)?(.*)/);
      if (!m) continue;
      const desc = m[6].trim();
      const shippedMatch = desc.match(/\| shipped:(\d{8})/);
      const killedMatch  = desc.match(/\| killed:(\d{8})(?: (.*))?$/);
      ideas.push({
        date:    m[1],
        stage:   m[2],
        source:  m[3] || 'manual',
        impact:  m[4] ? parseInt(m[4]) : null,
        effort:  m[5] ? parseInt(m[5]) : null,
        desc:    desc,
        shipped: shippedMatch ? shippedMatch[1] : null,
        killed:  killedMatch ? killedMatch[1] : null,
        benefit: benefitMatch ? benefitMatch[1].trim() : null,
      });
    }
    return ideas;
  }

  _write(ideas) {
    const dir = path.dirname(this.file);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    const header = `# Idea Pool

> 每个 session 产生的 idea 必须立即追加到此文件。
> 格式：`- [DATE] STAGE [source] [score:3x2] description [| shipped:DATE | killed:DATE REASON | benefit:描述]`
> STAGE: seed / proposal / running / shipped / killed / dormant
> SOURCE: brainstorm / suggest / manual（默认 manual）

`;
    const body = ideas.map(i => {
      const src   = i.source  ? ` [${i.source}]`  : '';
      const score = (i.impact && i.effort) ? ` [score:${i.impact}x${i.effort}]` : '';
      // 去除 desc 末尾可能残留的 [score:NxM]（避免与 score 字段重复）
      const cleanDesc = (i.desc || '').replace(/\s*\[score:\d+x\d+\]\s*$/, '');
      return `- [${i.date}] ${i.stage}${src}${score} ${cleanDesc}`;
    }).join('\n');
    const tmp = this.file + '.tmp';
    fs.writeFileSync(tmp, header + body + '\n', 'utf8');
    fs.renameSync(tmp, this.file);
  }
}
