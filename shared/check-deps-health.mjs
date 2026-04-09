#!/usr/bin/env node
/**
 * check-deps-health.mjs
 * Checks dependency health for workspace projects
 * Verifies node_modules exists for each project with package.json
 */
import { existsSync, readdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const WORKSPACE = join(__DIR, '..');
const PROJECTS_DIR = join(WORKSPACE, '80-PROJECTS');

let projects = [];
try {
  projects = readdirSync(PROJECTS_DIR).filter(p => {
    try {
      return !p.startsWith('.') && !p.includes('ARCHIVED') && existsSync(join(PROJECTS_DIR, p, 'package.json'));
    } catch { return false; }
  });
} catch {
  console.error('Cannot read 80-PROJECTS directory');
  process.exit(1);
}

console.log('╔══════════════════════════════════════════════════╗');
console.log('║  Dependency Health Check                      ║');
console.log('╚══════════════════════════════════════════════════╝\n');

let healthy = 0, missing = 0;
for (const proj of projects.sort()) {
  const pkg = join(PROJECTS_DIR, proj, 'package.json');
  const nm = join(PROJECTS_DIR, proj, 'node_modules');
  const hasNm = existsSync(nm);
  if (hasNm) {
    healthy++;
    console.log(`  ✓ ${proj.padEnd(40)} node_modules exists`);
  } else {
    missing++;
    console.log(`  ✗ ${proj.padEnd(40)} node_modules MISSING`);
  }
}

console.log(`\n  Summary: ${healthy} healthy, ${missing} missing (${projects.length} projects)`);
if (missing > 0) {
  console.log('\n  Run: cd <project> && npm install');
}
console.log('');
