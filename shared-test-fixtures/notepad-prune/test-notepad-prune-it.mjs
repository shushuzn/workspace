#!/usr/bin/env node
/**
 * IT for notepad-prune.mjs — end-to-end smoke test
 */
import { execSync } from 'child_process';

const SCRIPT = 'D:/OpenClaw/workspace/shared/notepad-prune.mjs';

// Test: script runs without error
let output = '';
let exitCode = 0;
try {
  output = execSync(`node "${SCRIPT}"`, { encoding: 'utf8', timeout: 5000 });
} catch (e) {
  output = (e.stdout || '') + (e.stderr || '');
  exitCode = e.status || 1;
}
const ok1 = exitCode === 0;
console.log(`[IT] exit code 0: ${ok1 ? 'PASS' : 'FAIL'}`);

// Test: output mentions notepad-prune
const ok2 = output.includes('[notepad-prune]');
console.log(`[IT] output has prefix: ${ok2 ? 'PASS' : 'FAIL'}`);

const allPass = ok1 && ok2;
console.log(allPass ? '\n[IT ALL PASS]' : '\n[IT FAIL]');
process.exit(allPass ? 0 : 1);
