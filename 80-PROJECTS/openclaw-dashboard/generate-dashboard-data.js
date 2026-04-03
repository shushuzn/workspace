#!/usr/bin/env node
/**
 * Dashboard Data Generator
 * Reads workspace state and generates dashboard-data.json
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const WORKSPACE = path.join(__dirname, '..', '..');
const OUTPUT = __dirname + '/dashboard-data.json';

function detectTechStack(projectPath) {
  const pkgPath = path.join(projectPath, 'package.json');
  const reqPath = path.join(projectPath, 'requirements.txt');
  const pyPath = path.join(projectPath, 'pyproject.toml');
  const cargoPath = path.join(projectPath, 'Cargo.toml');

  // Check package.json for JS/TS frameworks
  if (fs.existsSync(pkgPath)) {
    try {
      const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
      const deps = { ...pkg.dependencies, ...pkg.devDependencies };

      // Check specific frameworks
      if (deps.svelte || deps['@sveltejs/vite-plugin-svelte']) return 'Svelte';
      if (deps.react) return 'React';
      if (deps.vue) return 'Vue';
      if (deps.next) return 'Next.js';
      if (deps.express) return 'Express';
      if (deps.fastapi) return 'FastAPI';
      if (deps.flask) return 'Flask';
      if (deps.nestjs || deps['@nestjs/core']) return 'NestJS';
      if (deps.electron) return 'Electron';
      if (deps['@anthropic-ai/sdk'] || deps.ai) return 'AI/Claude';
      if (deps.ollama) return 'Ollama';
      if (deps.mcp) return 'MCP';

      // Check for TypeScript
      if (deps.typescript || deps['@types/node']) return 'TypeScript';

      // Generic Node.js
      if (deps.node) return 'Node.js';

      // Check scripts for hints
      const scripts = pkg.scripts || {};
      if (scripts.vite) return 'Vite';
      if (scripts.next) return 'Next.js';
      if (scripts.dev && scripts.dev.includes('react')) return 'React';
    } catch (e) { console.error('pkg parse error:', e.message); }
  }

  // Check Python projects
  if (fs.existsSync(reqPath) || fs.existsSync(pyPath)) {
    try {
      const content = fs.readFileSync(reqPath || pyPath, 'utf8');
      if (content.includes('fastapi')) return 'Python/FastAPI';
      if (content.includes('flask')) return 'Python/Flask';
      if (content.includes('django')) return 'Python/Django';
      if (content.includes('pandas') || content.includes('numpy')) return 'Python/Data';
      return 'Python';
    } catch (e) { console.error('pkg parse error:', e.message); }
  }

  // Check Rust projects
  if (fs.existsSync(cargoPath)) {
    try {
      const content = fs.readFileSync(cargoPath, 'utf8');
      if (content.includes('tauri')) return 'Rust/Tauri';
      return 'Rust';
    } catch (e) { console.error('pkg parse error:', e.message); }
  }

  return 'TypeScript'; // default
}

function getProjectDetails(projectPath) {
  const details = {
    dependencies: [],
    devDependencies: [],
    scripts: [],
    description: '',
    main: '',
    repo: ''
  };

  const pkgPath = path.join(projectPath, 'package.json');
  if (fs.existsSync(pkgPath)) {
    try {
      const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
      details.dependencies = Object.keys(pkg.dependencies || {}).slice(0, 5);
      details.devDependencies = Object.keys(pkg.devDependencies || {}).slice(0, 3);
      details.scripts = Object.keys(pkg.scripts || {}).slice(0, 6);
      details.description = pkg.description || '';
      details.main = pkg.main || '';
      details.repo = pkg.repository?.url || '';
    } catch (e) { console.error('pkg parse error:', e.message); }
  }

  const readmePath = path.join(projectPath, 'README.md');
  if (fs.existsSync(readmePath)) {
    try {
      const lines = fs.readFileSync(readmePath, 'utf8').split('\n');
      const descLine = lines.find(l => l.trim() && !l.startsWith('#') && !l.startsWith('```'));
      if (descLine && !details.description) {
        details.description = descLine.trim().substring(0, 120);
      }
    } catch (e) { console.error('pkg parse error:', e.message); }
  }

  return details;
}

function getProjects() {
  const projectsDir = path.join(WORKSPACE, '80-PROJECTS');
  if (!fs.existsSync(projectsDir)) return [];

  const dirs = fs.readdirSync(projectsDir).filter(f => {
    const stat = fs.statSync(path.join(projectsDir, f));
    return stat.isDirectory() && !f.startsWith('10-') && !f.startsWith('.');
  });

  return dirs.slice(0, 12).map(name => {
    const projectPath = path.join(projectsDir, name);
    const pkgPath = path.join(projectPath, 'package.json');

    // Detect tech stack
    let meta = detectTechStack(projectPath);

    // Get project details
    const details = getProjectDetails(projectPath);

    // Try to get last active from git log
    let lastActive = null;
    let hasChanges = false;
    let gitStatus = '';
    try {
      // Get last commit time (cross-platform: works on Git Bash/Unix/Windows)
      const isWin = process.platform === 'win32';
      const nullDev = isWin ? '2>nul' : '2>/dev/null';
      const log = execSync(`git log -1 --format="%ai" -- "*.ts" "*.js" "*.py" ${nullDev} || echo ""`, {
        cwd: projectPath,
        encoding: 'utf8',
        stdio: 'pipe',
        timeout: 3000
      }).trim();
      if (log && log.match(/^\d{4}-\d{2}-\d{2}/)) {
        lastActive = log.split(' ')[0];
      }
    } catch (e) { console.error('pkg parse error:', e.message); }

    try {
      // Check for uncommitted changes
      const isWin = process.platform === 'win32';
      const nullDev = isWin ? '2>nul' : '2>/dev/null';
      const status = execSync(`git status --porcelain ${nullDev} || echo ""`, {
        cwd: projectPath,
        encoding: 'utf8',
        stdio: 'pipe',
        timeout: 3000
      }).trim();
      hasChanges = status.length > 0;
      gitStatus = status || '';
    } catch (e) { console.error('pkg parse error:', e.message); }

    // Get current branch
    let branch = 'main';
    try {
      const isWin = process.platform === 'win32';
      const nullDev = isWin ? '2>nul' : '2>/dev/null';
      const branchOut = execSync(`git branch --show-current ${nullDev} || echo main`, {
        cwd: projectPath,
        encoding: 'utf8',
        stdio: 'pipe',
        timeout: 3000
      }).trim();
      if (branchOut) branch = branchOut;
    } catch (e) {}

    return {
      name,
      meta,
      description: details.description || '',
      lastActive,
      status: hasChanges ? 'modified' : 'idle',
      gitStatus,
      branch,
      dependencies: details.dependencies,
      devDependencies: details.devDependencies,
      scripts: details.scripts
    };
  });
}

function getSubmodules() {
  try {
    const result = execSync('git submodule status', {
      cwd: WORKSPACE,
      encoding: 'utf8',
      stdio: 'pipe'
    });
    return result.split('\n').filter(l => l.trim()).map(line => {
      const parts = line.trim().split(' ');
      return { path: parts[1] || parts[0] };
    }).filter(s => s.path);
  } catch {
    return [
      { path: '80-PROJECTS/idle-empire' },
      { path: '80-PROJECTS/50-ton-hackathon' },
      { path: '80-PROJECTS/stock-analysis-mcp' },
      { path: '80-PROJECTS/stock-analyzer-v2' },
    ];
  }
}

function getRecentSessions() {
  const sessionsDir = path.join(WORKSPACE, 'sessions');
  if (!fs.existsSync(sessionsDir)) return [];

  const files = fs.readdirSync(sessionsDir)
    .filter(f => f.endsWith('.json'))
    .map(f => ({
      name: f.replace('.json', ''),
      mtime: fs.statSync(path.join(sessionsDir, f)).mtime
    }))
    .sort((a, b) => b.mtime - a.mtime)
    .slice(0, 5);

  return files.map((f, i) => {
    const now = new Date();
    const diff = now - f.mtime;
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(hours / 24);

    let timeStr;
    if (i === 0) timeStr = '活跃中';
    else if (hours < 1) timeStr = '刚刚';
    else if (hours < 24) timeStr = `${hours}小时前`;
    else timeStr = `${days}天前`;

    return {
      id: f.name.substring(0, 8),
      time: f.mtime.toISOString().split('T')[0],
      status: timeStr
    };
  });
}

function getMemoryStats() {
  const memoryPath = path.join(WORKSPACE, '.claude', 'projects', 'D--OpenClaw-workspace', 'memory', 'MEMORY.md');
  const defaults = { used: 141, total: 158, entries: 0, health: 89 };

  if (!fs.existsSync(memoryPath)) {
    // Try alternative paths
    const altPaths = [
      path.join(WORKSPACE, '.claude', 'memory', 'MEMORY.md'),
      path.join(WORKSPACE, 'memory', 'MEMORY.md'),
    ];
    for (const p of altPaths) {
      if (fs.existsSync(p)) {
        return parseMemoryFile(p);
      }
    }
    return defaults;
  }

  return parseMemoryFile(memoryPath);
}

function parseMemoryFile(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split('\n');

    // Count entries/sections
    const headers = lines.filter(l => l.startsWith('## ')).length;
    const entries = lines.filter(l => l.startsWith('| ')).length;

    // Estimate usage based on file size
    const sizeKB = Buffer.byteLength(content, 'utf8') / 1024;
    const total = 200; // ~200KB reasonable limit
    const used = Math.min(Math.round(sizeKB * 0.8), total);
    const health = Math.round((1 - used / total) * 100);

    return {
      used,
      total,
      entries: headers + entries,
      health: Math.max(health, 70)
    };
  } catch {
    return { used: 141, total: 158, entries: 12, health: 89 };
  }
}

const STALE_THRESHOLD_DAYS = 30;
const LAST_STALE_PUSH_FILE = path.join(__dirname, '.last_stale_push');

function checkAndPushStaleProjects(projects) {
  const sckey = process.env.SERVERCHAN_SCKEY || process.env.SCKEY;
  if (!sckey) return;

  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - STALE_THRESHOLD_DAYS);
  const stale = projects.filter(p => {
    if (!p.lastActive) return false;
    return new Date(p.lastActive) < cutoff;
  });

  if (stale.length === 0) return;

  // Avoid duplicate pushes within same day (file-based)
  const today = new Date().toISOString().split('T')[0];
  try {
    if (fs.existsSync(LAST_STALE_PUSH_FILE)) {
      const lastPush = fs.readFileSync(LAST_STALE_PUSH_FILE, 'utf8').trim();
      if (lastPush === today) {
        console.log(`[stale] Already pushed today (${today}), skipping`);
        return;
      }
    }
  } catch (e) {}

  const lines = stale.map(p => `• ${p.name}（${p.lastActive}）`).join('\n');
  const desp = `共 ${stale.length} 个项目超过 ${STALE_THRESHOLD_DAYS} 天无更新\n\n${lines}`;
  const url = `https://sc.ftqq.com/${sckey}.send?text=${encodeURIComponent('🔴 项目失活提醒')}&desp=${encodeURIComponent(desp)}`;

  try {
    require('https').get(url, () => {
      fs.writeFileSync(LAST_STALE_PUSH_FILE, today);
      console.log(`[stale] Pushed ${stale.length} stale projects to Server酱`);
    }).on('error', e => { console.error('[stale] Push failed:', e.message); });
  } catch (e) {
    console.error('[stale] Push failed:', e.message);
  }
}

function generateData() {
  const data = {
    generated: new Date().toISOString(),
    projects: getProjects(),
    submodules: getSubmodules(),
    sessions: getRecentSessions(),
    memory: getMemoryStats(),
    stats: {
      totalProjects: fs.existsSync(path.join(WORKSPACE, '80-PROJECTS'))
        ? fs.readdirSync(path.join(WORKSPACE, '80-PROJECTS')).filter(f => !f.startsWith('10-')).length
        : 0,
      submodules: 4,
      gitHooks: 4
    }
  };

  // Atomic write: temp file + rename
  const tempFile = OUTPUT + '.tmp';
  fs.writeFileSync(tempFile, JSON.stringify(data, null, 2));
  fs.renameSync(tempFile, OUTPUT);
  console.log(`Dashboard data generated: ${OUTPUT}`);
  console.log(`- Projects: ${data.projects.length}`);
  console.log(`- Submodules: ${data.submodules.length}`);
  console.log(`- Sessions: ${data.sessions.length}`);
  console.log(`- Tech stacks: ${[...new Set(data.projects.map(p => p.meta))].join(', ')}`);

  // Stale project push (Server酱)
  checkAndPushStaleProjects(data.projects);
}

generateData();
