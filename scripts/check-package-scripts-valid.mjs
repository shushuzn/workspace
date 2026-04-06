/**
 * check-package-scripts-valid.mjs — Checks if npm scripts reference valid commands
 * Run: node scripts/check-package-scripts-valid.mjs
 */

import { readdirSync, readFileSync, existsSync } from 'fs';
import { resolve, join } from 'path';

const ROOT = resolve('D:/OpenClaw/workspace/80-PROJECTS');

const dirs = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.startsWith('.') && d.name !== 'node_modules')
  .map(d => join(ROOT, d.name));

const issues = [];
for (const dir of dirs) {
  const pkgPath = join(dir, 'package.json');
  const nodeModules = join(dir, 'node_modules');
  try {
    const pkg = JSON.parse(readFileSync(pkgPath, 'utf8'));
    const scripts = pkg.scripts || {};
    for (const [name, cmd] of Object.entries(scripts)) {
      if (!cmd || cmd.trim() === '') {
        issues.push({ dir: dir.replace(ROOT + '/', ''), script: name, issue: 'empty command' });
        continue;
      }
      // Extract first token (the command)
      const first = cmd.trim().split(/\s+/)[0];
      // Check if it's a local binary or file reference
      const isLocal = first.startsWith('./') || first.startsWith('../') || first.startsWith('/');
      if (isLocal) {
        const target = join(dir, first);
        if (!existsSync(target)) {
          issues.push({ dir: dir.replace(ROOT + '/', ''), script: name, issue: `missing: ${first}` });
        }
      }
      // For node_modules binaries, skip (npm validates these)
    }
  } catch {
    // skip non-JSON
  }
}

if (issues.length === 0) {
  console.log(`\n  All scripts valid across ${dirs.length} projects\n`);
} else {
  console.log(`\n  Script issues:`);
  for (const { dir, script, issue } of issues) {
    console.log(`  ✗ ${dir}/${script}: ${issue}`);
  }
  console.log(`\n  ${issues.length} issue(s)\n`);
}
