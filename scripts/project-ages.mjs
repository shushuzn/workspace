/**
 * project-ages.mjs — Shows project activity timeline by last modified time
 * Run: node scripts/project-ages.mjs
 */

import { readdirSync, statSync } from 'fs';
import { resolve, join } from 'path';

const ROOT = resolve('D:/OpenClaw/workspace/80-PROJECTS');

const dirs = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.startsWith('.') && d.name !== 'node_modules')
  .map(d => ({ name: d.name, path: join(ROOT, d.name) }));

const projects = dirs.map(({ name, path }) => {
  try {
    const stats = statSync(join(path, 'package.json'));
    return { name, mtime: stats.mtime };
  } catch {
    try {
      const stats = statSync(path);
      return { name, mtime: stats.mtime };
    } catch {
      return { name, mtime: new Date(0) };
    }
  }
});

projects.sort((a, b) => b.mtime - a.mtime);

console.log('\n  Project Activity Timeline (most recent first):\n');
for (const { name, mtime } of projects) {
  const age = Date.now() - mtime.getTime();
  const days = Math.floor(age / 86400000);
  const date = mtime.toISOString().slice(0, 10);
  const label = days === 0 ? 'today' : days === 1 ? '1 day ago' : `${days} days ago`;
  console.log(`    ${date}  ${label.padEnd(12)}  ${name}`);
}
console.log(`\n  ${projects.length} projects\n`);
