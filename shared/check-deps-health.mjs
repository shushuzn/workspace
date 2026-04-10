#!/usr/bin/env node
/**
 * check-deps-health.mjs
 * Checks dependency health for workspace projects
 * Verifies node_modules exists for each project with package.json
 * With --auto-fix: runs npm install for projects with missing node_modules
 * With --watch: continuously monitors dependencies
 */
import { existsSync, readdirSync, statSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';

const __DIR = dirname(fileURLToPath(import.meta.url));
const WORKSPACE = join(__DIR, '..');
const PROJECTS_DIR = join(WORKSPACE, '80-PROJECTS');

const AUTO_FIX = process.argv.includes('--auto-fix');
const WATCH_MODE = process.argv.includes('--watch');

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
console.log(`║  Dependency Health Check${AUTO_FIX ? ' (auto-fix)' : ''}`.padEnd(47) + '║');
console.log('╚══════════════════════════════════════════════════╝\n');

let healthy = 0, missing = 0, fixed = 0;
for (const proj of projects.sort()) {
  const nm = join(PROJECTS_DIR, proj, 'node_modules');
  const hasNm = existsSync(nm);
  if (hasNm) {
    healthy++;
    console.log(`  ✓ ${proj.padEnd(40)} node_modules exists`);
  } else {
    missing++;
    console.log(`  ✗ ${proj.padEnd(40)} node_modules MISSING`);
    if (AUTO_FIX) {
      const projDir = join(PROJECTS_DIR, proj);
      console.log(`    → Running npm install in ${proj}...`);
      try {
        execSync('npm install', { cwd: projDir, stdio: 'pipe', timeout: 120000 });
        fixed++;
        console.log(`    ✓ npm install succeeded for ${proj}`);
      } catch (e) {
        console.log(`    ✗ npm install failed for ${proj}: ${e.message}`);
      }
    }
  }
}

console.log(`\n  Summary: ${healthy} healthy, ${missing} missing${AUTO_FIX ? `, ${fixed} fixed` : ''} (${projects.length} projects)`);
if (!AUTO_FIX && missing > 0) {
  console.log('\n  Run: node shared/check-deps-health.mjs --auto-fix to auto-install');
}

// Watch mode
if (WATCH_MODE) {
  console.log('\n  [watch] Monitoring node_modules changes...');
  console.log('  Press Ctrl+C to stop.\n');

  const checkInterval = 60000; // 60 seconds

  const check = () => {
    const prev = new Map();
    for (const proj of projects) {
      prev.set(proj, existsSync(join(PROJECTS_DIR, proj, 'node_modules')));
    }

    const interval = setInterval(() => {
      let changed = false;
      for (const proj of projects) {
        const curr = existsSync(join(PROJECTS_DIR, proj, 'node_modules'));
        if (curr !== prev.get(proj)) {
          prev.set(proj, curr);
          if (curr) {
            console.log(`  [watch] ✓ ${proj}: node_modules appeared`);
          } else {
            console.error(`  [watch] ✗ ${proj}: node_modules removed`);
          }
          changed = true;
        }
      }
      if (!changed) {
        process.stdout.write('.'); // heartbeat
      }
    }, checkInterval);

    process.on('SIGINT', () => {
      clearInterval(interval);
      console.log('\n  [watch] stopped');
      process.exit(0);
    });
  };

  check();
}
