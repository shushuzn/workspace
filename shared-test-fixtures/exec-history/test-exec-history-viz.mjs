#!/usr/bin/env node
/**
 * Test for exec-history-viz.mjs
 */
import { writeFileSync, cpSync } from 'fs';
import { dirname } from 'path';
import { fileURLToPath, pathToFileURL } from 'url';
import { execSync, spawn } from 'child_process';

const THIS_DIR = dirname(fileURLToPath(import.meta.url));
const FIXTURE = THIS_DIR + '/sample.jsonl';
const HISTORY = '/d/OpenClaw/workspace/80-PROJECTS/task-orchestrator/exec-history.jsonl';
const SCRIPT_URL = pathToFileURL('D:/OpenClaw/workspace/shared/exec-history-viz.mjs').href;

// ── Tests with fixture data ──────────────────────────────────────
cpSync(FIXTURE, HISTORY, { overwrite: true });

let output;
try {
  output = execSync(`node "${SCRIPT_URL}"`, { cwd: '/d/OpenClaw/workspace', encoding: 'utf8', timeout: 10000 });
} catch (e) {
  output = (e.stdout || '') + (e.stderr || '');
}

const hasHeader = output.includes('Adapter Execution Trend');
const hasOpencli = output.includes('opencli');
const hasCliAnything = output.includes('cli-anything');
const hasDateSection = output.includes('Success Rate by Date');
const hasPerAdapter = output.includes('Per-Adapter Summary');

console.log(`[TEST] Header present: ${hasHeader ? 'PASS' : 'FAIL'}`);
console.log(`[TEST] opencli in output: ${hasOpencli ? 'PASS' : 'FAIL'}`);
console.log(`[TEST] cli-anything in output: ${hasCliAnything ? 'PASS' : 'FAIL'}`);
console.log(`[TEST] Date section: ${hasDateSection ? 'PASS' : 'FAIL'}`);
console.log(`[TEST] Per-adapter section: ${hasPerAdapter ? 'PASS' : 'FAIL'}`);

// ── Empty data test ──────────────────────────────────────────────
writeFileSync(HISTORY, '', 'utf8');
let emptyOut = '';
await new Promise((resolve) => {
  const p = spawn('node', [SCRIPT_URL], { cwd: '/d/OpenClaw/workspace', encoding: 'utf8' });
  p.stdout.on('data', d => emptyOut += d);
  p.on('close', resolve);
});
const handlesEmpty = emptyOut.includes('No data');
console.log(`[TEST] Empty data handled: ${handlesEmpty ? 'PASS' : 'FAIL'}`);

const allPass = hasHeader && hasOpencli && hasCliAnything && hasDateSection && hasPerAdapter && handlesEmpty;
console.log(allPass ? '\n[ALL TESTS PASS]' : '\n[SOME TESTS FAIL]');
process.exit(allPass ? 0 : 1);
