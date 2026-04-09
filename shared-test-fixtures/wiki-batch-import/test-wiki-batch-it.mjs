#!/usr/bin/env node
/**
 * IT for wiki-batch-import.mjs — end-to-end smoke test
 */
import { execSync } from 'child_process';
import { writeFileSync, unlinkSync } from 'fs';

const SCRIPT = 'shared/wiki-batch-import.mjs';
const WS = '/d/OpenClaw/workspace';

// Test 1: missing file → error
let output = '';
try {
  execSync(`node ${SCRIPT} no-such-file.txt`, { cwd: WS, encoding: 'utf8', timeout: 5000 });
} catch (e) {
  output = (e.stdout || '') + (e.stderr || '');
}
const ok1 = output.includes('File not found');
console.log(`[IT] missing file: ${ok1 ? 'PASS' : 'FAIL'}`);

// Test 2: usage shown with no args
output = '';
try {
  execSync(`node ${SCRIPT}`, { cwd: WS, encoding: 'utf8', timeout: 5000 });
} catch (e) {
  output = (e.stdout || '') + (e.stderr || '');
}
const ok2 = output.includes('Usage:');
console.log(`[IT] usage shown: ${ok2 ? 'PASS' : 'FAIL'}`);

const allPass = ok1 && ok2;
console.log(allPass ? '\n[IT ALL PASS]' : '\n[IT FAIL]');
process.exit(allPass ? 0 : 1);
