/**
 * generate-changelog.mjs — Generates workspace CHANGELOG from git logs
 * Run: node scripts/generate-changelog.mjs
 */

import { readdirSync } from 'fs';
import { resolve, join } from 'path';
import { execSync } from 'child_process';

const ROOT = resolve('D:/OpenClaw/workspace/80-PROJECTS');

const dirs = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.startsWith('.') && d.name !== 'node_modules')
  .map(d => join(ROOT, d.name));

console.log('\n# Workspace Changelog\n');
console.log(`_Generated ${new Date().toISOString().slice(0, 10)}_\n`);

for (const dir of dirs) {
  const name = dir.replace(ROOT, '').replace(/\\/g, '/').replace(/^\//, '');
  let hasGit = false;
  try {
    execSync('git rev-parse --git-dir', { cwd: dir, stdio: 'ignore' });
    hasGit = true;
  } catch {}

  if (!hasGit) continue;

  try {
    const out = execSync(
      `git log --oneline -10`,
      { cwd: dir, encoding: 'utf8', maxBuffer: 64 * 1024 }
    );
    const lines = out.trim().split('\n').filter(Boolean);
    if (lines.length === 0) continue;
    console.log(`## ${name}\n`);
    for (const line of lines) {
      console.log(`- ${line}`);
    }
    console.log('');
  } catch {}
}
