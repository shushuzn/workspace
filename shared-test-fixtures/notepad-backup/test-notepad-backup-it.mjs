#!/usr/bin/env node
/**
 * IT for notepad-backup.mjs — end-to-end smoke test
 */
import { execSync } from 'child_process';

const SCRIPT = 'D:/OpenClaw/workspace/shared/notepad-backup.mjs';

let output = '';
let exitCode = 0;
try {
  output = execSync(`node "${SCRIPT}"`, { encoding: 'utf8', timeout: 10000 });
} catch (e) {
  output = (e.stdout || '') + (e.stderr || '');
  exitCode = e.status || 1;
}

const ok1 = exitCode === 0;
console.log(`[IT] exit code 0: ${ok1 ? 'PASS' : 'FAIL'}`);

const ok2 = output.includes('[notepad-backup]');
console.log(`[IT] output prefix: ${ok2 ? 'PASS' : 'FAIL'}`);

const ok3 = output.includes('Priority Context entries:');
console.log(`[IT] stats shown: ${ok3 ? 'PASS' : 'FAIL'}`);

const allPass = ok1 && ok2 && ok3;
console.log(allPass ? '\n[IT ALL PASS]' : '\n[IT FAIL]');
process.exit(allPass ? 0 : 1);
