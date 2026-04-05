/**
 * check-outdated.mjs
 * Parallel npm outdated across all projects with package.json.
 * Run: node scripts/check-outdated.mjs
 */

import { execSync } from 'child_process';
import { globSync } from 'glob';
import { resolve } from 'path';

const WORKSPACE = resolve('D:/OpenClaw/workspace/80-PROJECTS');
const pkgs = globSync('*/package.json', { cwd: WORKSPACE });

console.log(`\nChecking ${pkgs.length} project(s)...\n`);

let hasUpdates = 0;

for (const pkg of pkgs) {
  const project = pkg.replace('/package.json', '');
  const fullPath = resolve(WORKSPACE, pkg.replace('/package.json', ''));
  try {
    const out = execSync('npm outdated --json', { cwd: fullPath, encoding: 'utf8', timeout: 60000, stdio: ['ignore', 'pipe', 'pipe'] });
    const data = JSON.parse(out);
    const entries = Object.entries(data);
    if (entries.length > 0) {
      console.log(`${project}:`);
      for (const [name, info] of entries) {
        console.log(`  ${name}: ${info.current} → ${info.latest} (${info.type})`);
      }
      hasUpdates++;
    }
  } catch {
    // no outdated deps
  }
}

console.log(`\n${hasUpdates} project(s) have outdated dependencies\n`);
