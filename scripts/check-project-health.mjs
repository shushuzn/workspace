#!/usr/bin/env node
/**
 * scripts/check-project-health.mjs
 * Scans 80-PROJECTS, reports package.json scripts completeness + git status health.
 * Usage: node scripts/check-project-health.mjs [--json]
 */
import { readFileSync, readdirSync } from 'fs';
import { join, resolve } from 'path';
import { execSync } from 'child_process';

const WORKSPACE = resolve('D:/OpenClaw/workspace/80-PROJECTS');
const NEED_SCRIPTS = ['dev', 'build', 'test', 'lint'];
const EXCLUDES = ['.', 'node_modules', 'ARCHIVED', '10-', '_']; // skip dotdirs, archived, temp prefixes

const jsonMode = process.argv.includes('--json');

function getGitStatus(dir) {
  try {
    const out = execSync('git status --porcelain', { cwd: dir, encoding: 'utf-8', timeout: 5000 });
    if (!out.trim()) return 'clean';
    const lines = out.trim().split('\n');
    const hasModified = lines.some(l => l.match(/^[ MADR]/));
    const hasUntracked = lines.some(l => l.match(/^\?\?/));
    if (hasModified && hasUntracked) return 'mixed';
    if (hasModified) return 'modified';
    if (hasUntracked) return 'untracked';
    return 'mixed';
  } catch {
    return 'no-git';
  }
}

function getScriptsHealth(pkg) {
  const scripts = Object.keys(pkg.scripts || {});
  const present = NEED_SCRIPTS.filter(s => scripts.includes(s));
  const missing = NEED_SCRIPTS.filter(s => !scripts.includes(s));
  return { present, missing, score: present.length, total: NEED_SCRIPTS.length };
}

const dirs = readdirSync(WORKSPACE).filter(d =>
  !EXCLUDES.some(e => d.startsWith(e))
);

const results = [];
for (const dir of dirs) {
  const projPath = join(WORKSPACE, dir);
  const pkgPath = join(projPath, 'package.json');
  let scriptsHealth = { present: [], missing: [...NEED_SCRIPTS], score: 0, total: NEED_SCRIPTS.length };
  let gitStatus = 'no-git';
  let name = dir;

  try {
    const pkg = JSON.parse(readFileSync(pkgPath, 'utf8'));
    scriptsHealth = getScriptsHealth(pkg);
    name = pkg.name || dir;
  } catch { /* no package.json */ }

  try {
    gitStatus = getGitStatus(projPath);
  } catch { /* no git */ }

  // Health score: scripts (50%) + git (50%)
  const scriptScore = scriptsHealth.score / scriptsHealth.total;
  const gitScore = gitStatus === 'clean' ? 1 : gitStatus === 'no-git' ? 0 : 0.5;
  const healthScore = Math.round((scriptScore * 0.5 + gitScore * 0.5) * 100);

  results.push({ dir, name, scriptsHealth, gitStatus, healthScore });
}

results.sort((a, b) => b.healthScore - a.healthScore);

if (jsonMode) {
  console.log(JSON.stringify(results, null, 2));
} else {
  console.log(`\n=== Project Health Report ===`);
  console.log(`${'Project'.padEnd(26)} ${'Scripts'.padEnd(10)} ${'Git'.padEnd(10)} ${'Health'}`);
  console.log('-'.repeat(60));
  for (const r of results) {
    const missingStr = r.scriptsHealth.missing.length > 0 ? r.scriptsHealth.missing.join(',') : 'OK';
    console.log(`${r.name.padEnd(26)} ${missingStr.padEnd(10)} ${r.gitStatus.padEnd(10)} ${r.healthScore}%`);
  }
  const healthy = results.filter(r => r.healthScore >= 80).length;
  const noGit = results.filter(r => r.gitStatus === 'no-git').length;
  const missingScripts = results.filter(r => r.scriptsHealth.missing.length > 0).length;
  console.log(`\nTotal: ${results.length} | Healthy(≥80%): ${healthy} | No git: ${noGit} | Missing scripts: ${missingScripts}`);
}
