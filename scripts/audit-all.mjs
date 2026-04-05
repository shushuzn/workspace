/**
 * audit-all.mjs
 * Parallel npm audit across all projects with package.json.
 * Run: node scripts/audit-all.mjs
 */

import { execSync } from 'child_process';
import { globSync } from 'glob';
import { resolve } from 'path';

const WORKSPACE = resolve('D:/OpenClaw/workspace/80-PROJECTS');
const pkgs = globSync('*/package.json', { cwd: WORKSPACE });

console.log(`\nAuditing ${pkgs.length} project(s)...\n`);

const results = [];
for (const pkg of pkgs) {
  const project = pkg.replace('/package.json', '');
  const fullPath = resolve(WORKSPACE, pkg.replace('/package.json', ''));
  try {
    const out = execSync('npm audit --json', { cwd: fullPath, encoding: 'utf8', timeout: 60000, stdio: ['ignore', 'pipe', 'pipe'] });
    const data = JSON.parse(out);
    const totals = data.metadata?.vulnerabilities || {};
    const total = Object.values(totals).reduce((a, b) => a + b, 0);
    if (total > 0) {
      console.log(`${project}: ${total} vulnerabilities (C:${totals.critical||0} H:${totals.high||0} M:${totals.moderate||0} L:${totals.low||0})`);
    }
    results.push({ project, total });
  } catch (e) {
    const stderr = e.stderr?.toString() || '';
    if (stderr.includes('npm audit')) {
      console.log(`${project}: audit failed`);
    }
    results.push({ project, total: -1 });
  }
}

const vuln = results.filter(r => r.total > 0).length;
const done = results.filter(r => r.total >= 0).length;
console.log(`\n${done}/${pkgs.length} scanned  |  ${vuln} project(s) with vulnerabilities\n`);
