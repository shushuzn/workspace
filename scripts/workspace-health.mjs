/**
 * workspace-health.mjs
 * Prints a health overview of all projects in MEMORY.md Active Projects table.
 * Run: node scripts/workspace-health.mjs
 */

import { readFileSync } from 'fs';
import { join, resolve } from 'path';
import { execSync } from 'child_process';

const MEMORY_PATH = 'C:/Users/adm/.claude/projects/D--OpenClaw-workspace/memory/MEMORY.md';
const WORKSPACE = resolve('D:/OpenClaw/workspace');

function execGit(cmd, dir) {
  try {
    return execSync(cmd, { cwd: dir, encoding: 'utf8', timeout: 5000, stdio: ['ignore', 'pipe', 'pipe'] }).trim();
  } catch {
    return '?';
  }
}

const memory = readFileSync(MEMORY_PATH, 'utf8');
const lines = memory.split('\n');

// Find Active Projects table header
let headerIdx = lines.findIndex(l => l.startsWith('| Project |'));
if (headerIdx === -1) { console.error('Active Projects table not found'); process.exit(1); }

// Find separator
let sepIdx = headerIdx;
while (sepIdx < lines.length && !lines[sepIdx].match(/\|[-]+\|/)) sepIdx++;

// Stop at next table (Archived)
const nextTableIdx = lines.slice(sepIdx + 1).findIndex(l => l.startsWith('| Archive |'));

const rows = lines.slice(sepIdx + 1, nextTableIdx > 0 ? sepIdx + 1 + nextTableIdx : undefined)
  .filter(l => l.startsWith('| '));

console.log(`\n${'Project'.padEnd(28)} ${'Tech'.padEnd(14)} ${'Active'.padEnd(10)} ${'Branch'.padEnd(12)} Status`);
console.log('-'.repeat(78));

let count = 0;
for (const row of rows) {
  const cols = row.split('|').map(c => c.trim());
  if (cols.length < 6) continue;
  // cols: [empty, name, path, tech, lastActive, ceiling, ...]
  const name = cols[1];
  const path = cols[2];
  const tech = cols[3];
  const lastActive = cols[4];
  if (!name || !path) continue;

  const fullPath = join(WORKSPACE, path);
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

  const nameOut = name.length > 28 ? name.slice(0, 25) + '...' : name.padEnd(28);
  const techOut = (tech || '').length > 14 ? tech.slice(0, 11) + '...' : (tech || '').padEnd(14);
  const lastOut = (lastActive || '').padEnd(10);
  const branchOut = (branch || '').padEnd(12);
  console.log(`${nameOut} ${techOut} ${lastOut} ${branchOut} ${status}`);
  count++;
}

console.log(`\n${count} projects scanned\n`);
