/**
 * Discoverer (Learn Layer)
 * Finds new knowledge from environment
 */

import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';

export class Discoverer {
  constructor(workspace, ltm) {
    this.workspace = workspace;
    this.ltm = ltm;
    this.scanPatterns = [
      { pattern: '*.md', type: 'documentation' },
      { pattern: '*.json', type: 'config' },
      { pattern: '*.mjs', type: 'code' }
    ];
  }

  /**
   * Discover new knowledge from environment
   */
  async discover() {
    const discoveries = [];

    // Scan for patterns
    discoveries.push(...await this.scanPatterns());

    // Analyze git history for patterns
    discoveries.push(...this.analyzeGitHistory());

    // Find optimization opportunities
    discoveries.push(...this.findOptimizationOpportunities());

    // Check for skill gaps
    discoveries.push(...this.identifySkillGaps());

    return discoveries;
  }

  async scanPatterns() {
    const discoveries = [];
    const projectsDir = path.join(this.workspace, '80-PROJECTS');

    if (!fs.existsSync(projectsDir)) return discoveries;

    const projects = fs.readdirSync(projectsDir).filter(p => {
      const stat = fs.statSync(path.join(projectsDir, p));
      return stat.isDirectory() && !p.startsWith('10-');
    });

    for (const project of projects) {
      const projectPath = path.join(projectsDir, project);

      // Check for README
      const hasReadme = fs.existsSync(path.join(projectPath, 'README.md'));
      if (!hasReadme) {
        discoveries.push({
          type: 'missing_resource',
          category: 'documentation',
          target: project,
          finding: `项目 ${project} 缺少 README.md`,
          potential: 'high'
        });
      }

      // Check for package.json
      const hasPackageJson = fs.existsSync(path.join(projectPath, 'package.json'));
      if (hasPackageJson) {
        try {
          const pkg = JSON.parse(
            fs.readFileSync(path.join(projectPath, 'package.json'), 'utf8')
          );
          if (!pkg.scripts?.build && !pkg.scripts?.dev) {
            discoveries.push({
              type: 'missing_script',
              category: 'automation',
              target: project,
              finding: `项目 ${project} 缺少构建脚本`,
              potential: 'medium'
            });
          }
        } catch {}
      }
    }

    return discoveries;
  }

  analyzeGitHistory() {
    const discoveries = [];

    try {
      const out = execSync('git log --oneline -20', {
        cwd: this.workspace,
        encoding: 'utf8',
        timeout: 5000
      });

      const lines = out.trim().split('\n');
      const commits = lines.map(l => l.split(' ')[0]);

      // Find repeated message patterns
      const msgOut = execSync('git log --format="%s" -20', {
        cwd: this.workspace,
        encoding: 'utf8',
        timeout: 5000
      });

      const messages = msgOut.trim().split('\n');
      const patterns = {};

      for (const msg of messages) {
        const key = msg.split(' ')[0].toLowerCase();
        patterns[key] = (patterns[key] || 0) + 1;
      }

      for (const [pattern, count] of Object.entries(patterns)) {
        if (count >= 3) {
          discoveries.push({
            type: 'commit_pattern',
            category: 'process',
            target: 'git',
            finding: `提交信息常用 "${pattern}" 模式 ${count} 次`,
            potential: 'low'
          });
        }
      }

    } catch {}

    return discoveries;
  }

  findOptimizationOpportunities() {
    const discoveries = [];

    // Check .omc directory
    const omcDir = path.join(this.workspace, '.omc');

    if (fs.existsSync(omcDir)) {
      // Check for large files
      try {
        const files = execSync('find .omc -type f -size +5M 2>/dev/null || dir /s /b .omc\\* 2>nul | findstr /r /i "\\.[^.]*[5-9][0-9][0-9][0-9][0-9]"', {
          cwd: this.workspace,
          encoding: 'utf8',
          timeout: 5000
        });

        if (files.trim()) {
          discoveries.push({
            type: 'large_file',
            category: 'resource',
            target: '.omc',
            finding: '发现大于5MB的文件',
            potential: 'medium'
          });
        }
      } catch {}

      // Check session count
      const sessionsDir = path.join(omcDir, 'sessions');
      if (fs.existsSync(sessionsDir)) {
        const sessions = fs.readdirSync(sessionsDir).filter(f => f.endsWith('.json'));
        if (sessions.length > 50) {
          discoveries.push({
            type: 'session_bloat',
            category: 'maintenance',
            target: '.omc/sessions',
            finding: `发现 ${sessions.length} 个会话文件`,
            potential: 'medium'
          });
        }
      }
    }

    return discoveries;
  }

  identifySkillGaps() {
    const discoveries = [];

    // Check if certain operations types are missing
    const requiredCapabilities = [
      'code_generation',
      'documentation',
      'testing',
      'security_analysis'
    ];

    // This would be enhanced with actual skill library integration
    for (const capability of requiredCapabilities) {
      discoveries.push({
        type: 'capability_gap',
        category: 'skill',
        target: capability,
        finding: `缺少 ${capability} 技能`,
        potential: 'high'
      });
    }

    return discoveries;
  }
}
