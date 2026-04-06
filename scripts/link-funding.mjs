/**
 * link-funding.mjs — Symlinks or copies .github/FUNDING.yml to projects missing it
 * Run: node scripts/link-funding.mjs [--dry-run]
 */

import { readdirSync, existsSync, copyFileSync, mkdirSync } from 'fs';
import { resolve, join } from 'path';

const ROOT = resolve('D:/OpenClaw/workspace/80-PROJECTS');
const TEMPLATE = resolve('D:/OpenClaw/workspace/.github/FUNDING.yml');

const args = process.argv.slice(2);
const dryRun = args.includes('--dry-run');

const dirs = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.startsWith('.') && d.name !== 'node_modules')
  .map(d => join(ROOT, d.name));

let linked = 0;
for (const dir of dirs) {
  const rel = dir.replace(ROOT, '').replace(/\\/g, '/').replace(/^\//, '');
  const ghDir = join(dir, '.github');
  const fundingPath = join(ghDir, 'FUNDING.yml');

  if (!existsSync(fundingPath)) {
    if (dryRun) {
      console.log(`  [dry-run] would link: ${rel}/.github/FUNDING.yml`);
    } else {
      if (!existsSync(ghDir)) mkdirSync(ghDir, { recursive: true });
      copyFileSync(TEMPLATE, fundingPath);
      console.log(`  + ${rel}/.github/FUNDING.yml`);
    }
    linked++;
  }
}

if (dryRun) {
  console.log(`\n  [dry-run] ${linked} project(s) need FUNDING.yml (not written)\n`);
} else {
  console.log(`\n  ${linked} FUNDING.yml file(s) created\n`);
}
