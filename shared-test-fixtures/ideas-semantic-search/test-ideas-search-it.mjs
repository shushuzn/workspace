#!/usr/bin/env node
/**
 * IT for ideas-semantic-search.mjs — end-to-end smoke test
 */
import { execSync } from 'child_process';

const SCRIPT = 'D:/OpenClaw/workspace/shared/ideas-semantic-search.mjs';
const INDEX = 'D:/OpenClaw/workspace/.omc/ideas-index.json';

let output = '';
let exitCode = 0;
try {
  output = execSync(`node "${SCRIPT}" search "批量导入"`, { encoding: 'utf8', timeout: 10000 });
} catch (e) {
  output = (e.stdout || '') + (e.stderr || '');
  exitCode = e.status || 1;
}

const ok1 = exitCode === 0;
console.log(`[IT] exit code 0: ${ok1 ? 'PASS' : 'FAIL'}`);

const ok2 = output.includes('Keyword Search:');
console.log(`[IT] search header: ${ok2 ? 'PASS' : 'FAIL'}`);

const ok3 = output.includes('批量导入');
console.log(`[IT] results found: ${ok3 ? 'PASS' : 'FAIL'}`);

const allPass = ok1 && ok2 && ok3;
console.log(allPass ? '\n[IT ALL PASS]' : '\n[IT FAIL]');
process.exit(allPass ? 0 : 1);
