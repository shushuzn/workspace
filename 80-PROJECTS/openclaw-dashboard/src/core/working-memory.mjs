/**
 * Working Memory (Core Layer)
 * Calculates workspace health score (0-100+)
 * Refactored from: health-scorer.mjs
 */

import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';

export class WorkingMemory {
  constructor(workspace) {
    this.workspace = workspace;
  }

  calculate() {
    let score = 50; // Base score

    try {
      score += this.projectScore();
      score += this.readmeScore();
      score += this.memoryScore();
      score += this.stateCleanScore();
      score += this.gitScore();
      score += this.brainstormScore();
    } catch (e) {
      console.error('[WorkingMemory] Score calculation error:', e.message);
    }

    return Math.min(100, Math.max(0, score));
  }

  /**
   * Get detailed health breakdown
   */
  getDetailedScore() {
    return {
      total: this.calculate(),
      projects: this.projectScore(),
      readmes: this.readmeScore(),
      memory: this.memoryScore(),
      state: this.stateCleanScore(),
      git: this.gitScore(),
      brainstorm: this.brainstormScore()
    };
  }

  projectScore() {
    const projectsDir = this.workspace;
    if (!fs.existsSync(projectsDir)) return 0;

    const dirs = fs.readdirSync(projectsDir).filter(f => {
      try {
        const stat = fs.statSync(path.join(projectsDir, f));
        return stat.isDirectory() && !f.startsWith('10-') && !f.startsWith('.');
      } catch { return false; }
    });

    return Math.min(dirs.length, 30); // Max +30
  }

  readmeScore() {
    const projectsDir = this.workspace;
    if (!fs.existsSync(projectsDir)) return 0;

    const dirs = fs.readdirSync(projectsDir).filter(f => {
      try {
        const stat = fs.statSync(path.join(projectsDir, f));
        return stat.isDirectory() && !f.startsWith('10-') && !f.startsWith('.');
      } catch { return false; }
    });

    const withReadme = dirs.filter(d =>
      fs.existsSync(path.join(projectsDir, d, 'README.md'))
    );
    const ratio = dirs.length > 0 ? withReadme.length / dirs.length : 0;
    return Math.round(ratio * 10); // 0-10 points
  }

  memoryScore() {
    const candidates = [
      path.join(this.workspace, '.omc', 'memory', 'MEMORY.md'),
      path.join(process.env.HOME || '', '.claude', 'projects', 'D--OpenClaw-workspace', 'memory', 'MEMORY.md')
    ];

    for (const memPath of candidates) {
      if (fs.existsSync(memPath)) {
        const content = fs.readFileSync(memPath, 'utf8');
        const sizeKB = Buffer.byteLength(content, 'utf8') / 1024;
        return sizeKB < 150 ? 10 : -10;
      }
    }
    return 0;
  }

  stateCleanScore() {
    const sessionsDir = path.join(this.workspace, '.omc', 'sessions');
    const checkpointsDir = path.join(this.workspace, '.omc', 'state', 'checkpoints');

    let totalFiles = 0;
    if (fs.existsSync(sessionsDir)) {
      totalFiles += fs.readdirSync(sessionsDir).filter(f => f.endsWith('.json')).length;
    }
    if (fs.existsSync(checkpointsDir)) {
      totalFiles += fs.readdirSync(checkpointsDir).filter(f => f.endsWith('.json')).length;
    }

    // Sliding scale
    if (totalFiles < 5) return 10;
    if (totalFiles < 20) return 8;
    if (totalFiles < 40) return 6;
    if (totalFiles < 60) return 4;
    if (totalFiles < 100) return 2;
    return 0;
  }

  gitScore() {
    try {
      const out = execSync('git status --porcelain', {
        cwd: this.workspace,
        encoding: 'utf8',
        timeout: 5000
      }).trim();

      const changed = out ? out.split('\n').filter(l => {
        const trimmed = l.trim();
        return trimmed &&
          !trimmed.includes('loop-history.json') &&
          !trimmed.includes('dashboard-data.json');
      }).length : 0;

      if (changed === 0) return 10;
      if (changed <= 3) return 5;
      if (changed <= 10) return 2;
      return -Math.min(changed - 10, 10);
    } catch {
      return 0;
    }
  }

  brainstormScore() {
    const brainstormDir = path.join(this.workspace, '.omc', 'brainstorm');
    if (!fs.existsSync(brainstormDir)) return 0;

    const files = fs.readdirSync(brainstormDir).filter(f => f.endsWith('.md'));
    // Penalize if > 20 files
    if (files.length > 20) {
      return -Math.floor((files.length - 20) / 10);
    }
    return 0;
  }
}
