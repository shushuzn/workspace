/**
 * Detection Operations
 * Operations that detect/analyze without making changes
 */

import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';
import { DetectionOperation } from './base.mjs';
import { CONFIG } from '../config/default.mjs';

export class CheckProjectReadmes extends DetectionOperation {
  constructor(workspace) {
    super('check_project_readmes', '检查项目 README 完整性');
    this.workspace = workspace;
  }

  async execute() {
    const projectsDir = this.workspace;
    if (!fs.existsSync(projectsDir)) return { total: 0, missing: 0 };

    const dirs = fs.readdirSync(projectsDir).filter(f => {
      try {
        const stat = fs.statSync(path.join(projectsDir, f));
        return stat.isDirectory() && !f.startsWith('10-') && !f.startsWith('.');
      } catch { return false; }
    });

    let missing = 0;
    for (const d of dirs.slice(0, 10)) {
      const readmePath = path.join(projectsDir, d, 'README.md');
      if (!fs.existsSync(readmePath)) missing++;
    }

    return { checked: Math.min(dirs.length, 10), missing };
  }
}

export class CheckMemorySize extends DetectionOperation {
  constructor(workspace) {
    super('check_memory_size', '检查记忆文件大小');
    this.workspace = workspace;
  }

  async execute() {
    const candidates = [
      path.join(this.workspace, '.omc', 'memory', 'MEMORY.md'),
      path.join(process.env.HOME || '', '.claude', 'projects', 'D--OpenClaw-workspace', 'memory', 'MEMORY.md')
    ];

    for (const memPath of candidates) {
      if (fs.existsSync(memPath)) {
        const content = fs.readFileSync(memPath, 'utf8');
        const sizeKB = Math.round(Buffer.byteLength(content, 'utf8') / 1024);
        const isGlobal = memPath.includes('.claude');
        return { sizeKB, lines: content.split('\n').length, global: isGlobal };
      }
    }
    return { sizeKB: 0 };
  }
}

export class BrainstormProjects extends DetectionOperation {
  constructor(workspace) {
    super('brainstorm_projects', '头脑风暴项目优化建议');
    this.workspace = workspace;
  }

  canImprove() {
    const bmDir = path.join(this.workspace, '.omc', 'brainstorm');
    if (!fs.existsSync(bmDir)) return true;
    const files = fs.readdirSync(bmDir).filter(f => f.endsWith('.md'));
    if (files.length === 0) return true;
    const latest = files.sort().pop();
    const age = Date.now() - fs.statSync(path.join(bmDir, latest)).mtimeMs;
    return age > CONFIG.brainstorm.minDaysBetween * 24 * 60 * 60 * 1000;
  }

  async execute() {
    const projectsDir = this.workspace;
    if (!fs.existsSync(projectsDir)) return { ideas: 0 };

    const dirs = fs.readdirSync(projectsDir).filter(f => {
      try {
        const stat = fs.statSync(path.join(projectsDir, f));
        return stat.isDirectory() && !f.startsWith('10-') && !f.startsWith('.');
      } catch { return false; }
    });

    if (dirs.length === 0) return { ideas: 0 };

    const target = dirs[Math.floor(Math.random() * dirs.length)];
    const projectPath = path.join(projectsDir, target);

    const suggestions = [];
    const readmePath = path.join(projectPath, 'README.md');
    const packagePath = path.join(projectPath, 'package.json');
    const srcPath = path.join(projectPath, 'src');

    if (!fs.existsSync(readmePath)) {
      suggestions.push('缺少 README.md - 建议添加项目说明文档');
    }
    if (fs.existsSync(packagePath)) {
      try {
        const pkg = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
        if (!pkg.scripts?.dev && !pkg.scripts?.start) {
          suggestions.push('缺少启动脚本 - 建议添加 dev 或 start 命令');
        }
        if (!pkg.keywords || pkg.keywords.length < 3) {
          suggestions.push('关键词不足 - 建议添加更多关键词提升可发现性');
        }
      } catch { /* ignore */ }
    }
    if (fs.existsSync(srcPath)) {
      const srcFiles = fs.readdirSync(srcPath)
        .filter(f => f.endsWith('.ts') || f.endsWith('.js'));
      if (srcFiles.length > 10) {
        suggestions.push(`src 目录有 ${srcFiles.length} 个文件 - 考虑模块化拆分`);
      }
    }

    if (suggestions.length === 0) {
      return { project: target, ideas: 0, message: '项目状态良好' };
    }

    const brainstormDir = path.join(this.workspace, '.omc', 'brainstorm');
    if (!fs.existsSync(brainstormDir)) fs.mkdirSync(brainstormDir, { recursive: true });

    const timestamp = new Date().toISOString().slice(0, 10);
    const outputPath = path.join(brainstormDir, `${target}-${timestamp}.md`);
    const content = `# ${target} 优化建议\n\n**生成时间**: ${new Date().toLocaleString()}\n\n## 项目信息\n- **路径**: ${projectPath}\n- **建议数量**: ${suggestions.length}\n\n## 优化建议\n${suggestions.map((s, i) => `${i + 1}. ${s}`).join('\n')}\n`;
    fs.writeFileSync(outputPath, content);

    return { project: target, ideas: suggestions.length, suggestions, output: outputPath };
  }
}

export class FindLargeFiles extends DetectionOperation {
  constructor(workspace) {
    super('find_large_files', '查找大文件（仅报告）');
    this.workspace = workspace;
  }

  async execute() {
    const projectsDir = this.workspace;
    if (!fs.existsSync(projectsDir)) return { found: 0 };

    const largeFiles = [];

    const scanDir = (dir, depth = 0) => {
      if (depth > CONFIG.largeFile.maxDepth) return;
      try {
        const entries = fs.readdirSync(dir, { withFileTypes: true });
        for (const entry of entries.slice(0, 50)) {
          if (entry.name.startsWith('.')) continue;
          const fullPath = path.join(dir, entry.name);
          if (entry.isDirectory()) {
            const isSafe = CONFIG.largeFile.safePatterns
              .some(p => entry.name.includes(p));
            if (isSafe || depth < 2) scanDir(fullPath, depth + 1);
          } else if (entry.isFile()) {
            const size = fs.statSync(fullPath).size;
            const sizeMB = size / (1024 * 1024);
            if (sizeMB > CONFIG.largeFile.limitMB) {
              const relPath = fullPath.replace(this.workspace, '').replace(/\\/g, '/');
              if (!CONFIG.largeFileWhitelist.some(w => relPath.includes(w))) {
                largeFiles.push({ path: relPath, sizeMB: sizeMB.toFixed(2) });
              }
            }
          }
        }
      } catch { /* ignore */ }
    };

    scanDir(projectsDir);
    return { found: largeFiles.length, files: largeFiles.slice(0, 5) };
  }
}

export class CheckGitRemotes extends DetectionOperation {
  constructor(workspace) {
    super('check_git_remotes', '检查 git remote 状态');
    this.workspace = workspace;
  }

  async execute() {
    const projectsDir = this.workspace;
    if (!fs.existsSync(projectsDir)) return { checked: 0, issues: [] };

    const dirs = fs.readdirSync(projectsDir).filter(f => {
      try {
        const stat = fs.statSync(path.join(projectsDir, f));
        return stat.isDirectory() && !f.startsWith('10-') && !f.startsWith('.');
      } catch { return false; }
    });

    const issues = [];

    for (const d of dirs) {
      const projectPath = path.join(projectsDir, d);
      const gitFile = path.join(projectPath, '.git');

      // Skip submodules (they have .git as a file pointing to actual gitdir)
      if (fs.existsSync(gitFile)) {
        const stat = fs.statSync(gitFile);
        if (stat.isFile()) {
          const gitContent = fs.readFileSync(gitFile, 'utf8');
          if (gitContent.includes('gitdir:')) continue;
        }
        // else: .git is a directory = normal repo, continue
      }

      try {
        const remote = execSync('git remote get-url origin', {
          cwd: projectPath,
          encoding: 'utf8',
          timeout: 3000
        }).trim();

        if (!remote) {
          issues.push({ project: d, type: 'no_remote', detail: '无有效 remote' });
          continue;
        }

        // Check for stale branches
        try {
          const branches = execSync('git branch -vv', {
            cwd: projectPath,
            encoding: 'utf8',
            timeout: 3000
          });
          const stale = branches.split('\n').filter(l => l.includes(': gone]'));
          for (const s of stale) {
            const match = s.match(/^\s*(\S+)/);
            if (match) {
              issues.push({ project: d, type: 'stale_branch', detail: `${d}/${match[1]}` });
            }
          }
        } catch { /* ignore */ }
      } catch { /* not a git repo */ }
    }

    // Write to dashboard data
    if (issues.length > 0) {
      const dataFile = path.join(this.workspace, 'dashboard-data.json');
      let data = {};
      if (fs.existsSync(dataFile)) {
        try { data = JSON.parse(fs.readFileSync(dataFile, 'utf8')); } catch { /* ignore */ }
      }
      if (!data.issues) data.issues = [];
      for (const issue of issues) {
        const key = `${issue.type}:${issue.project}:${issue.detail}`;
        if (!data.issues.some(i => i.key === key)) {
          data.issues.push({ ...issue, key, found_at: new Date().toISOString(), resolved: false });
        }
      }
      fs.writeFileSync(dataFile, JSON.stringify(data, null, 2));
    }

    return { checked: dirs.length, issues };
  }
}
