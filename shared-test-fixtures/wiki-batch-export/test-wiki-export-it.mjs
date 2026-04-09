#!/usr/bin/env node
/**
 * IT for wiki-batch-export.mjs — end-to-end smoke test
 */
import { execSync } from 'child_process';
import { existsSync, unlinkSync, rmdirSync } from 'fs';

const SCRIPT = 'D:/OpenClaw/workspace/shared/wiki-batch-export.mjs';
const OUTPUT = 'D:/OpenClaw/workspace/wiki-export-it-test';

// Clean up first
try {
  const files = ['D:/OpenClaw/workspace/wiki-export-it-test/math-burau-lyapunov-指数.html'];
  for (const f of files) {
    try { unlinkSync(f); } catch {}
    try { rmdirSync('D:/OpenClaw/workspace/wiki-export-it-test'); } catch {}
  }
} catch {}

// Test: script runs without error
let output = '';
let exitCode = 0;
try {
  output = execSync(`node "${SCRIPT}" --format=html --output="${OUTPUT}"`, { encoding: 'utf8', timeout: 30000 });
} catch (e) {
  output = (e.stdout || '') + (e.stderr || '');
  exitCode = e.status || 1;
}
const ok1 = exitCode === 0;
console.log(`[IT] exit code 0: ${ok1 ? 'PASS' : 'FAIL'}`);

const ok2 = output.includes('[wiki-batch-export]');
console.log(`[IT] output prefix: ${ok2 ? 'PASS' : 'FAIL'}`);

const ok3 = output.includes('Done:');
console.log(`[IT] done message: ${ok3 ? 'PASS' : 'FAIL'}`);

const allPass = ok1 && ok2 && ok3;
console.log(allPass ? '\n[IT ALL PASS]' : '\n[IT FAIL]');
process.exit(allPass ? 0 : 1);
