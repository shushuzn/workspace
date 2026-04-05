/**
 * update-readme-badges.mjs
 * Adds/updates GitHub Actions CI badges in README.md for projects with workflows.
 * Run: node scripts/update-readme-badges.mjs [--dry-run]
 */

import { readFileSync, writeFileSync, readdirSync, existsSync } from 'fs';
import { join, resolve } from 'path';

const DRY = process.argv.includes('--dry-run');
const WORKSPACE = resolve('D:/OpenClaw/workspace/80-PROJECTS');
const dirs = readdirSync(WORKSPACE).filter(d => !d.startsWith('.'));

const REPO = 'OpenClaw'; // adjust if different

let updated = 0;
for (const dir of dirs) {
  const wfDir = join(WORKSPACE, dir, '.github', 'workflows');
  let wfs = [];
  try { wfs = readdirSync(wfDir).filter(f => f.endsWith('.yml') || f.endsWith('.yaml')); } catch {}

  for (const wf of wfs) {
    const badge = `[![CI](https://github.com/${REPO}/${dir}/actions/workflows/${wf}/badge.svg)](https://github.com/${REPO}/${dir}/actions/workflows/${wf})`;
    const readmePath = join(WORKSPACE, dir, 'README.md');
    try {
      let content = readFileSync(readmePath, 'utf8');
      const badgeRe = new RegExp(`!\\[CI\\]\\(https://github\\.com/${REPO}/${dir}/actions/workflows/${wf}/badge\\.svg\\)`);
      if (badgeRe.test(content)) continue;

      // Insert after first heading or at top
      const lines = content.split('\n');
      const afterTitle = lines.findIndex(l => l.startsWith('# '));
      if (afterTitle >= 0) {
        lines.splice(afterTitle + 1, 0, `\n${badge}\n`);
      } else {
        lines.unshift(`\n${badge}\n`);
      }
      const newContent = lines.join('\n');
      if (!DRY) writeFileSync(readmePath, newContent, 'utf8');
      process.stderr.write(`${DRY ? '[dry-run] ' : ''}added badge to ${dir}/README.md (${wf})\n`);
      updated++;
    } catch {
      // no README
    }
  }
}

process.stderr.write(`\n${DRY ? 'dry-run: ' : ''}updated ${updated} badge(s)\n`);
