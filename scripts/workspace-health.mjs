/**
 * workspace-health.mjs
 * Prints + exports project health matrix (CSV + README badge update).
 * Run: node scripts/workspace-health.mjs [--csv [path]] [--badges]
 *
 * Health dimensions:
 *   activity: days since last active (0=active today, higher=worse)
 *   dependency_health: 1-(outdated/total) or null if no deps
 *   ci_presence: 1 if .github/workflows exists, else 0
 *   readme_quality: README exists + has >100 chars + has ## heading
 */

import { readFileSync, writeFileSync, existsSync, readdirSync } from 'fs';
import { join, resolve } from 'path';
import { execSync } from 'child_process';

const DRY = process.argv.includes('--dry-run');
const DO_CSV = process.argv.includes('--csv');
const DO_BADGES = process.argv.includes('--badges');
const CSV_PATH = (() => {
  const i = process.argv.indexOf('--csv');
  return i >= 0 && process.argv[i + 1] && !process.argv[i + 1].startsWith('--')
    ? process.argv[i + 1]
    : join(process.argv[1] || '.', 'project-health-matrix.csv');
})();

const MEMORY_PATH = 'C:/Users/adm/.claude/projects/D--OpenClaw-workspace/memory/MEMORY.md';
const WORKSPACE = resolve('D:/OpenClaw/workspace');

function execGit(cmd, dir) {
  try {
    return execSync(cmd, { cwd: dir, encoding: 'utf8', timeout: 5000, stdio: ['ignore', 'pipe', 'pipe'] }).trim();
  } catch {
    return '?';
  }
}

function daysSince(dateStr) {
  if (!dateStr || !/^\d{4}-\d{2}-\d{2}$/.test(dateStr.trim())) return null;
  const parts = dateStr.trim().split('-').map(Number);
  const last = new Date(parts[0], parts[1] - 1, parts[2]);
  const now = new Date();
  return Math.floor((now.getTime() - last.getTime()) / 86400000);
}

const memory = readFileSync(MEMORY_PATH, 'utf8');
const lines = memory.split('\n');

// Find Active Projects table header
let headerIdx = lines.findIndex(l => l.startsWith('| Project |'));
if (headerIdx === -1) { console.error('Active Projects table not found'); process.exit(1); }

let sepIdx = headerIdx;
while (sepIdx < lines.length && !lines[sepIdx].match(/\|[-]+\|/)) sepIdx++;

const nextTableIdx = lines.slice(sepIdx + 1).findIndex(l => l.startsWith('| Archive |'));

const rows = lines.slice(sepIdx + 1, nextTableIdx > 0 ? sepIdx + 1 + nextTableIdx : undefined)
  .filter(l => l.startsWith('| '));

// ── CSV header ────────────────────────────────────────────────────────────────
const CSV_HEADER = 'project,path,last_active,days_since_active,activity_score,deps_total,deps_outdated,dep_health_score,has_ci,readme_len,readme_quality,overall_score';

console.log(`\n${'Project'.padEnd(28)} ${'Active'.padEnd(10)} ${'Days'.padEnd(5)} ${'Act'.padEnd(4)} ${'Dep'.padEnd(4)} ${'CI'.padEnd(3)} ${'RDMe'.padEnd(5)} ${'Score'.padEnd(6)} ${'Branch'.padEnd(12)} Status`);
console.log('-'.repeat(88));

let count = 0;
const csvRows = [];

for (const row of rows) {
  const cols = row.split('|').map(c => c.trim());
  if (cols.length < 6) continue;
  const name = cols[1];
  const relPath = cols[2];
  const tech = cols[3];
  const lastActive = cols[4];
  if (!name || !relPath) continue;

  const fullPath = join(WORKSPACE, relPath);

  // Branch + sync status
  let branch = '?';
  let status = '';
  try {
    branch = execGit('git branch --show-current', fullPath) || execGit('git rev-parse --short HEAD', fullPath);
    const tracking = execGit('git rev-list --left-right --count @{u}...HEAD', fullPath);
    if (tracking && tracking !== '?' && tracking.includes('\t')) {
      const [behind, ahead] = tracking.split('\t').map(n => parseInt(n) || 0);
      if (ahead > 0) status += `+${ahead}`;
      if (behind > 0) status += `-${behind}`;
      if (!status) status = 'synced';
    } else {
      status = 'synced';
    }
  } catch {
    branch = 'n/a';
    status = 'n/a';
  }

  // Activity score (0=active today, 30+=dead)
  const days = daysSince(lastActive);
  const actScore = days === null ? null : Math.max(0, Math.min(100, Math.round(100 - days * 3.3)));

  // Dependency health
  const pkgPath = join(fullPath, 'package.json');
  let depTotal = 0, depOutdated = 0;
  if (existsSync(pkgPath)) {
    try {
      const pkg = JSON.parse(readFileSync(pkgPath, 'utf8'));
      const deps = { ...pkg.dependencies, ...pkg.devDependencies };
      depTotal = Object.keys(deps).length;
    } catch {}
  }
  const depScore = depTotal > 0 ? Math.round(((depTotal - depOutdated) / depTotal) * 100) : null;

  // CI presence
  const hasCI = existsSync(join(fullPath, '.github', 'workflows')) ? 1 : 0;

  // README quality
  let readmeLen = 0;
  let hasReadme = false;
  for (const n of ['README.md', 'readme.md', 'CLAUDE.md']) {
    const rp = join(fullPath, n);
    if (existsSync(rp)) {
      const content = readFileSync(rp, 'utf8');
      readmeLen = content.length;
      hasReadme = content.includes('##');
      break;
    }
  }
  const readmeScore = !hasReadme ? 0 : readmeLen < 200 ? 50 : readmeLen < 1000 ? 80 : 100;

  // Overall (weighted average)
  const components = [actScore, depScore, null, readmeScore].filter(s => s !== null);
  const ciComp = hasCI * 100;
  const overall = components.length > 0
    ? Math.round((components.reduce((a, b) => a + b, 0) + ciComp) / (components.length + 1))
    : (components.length > 0 ? Math.round(components.reduce((a, b) => a + b, 0) / components.length) : null);

  csvRows.push([
    name,
    relPath,
    lastActive || '',
    days !== null ? String(days) : '',
    actScore !== null ? String(actScore) : '',
    String(depTotal),
    String(depOutdated),
    depScore !== null ? String(depScore) : '',
    String(hasCI),
    String(readmeLen),
    String(readmeScore),
    overall !== null ? String(overall) : '',
  ].join(','));

  // Print row
  const nameOut = name.length > 28 ? name.slice(0, 25) + '...' : name.padEnd(28);
  const lastOut = (lastActive || '').padEnd(10);
  const daysOut = days !== null ? String(days).padEnd(5) : ' n/a '.padEnd(5);
  const actOut = actScore !== null ? String(actScore).padEnd(4) : ' n/a '.padEnd(4);
  const depOut = depScore !== null ? String(depScore).padEnd(4) : ' n/a '.padEnd(4);
  const ciOut = hasCI ? 'yes'.padEnd(4) : 'no'.padEnd(4);
  const rdmeOut = readmeScore > 0 ? (readmeScore >= 100 ? 'rich'.padEnd(5) : 'thin'.padEnd(5)) : 'none'.padEnd(5);
  const scoreOut = overall !== null ? String(overall).padEnd(6) : ' n/a '.padEnd(6);
  const branchOut = (branch || '').padEnd(12);
  console.log(`${nameOut} ${lastOut} ${daysOut} ${actOut} ${depOut} ${ciOut} ${rdmeOut} ${scoreOut} ${branchOut} ${status}`);
  count++;
}

console.log(`\n${count} projects scanned`);

// ── CSV export ────────────────────────────────────────────────────────────────
if (DO_CSV) {
  const csv = [CSV_HEADER, ...csvRows].join('\n');
  if (!DRY) writeFileSync(CSV_PATH, csv, 'utf8');
  console.log(`CSV: ${DRY ? '[dry-run] ' : ''}${CSV_PATH}`);
}

// ── README badge update ─────────────────────────────────────────────────────
if (DO_BADGES) {
  const REPO = 'OpenClaw';
  let updated = 0;
  for (const row of rows) {
    const cols = row.split('|').map(c => c.trim());
    if (cols.length < 3) continue;
    const name = cols[1];
    const relPath = cols[2];
    if (!name || !relPath) continue;
    const fullPath = join(WORKSPACE, relPath);
    const readmePath = join(fullPath, 'README.md');
    if (!existsSync(readmePath)) continue;

    // Find overall score for this project
    const csvRow = csvRows.find(r => r.startsWith(name + ','));
    if (!csvRow) continue;
    const score = parseInt(csvRow.split(',')[11]) || 0;
    const badgeColor = score >= 80 ? 'brightgreen' : score >= 60 ? 'yellow' : score >= 40 ? 'orange' : 'red';
    const badge = `[![Health](https://img.shields.io/badge/workspace--health-${score}-${badgeColor})](https://github.com/${REPO}/${name}/actions/workflows)`;

    try {
      let content = readFileSync(readmePath, 'utf8');
      const badgeRe = /!\[Health\]\(https:\/\/img\.shields\.io\/badge\/workspace--health-\d+/;
      if (badgeRe.test(content)) {
        content = content.replace(badgeRe, badge);
      } else {
        const lines = content.split('\n');
        const titleIdx = lines.findIndex(l => l.startsWith('# '));
        if (titleIdx >= 0) lines.splice(titleIdx + 1, 0, `\n${badge}\n`);
        content = lines.join('\n');
      }
      if (!DRY) writeFileSync(readmePath, content, 'utf8');
      updated++;
    } catch {}
  }
  console.log(`${DRY ? '[dry-run] ' : ''}Updated ${updated} README badges`);
}
