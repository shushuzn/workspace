/**
 * Improvement Operations
 * Operations that create or fix things in the workspace
 */

import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';
import { ProductiveOperation } from './base.mjs';

export class CleanTempFiles extends ProductiveOperation {
  constructor(workspace) {
    super('clean_temp_files', '清理临时文件和缓存');
    this.workspace = workspace;
  }

  canImprove() {
    const patterns = ['*.tmp', '*.log', '*~', '.DS_Store', 'Thumbs.db'];
    for (const p of patterns) {
      try {
        const out = execSync(`dir /s /b "${p}" 2>nul`, {
          cwd: this.workspace, encoding: 'utf8', timeout: 3000
        }).trim();
        if (out) return true;
      } catch { /* no matches */ }
    }
    return false;
  }

  async execute() {
    const tempPatterns = [
      { pattern: '*.tmp', dirs: ['.omc', '80-PROJECTS'] },
      { pattern: '*.log', dirs: ['.omc'] },
      { pattern: '*~', dirs: ['.omc', '80-PROJECTS'] },
      { pattern: '.DS_Store', dirs: ['80-PROJECTS'] },
    ];

    let cleaned = 0;
    for (const { pattern, dirs } of tempPatterns) {
      for (const dir of dirs) {
        const dirPath = path.join(this.workspace, dir);
        if (!fs.existsSync(dirPath)) continue;
        try {
          const out = execSync(`dir /s /b "${pattern}" 2>nul`, {
            cwd: dirPath, encoding: 'utf8', timeout: 3000
          }).trim();
          if (!out) continue;
          for (const f of out.split('\n').filter(Boolean)) {
            try {
              fs.unlinkSync(f);
              cleaned++;
            } catch { /* ignore */ }
          }
        } catch { /* no matches */ }
      }
    }
    return { cleaned };
  }
}

export class FixPackageScripts extends ProductiveOperation {
  constructor(workspace) {
    super('fix_package_scripts', '修复缺失或无效的 package.json scripts');
    this.workspace = workspace;
  }

  canImprove() {
    const projectsDir = this.workspace;
    if (!fs.existsSync(projectsDir)) return false;
    try {
      const dirs = fs.readdirSync(projectsDir).filter(f => {
        try { return fs.statSync(path.join(projectsDir, f)).isDirectory() && !f.startsWith('.'); }
        catch { return false; }
      });
      for (const d of dirs) {
        const pkgPath = path.join(projectsDir, d, 'package.json');
        if (!fs.existsSync(pkgPath)) continue;
        try {
          const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
          if (!pkg.scripts || typeof pkg.scripts !== 'object') return true;
        } catch { return true; }
      }
    } catch { return false; }
    return false;
  }

  async execute() {
    const projectsDir = this.workspace;
    if (!fs.existsSync(projectsDir)) return { fixed: 0 };

    const dirs = fs.readdirSync(projectsDir).filter(f => {
      try { return fs.statSync(path.join(projectsDir, f)).isDirectory(); }
      catch { return false; }
    });

    let fixed = 0;
    for (const d of dirs) {
      const pkgPath = path.join(projectsDir, d, 'package.json');
      if (!fs.existsSync(pkgPath)) continue;
      try {
        const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
        let changed = false;
        if (!pkg.scripts || typeof pkg.scripts !== 'object') {
          pkg.scripts = { start: 'echo "No start script"', test: 'echo "No test script"' };
          changed = true;
        }
        if (!pkg.scripts.start) { pkg.scripts.start = 'echo "No start script"'; changed = true; }
        if (!pkg.scripts.test) { pkg.scripts.test = 'echo "No test script"'; changed = true; }
        if (changed) {
          fs.writeFileSync(pkgPath, JSON.stringify(pkg, null, 2));
          fixed++;
        }
      } catch { /* ignore */ }
    }
    return { fixed };
  }
}

export class UpdateReadmeDocs extends ProductiveOperation {
  constructor(workspace) {
    super('update_readme_docs', '更新过时或简略的 README 文档');
    this.workspace = workspace;
  }

  canImprove() {
    const projectsDir = this.workspace;
    if (!fs.existsSync(projectsDir)) return false;
    try {
      const dirs = fs.readdirSync(projectsDir).filter(f => {
        try { return fs.statSync(path.join(projectsDir, f)).isDirectory(); }
        catch { return false; }
      });
      for (const d of dirs) {
        const readmePath = path.join(projectsDir, d, 'README.md');
        if (!fs.existsSync(readmePath)) continue;
        try {
          const content = fs.readFileSync(readmePath, 'utf8');
          // README 太简略（少于100字符或只有标题）
          if (content.length < 100 || content.split('\n').length < 3) return true;
        } catch { /* ignore */ }
      }
    } catch { return false; }
    return false;
  }

  async execute() {
    const projectsDir = this.workspace;
    if (!fs.existsSync(projectsDir)) return { updated: 0 };

    const dirs = fs.readdirSync(projectsDir).filter(f => {
      try { return fs.statSync(path.join(projectsDir, f)).isDirectory(); }
      catch { return false; }
    });

    let updated = 0;
    for (const d of dirs) {
      const readmePath = path.join(projectsDir, d, 'README.md');
      if (!fs.existsSync(readmePath)) continue;
      try {
        const content = fs.readFileSync(readmePath, 'utf8');
        if (content.length >= 100 && content.split('\n').length >= 3) continue;

        const pkgPath = path.join(projectsDir, d, 'package.json');
        let description = '项目描述暂无';
        if (fs.existsSync(pkgPath)) {
          try {
            const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
            description = pkg.description || description;
          } catch { /* ignore */ }
        }

        const newContent = `# ${d}

${description}

## 项目信息

- **路径**: ${path.join(projectsDir, d)}

## 快速开始

\`\`\`bash
npm install
npm run dev
\`\`\`
`;
        fs.writeFileSync(readmePath, newContent);
        updated++;
      } catch { /* ignore */ }
    }
    return { updated };
  }
}

export class FindDeadLinks extends ProductiveOperation {
  constructor(workspace) {
    super('find_dead_links', '检查 markdown 中的死链接');
    this.workspace = workspace;
  }

  async execute() {
    const dirs = ['80-PROJECTS', '.omc'].filter(d =>
      fs.existsSync(path.join(this.workspace, d))
    );

    const deadLinks = [];
    const mdFiles = [];

    for (const dir of dirs) {
      const dirPath = path.join(this.workspace, dir);
      try {
        const out = execSync(`dir /s /b "*.md" 2>nul`, {
          cwd: dirPath, encoding: 'utf8', timeout: 5000
        }).trim();
        if (out) mdFiles.push(...out.split('\n').filter(Boolean));
      } catch { /* no md files */ }
    }

    for (const mdFile of mdFiles.slice(0, 50)) { // 限制检查数量
      try {
        const content = fs.readFileSync(mdFile, 'utf8');
        const links = content.match(/\[([^\]]+)\]\(([^)]+)\)/g) || [];
        for (const link of links) {
          const urlMatch = link.match(/\]\(([^)]+)\)/);
          if (!urlMatch) continue;
          const url = urlMatch[1];
          // 只检查本地相对路径链接
          if (url.startsWith('.') || url.startsWith('/')) {
            const linkPath = path.resolve(path.dirname(mdFile), url.split('#')[0]);
            if (!fs.existsSync(linkPath) && !linkPath.includes('#')) {
              deadLinks.push({ file: path.basename(mdFile), link: url });
            }
          }
        }
      } catch { /* ignore */ }
    }

    // 写入 dashboard data
    if (deadLinks.length > 0) {
      const dataFile = path.join(this.workspace, 'dashboard-data.json');
      let data = {};
      try { data = JSON.parse(fs.readFileSync(dataFile, 'utf8')); } catch { /* ignore */ }
      if (!data.deadLinks) data.deadLinks = [];
      for (const dl of deadLinks) {
        if (!data.deadLinks.some(d => d.file === dl.file && d.link === dl.link)) {
          data.deadLinks.push({ ...dl, found_at: new Date().toISOString() });
        }
      }
      fs.writeFileSync(dataFile, JSON.stringify(data, null, 2));
    }

    return { found: deadLinks.length, deadLinks };
  }
}
