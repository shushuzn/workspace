/**
 * session-report.mjs — Session 生产力报表
 *
 * 用法:
 *   node scripts/session-report.mjs
 *
 * 输出:
 *   .omc/sessions/{date}/{sessionId}/report.json
 *   终端展示报表
 */

import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const WORKSPACE = path.join(__dirname, '..');
const SESSION_ID = path.basename(process.env.TEMP || '/tmp').replace(/[^\w-]/g, '') || 'unknown';
const TODAY = new Date().toISOString().split('T')[0].replace(/-/g, '');

function getSessionDir() {
  const dir = path.join(WORKSPACE, '.omc', 'sessions', TODAY, SESSION_ID);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  return dir;
}

function getGitStats() {
  try {
    const today = new Date().toISOString().split('T')[0];
    const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0];
    const range = `${yesterday}..${today}`;

    const log = execSync(`git log --pretty=format:"%h|%s|%an" --since="${yesterday} 23:59:59" --until="${today} 23:59:59"`, {
      cwd: WORKSPACE,
      encoding: 'utf8',
      timeout: 5000,
    }).trim();

    const commits = log ? log.split('\n').filter(Boolean) : [];
    const files = execSync(`git diff --name-only ${range}`, {
      cwd: WORKSPACE,
      encoding: 'utf8',
      timeout: 5000,
    }).trim().split('\n').filter(Boolean);

    return { commitCount: commits.length, commits, filesChanged: [...new Set(files)].slice(0, 20) };
  } catch {
    return { commitCount: 0, commits: [], filesChanged: [] };
  }
}

function getIdeaStats() {
  try {
    const poolFile = path.join(WORKSPACE, '.omc', 'innovation', 'ideas.md');
    if (!fs.existsSync(poolFile)) return { total: 0, added: 0, scored: 0, advanced: 0 };
    const today = new Date().toISOString().slice(0, 10).replace(/-/g, '');
    const raw = fs.readFileSync(poolFile, 'utf8');
    const lines = raw.split('\n');
    let total = 0, added = 0, scored = 0, advanced = 0;
    for (const line of lines) {
      const m = line.match(/^-\s*\[(\d{8})\]\s*(\w+)/);
      if (!m) continue;
      total++;
      if (m[1] === today) added++;
      if (line.includes('[score:')) scored++;
      if (['proposal','running','shipped'].includes(m[2])) advanced++;
    }
    return { total, added, scored, advanced };
  } catch {
    return { total: 0, added: 0, scored: 0, advanced: 0 };
  }
}

function getMemoryProjects() {
  try {
    const memoryFile = 'C:/Users/adm/.claude/projects/D--OpenClaw-workspace/memory/MEMORY.md';
    if (!fs.existsSync(memoryFile)) return [];
    const raw = fs.readFileSync(memoryFile, 'utf8');
    const lines = raw.split('\n');
    let inTable = false, active = 0;
    for (const line of lines) {
      if (line.includes('### Active Projects')) { inTable = true; continue; }
      if (inTable && line.startsWith('### ')) break;
      if (inTable && line.startsWith('|') && !line.includes('---') && line.includes('|')) active++;
    }
    return [active];
  } catch {
    return [];
  }
}

function main() {
  const sessionDir = getSessionDir();
  const reportFile = path.join(sessionDir, 'report.json');

  const git = getGitStats();
  const idea = getIdeaStats();
  const activeCount = getMemoryProjects();
  const sessionStart = process.env.SESSION_START || new Date().toISOString();

  const report = {
    sessionId: SESSION_ID,
    generatedAt: new Date().toISOString(),
    sessionStart,
    duration: Math.round((Date.now() - new Date(sessionStart).getTime()) / 60000) + 'min',
    git: {
      commits: git.commitCount,
      filesChanged: git.filesChanged.length,
      topFiles: git.filesChanged.slice(0, 5),
    },
    ideas: {
      total: idea.total,
      addedThisSession: idea.added,
      scored: idea.scored,
      advanced: idea.advanced,
    },
    activeProjects: activeCount[0] || 0,
  };

  fs.writeFileSync(reportFile, JSON.stringify(report, null, 2), 'utf8');

  // Terminal output
  console.log('\n📊 Session 生产力报表');
  console.log('═'.repeat(48));
  console.log(`  会话ID: ${SESSION_ID}`);
  console.log(`  持续: ${report.duration}`);
  console.log('─'.repeat(48));
  console.log(`  📝 Git 提交: ${git.commitCount} 次`);
  if (git.filesChanged.length > 0) {
    console.log(`  📄 变更文件: ${git.filesChanged.length} 个`);
    git.filesChanged.slice(0, 3).forEach(f => console.log(`     • ${f}`));
  }
  console.log('─'.repeat(48));
  console.log(`  💡 Idea 池: 共 ${idea.total} 条`);
  console.log(`     本次新增: ${idea.added} 条`);
  console.log(`     已评分: ${idea.scored} 条`);
  console.log(`     已推进: ${idea.advanced} 条`);
  console.log('─'.repeat(48));
  console.log(`  📁 Active Projects: ${activeCount[0] || '?'} 个`);
  console.log('═'.repeat(48));
  console.log(`  已保存: ${reportFile}\n`);

  // Monthly aggregation
  const monthDir = path.join(WORKSPACE, '.omc', 'sessions', String(TODAY).slice(0, 6));
  const monthlyFile = path.join(monthDir, 'monthly.json');
  if (!fs.existsSync(monthDir)) fs.mkdirSync(monthDir, { recursive: true });
  let monthly = [];
  if (fs.existsSync(monthlyFile)) {
    try { monthly = JSON.parse(fs.readFileSync(monthlyFile, 'utf8')); } catch { monthly = []; }
  }
  monthly.push({ sessionId: SESSION_ID, git: report.git, ideas: report.ideas, duration: report.duration });
  if (monthly.length > 30) monthly = monthly.slice(-30);
  try { fs.writeFileSync(monthlyFile, JSON.stringify(monthly, null, 2), 'utf8'); } catch {} // trim to last 30

  // Monthly summary
  const totalCommits = monthly.reduce((s, r) => s + (r.git?.commits || 0), 0);
  const totalIdeas = monthly.reduce((s, r) => s + (r.ideas?.addedThisSession || 0), 0);
  const avgDuration = monthly.reduce((s, r) => s + parseInt(r.duration || '0'), 0) / monthly.length;
  console.log(`📅 本月汇总（共 ${monthly.length} sessions）`);
  console.log(`   Git: ${totalCommits} 次提交 | Idea: ${totalIdeas} 条新增 | 均时长: ${Math.round(avgDuration)}min\n`);
}

main();
