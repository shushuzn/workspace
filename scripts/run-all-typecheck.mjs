/**
 * run-all-typecheck.mjs
 * Parallel TypeScript type-checking across all TS projects with tsconfig.json.
 * Run: node scripts/run-all-typecheck.mjs
 */

import { execSync } from 'child_process';
import { globSync } from 'glob';
import { resolve } from 'path';

const WORKSPACE = resolve('D:/OpenClaw/workspace/80-PROJECTS');

const tsconfigs = globSync('*/tsconfig.json', { cwd: WORKSPACE });

console.log(`\nChecking ${tsconfigs.length} TypeScript project(s)...\n`);

const results = [];
for (const tc of tsconfigs) {
  const project = tc.replace('/tsconfig.json', '');
  const fullPath = resolve(WORKSPACE, tc.replace('/tsconfig.json', ''));
  try {
    execSync('npx tsc --noEmit', { cwd: fullPath, stdio: ['ignore', 'pipe', 'pipe'], timeout: 60000 });
    results.push({ project, status: 'PASS' });
  } catch (e) {
    const stderr = e.stderr?.toString() || '';
    const msg = stderr.includes('error TS') ? `FAIL (${(stderr.match(/error TS\d+:/g) || []).length} errors)` : 'FAIL';
    results.push({ project, status: msg });
    process.stderr.write(`${project}: ${msg}\n`);
  }
}

const pass = results.filter(r => r.status === 'PASS').length;
console.log(`\n${pass}/${tsconfigs.length} projects passed type check\n`);
process.exit(pass === tsconfigs.length ? 0 : 1);
