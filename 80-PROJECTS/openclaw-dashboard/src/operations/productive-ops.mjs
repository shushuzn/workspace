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
    const projectsDir = path.join(this.workspace, '80-PROJECTS');
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
    const projectsDir = path.join(this.workspace, '80-PROJECTS');
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
    this.destructive = true; // Deletes files (orphan checkpoints, stale sessions)
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
    const projectsDir = path.join(this.workspace, '80-PROJECTS');
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
