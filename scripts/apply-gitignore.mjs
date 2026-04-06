/**
 * apply-gitignore.mjs — Copies workspace .gitignore to projects missing it
 * Run: node scripts/apply-gitignore.mjs [project-name]
 * Without args: applies to all missing projects
 */

import { copyFileSync, accessSync } from 'fs';
import { readdirSync } from 'fs';
import { resolve, join } from 'path';

const ROOT = resolve('D:/OpenClaw/workspace/80-PROJECTS');
const templateSrc = resolve('D:/OpenClaw/workspace/80-PROJECTS/.gitignore');

function hasGitignore(dir) {
  try { accessSync(join(dir, '.gitignore')); return true; } catch { return false; }
}

const args = process.argv.slice(2);
let targets;

if (args.length > 0) {
  targets = args.map(a => join(ROOT, a));
} else {
  targets = readdirSync(ROOT, { withFileTypes: true })
    .filter(d => d.isDirectory() && !d.name.startsWith('.') && d.name !== 'node_modules')
    .map(d => join(ROOT, d.name))
    .filter(d => !hasGitignore(d));
}

let applied = 0;
for (const dir of targets) {
  const rel = dir.replace(ROOT, '').replace(/\\/g, '/').replace(/^\//, '');
  try {
    copyFileSync(templateSrc, join(dir, '.gitignore'));
    console.log(`  ✓ ${rel}`);
    applied++;
  } catch (e) {
    console.log(`  ✗ ${rel}: ${e.message}`);
  }
}
console.log(`\n  ${applied}/${targets.length} .gitignore applied\n`);
