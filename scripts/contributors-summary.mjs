/**
 * contributors-summary.mjs — Summarizes top contributors per project
 * Run: node scripts/contributors-summary.mjs [--limit 5]
 */

import { readdirSync } from 'fs';
import { resolve, join } from 'path';
import { execSync } from 'child_process';

const ROOT = resolve('D:/OpenClaw/workspace/80-PROJECTS');
const LIMIT = parseInt(process.argv.find(a => a.startsWith('--limit='))?.split('=')[1] || '5');

const dirs = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.startsWith('.') && d.name !== 'node_modules')
  .map(d => join(ROOT, d.name));

console.log(`\n  Top ${LIMIT} contributors per project:\n`);

for (const dir of dirs) {
  const name = dir.replace(ROOT, '').replace(/\\/g, '/').replace(/^\//, '');
  const gitDir = join(dir, '.git');
  let hasGit = false;
  try {
    execSync('git rev-parse --git-dir', { cwd: dir, stdio: 'ignore' });
    hasGit = true;
  } catch {}

  if (!hasGit) {
    console.log(`  ${name}: (no git repo)`);
    continue;
  }

  try {
    const out = execSync(
      `git log --format="%an" -n 200`,
      { cwd: dir, encoding: 'utf8', maxBuffer: 1024 * 1024 }
    );
    const counts = {};
    for (const line of out.split('\n')) {
      const author = line.trim();
      if (author) counts[author] = (counts[author] || 0) + 1;
    }
    const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, LIMIT);
    const total = Object.values(counts).reduce((s, n) => s + n, 0);
    console.log(`  ${name} (${total} commits):`);
    for (const [author, count] of sorted) {
      console.log(`    ${author}: ${count}`);
    }
  } catch {
    console.log(`  ${name}: (error reading git log)`);
  }
}
console.log('');
