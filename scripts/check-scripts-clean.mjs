/**
 * check-scripts-clean.mjs — Detects non-script garbage files in scripts/
 * Run: node scripts/check-scripts-clean.mjs
 */

import { readdirSync } from 'fs';
import { resolve } from 'path';

const SCRIPTS_DIR = resolve('D:/OpenClaw/workspace/scripts');

const allowed = new Set(['.mjs', '.js', '.cjs', '.ts']);
const files = readdirSync(SCRIPTS_DIR);

const issues = [];
for (const file of files) {
  const ext = file.slice(file.lastIndexOf('.'));
  if (!allowed.has(ext) && !file.startsWith('.')) {
    issues.push(file);
  }
}

if (issues.length === 0) {
  console.log(`\n  scripts/ directory is clean (${files.length} files)\n`);
} else {
  console.log(`\n  Garbage files in scripts/: ${issues.join(', ')}`);
  console.log(`  Run: rm scripts/${issues.join(' scripts/')}\n`);
}
