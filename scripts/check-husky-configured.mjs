/**
 * check-husky-configured.mjs — Reports which projects have husky pre-commit hook configured
 * Run: node scripts/check-husky-configured.mjs
 */

import { readdirSync, statSync } from 'fs';
import { resolve, join } from 'path';

const ROOT = resolve('D:/OpenClaw/workspace/80-PROJECTS');

const dirs = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.startsWith('.') && d.name !== 'node_modules')
  .map(d => join(ROOT, d.name));

const configured = [];
const unconfigured = [];

for (const dir of dirs) {
  const rel = dir.replace(ROOT, '').replace(/\\/g, '/').replace(/^\//, '');
  let hasHook = false;
  try { statSync(join(dir, '.husky', 'pre-commit')); hasHook = true; } catch {}
  if (hasHook) {
    configured.push(rel);
  } else {
    unconfigured.push(rel);
  }
}

console.log(`\n  Husky configured: ${configured.length} projects`);
if (configured.length > 0) {
  configured.forEach(p => console.log(`  ✓ ${p}`));
}
console.log(`\n  Husky NOT configured: ${unconfigured.length} projects`);
unconfigured.forEach(p => console.log(`  - ${p}`));
console.log('');
