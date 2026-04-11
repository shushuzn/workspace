#!/usr/bin/env node
/**
 * shared/add-seed.test.mjs
 * Tests for add-seed.mjs Gate 4b-adjacent logic and file/batch modes.
 */
import { spawn } from 'child_process';
import { writeFileSync, unlinkSync, readFileSync } from 'fs';
import { tmpdir } from 'os';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));

const JSON_MODE = process.argv.includes('--json');
const log = JSON_MODE ? () => {} : console.log;
let passed = 0, failed = 0;
const results = [];
function test(name, fn) {
  try { fn(); passed++; if (JSON_MODE) results.push({ name, status: 'pass' }); else log(`  ✓ ${name}`); }
  catch (e) { failed++; if (JSON_MODE) results.push({ name, status: 'fail', error: e.message }); else { log(`  ✗ ${name}`); log(`    ${e.message}`); }}
}

function runCmd(args) {
  return new Promise((resolve) => {
    const p = spawn('node', ['shared/add-seed.mjs', ...args], {
      stdio: ['ignore', 'pipe', 'pipe']
    });
    let out = '';
    p.stdout.on('data', d => out += d.toString());
    p.stderr.on('data', d => out += d.toString());
    p.on('close', (code) => resolve({ exit: code || 0, out }));
  });
}

function runFileMode(filePath) {
  return runCmd(['--file', filePath]);
}

const BASE = '- [20260411] seed [brainstorm] [score:3x3=9] [f:3] [angle:ws-level] test | benefit: test | reason: test | approach: ';

async function run() {
  log('\n=== add-seed.mjs tests ===\n');

  // ── --help ────────────────────────────────────────────────────────────────────
  log('--- --help flag ---');
  await test('--help exits 0', async () => {
    const r = await runCmd(['--help']);
    if (r.exit !== 0) throw new Error('expected exit 0: ' + r.exit);
    if (!r.out.includes('Usage')) throw new Error('missing usage: ' + r.out.slice(0, 100));
  });

  // ── --file mode with missing path ─────────────────────────────────────────────
  log('--- --file missing path ---');
  await test('--file without path → exit 1', async () => {
    const r = await runCmd(['--file']);
    if (r.exit === 0) throw new Error('expected non-zero exit');
    if (!r.out.includes('--file requires')) throw new Error('missing error msg: ' + r.out.slice(0, 100));
  });

  // ── --file mode with unparseable line ─────────────────────────────────────────
  log('--- --file unparseable seed ---');
  await test('--file skips unparseable lines', async () => {
    const tmp = join(tmpdir(), `add-seed-parse-${Date.now()}.txt`);
    writeFileSync(tmp, 'totally invalid seed line\n');
    try {
      const r = await runFileMode(tmp);
      if (!r.out.includes('[SKIP]')) throw new Error('missing [SKIP]: ' + r.out.slice(0, 200));
    } finally { unlinkSync(tmp); }
  });

  // ── --file mode with valid but validation-failing seed ─────────────────────────
  log('--- --file validation failure ---');
  await test('--file records skipped on validation fail', async () => {
    const tmp = join(tmpdir(), `add-seed-parse-${Date.now()}.txt`);
    writeFileSync(tmp, BASE + '1. grep -r pattern .\n');
    try {
      const r = await runFileMode(tmp);
      if (!r.out.includes('[FAIL]')) throw new Error('missing [FAIL]: ' + r.out.slice(0, 200));
    } finally { unlinkSync(tmp); }
  });

  // ── --file mode success ────────────────────────────────────────────────────────
  log('--- --file success ---');
  await test('--file dry-run succeeds', async () => {
    const tmp = join(tmpdir(), `add-seed-parse-${Date.now()}.txt`);
    writeFileSync(tmp, BASE + '1. python shared/patch-exec-trace-grep.py\n');
    try {
      const r = await runFileMode(tmp);
      if (!r.out.includes('[OK]')) throw new Error('missing [OK]: ' + r.out.slice(0, 200));
    } finally { unlinkSync(tmp); }
  });

  // ── readonly step1 + no file creation → FAIL ─────────────────────────────────
  log('--- readonly step1 + no file creation → FAIL ---');
  await test('grep step1 → FAIL', async () => {
    const r = await runCmd([BASE + '1. grep -r pattern .']);
    if (!r.out.includes('[FAIL]')) throw new Error('expected [FAIL]: ' + r.out.slice(0, 200));
    if (!r.out.includes('Gate 4b-adjacent')) throw new Error('missing Gate 4b-adjacent');
  });

  await test('ls step1 → FAIL', async () => {
    const r = await runCmd([BASE + '1. ls shared/']);
    if (!r.out.includes('[FAIL]')) throw new Error('expected [FAIL]');
    if (!r.out.includes('Gate 4b-adjacent')) throw new Error('missing Gate 4b-adjacent');
  });

  await test('cat step1 → FAIL', async () => {
    const r = await runCmd([BASE + '1. cat file.txt']);
    if (!r.out.includes('[FAIL]')) throw new Error('expected [FAIL]');
    if (!r.out.includes('Gate 4b-adjacent')) throw new Error('missing Gate 4b-adjacent');
  });

  await test('cd step1 → FAIL', async () => {
    const r = await runCmd([BASE + '1. cd shared/']);
    if (!r.out.includes('[FAIL]')) throw new Error('expected [FAIL]');
    if (!r.out.includes('Gate 4b-adjacent')) throw new Error('missing Gate 4b-adjacent');
  });

  await test('echo step1 → FAIL', async () => {
    const r = await runCmd([BASE + '1. echo hello']);
    if (!r.out.includes('[FAIL]')) throw new Error('expected [FAIL]');
    if (!r.out.includes('Gate 4b-adjacent')) throw new Error('missing Gate 4b-adjacent');
  });

  // ── readonly step1 + file creation step2 → PASS ────────────────────────────────
  log('--- readonly step1 + file creation step2 → PASS ---');
  await test('grep + python step2 → PASS', async () => {
    const r = await runCmd([BASE + '1. grep -r pattern .\n2. python shared/patch-exec-trace-grep.py']);
    if (!r.out.includes('[OK]')) throw new Error('expected [OK]: ' + r.out.slice(0, 200));
    if (!r.out.includes('PASS')) throw new Error('missing PASS');
  });

  await test('grep + Edit step2 → PASS', async () => {
    const r = await runCmd([BASE + '1. grep pattern\n2. Edit shared/test.mjs']);
    if (!r.out.includes('[OK]')) throw new Error('expected [OK]');
    if (!r.out.includes('PASS')) throw new Error('missing PASS');
  });

  await test('ls + mkdir step2 → PASS', async () => {
    const r = await runCmd([BASE + '1. ls shared/\n2. mkdir -p shared/test-dir']);
    if (!r.out.includes('[OK]')) throw new Error('expected [OK]');
    if (!r.out.includes('PASS')) throw new Error('missing PASS');
  });

  // ── dangerous step1 → FAIL (Gate 4b) ─────────────────────────────────────────
  log('--- dangerous step1 → FAIL ---');
  await test('node -e step1 → FAIL', async () => {
    const r = await runCmd([BASE + '1. node -e "console.log(1)"']);
    if (!r.out.includes('[FAIL]')) throw new Error('expected [FAIL]');
    if (!r.out.includes('Gate 4b')) throw new Error('missing Gate 4b');
  });

  // ── IMPLEMENT step1 → PASS ───────────────────────────────────────────────────
  log('--- IMPLEMENT step1 → PASS ---');
  await test('python script step1 → PASS', async () => {
    const r = await runCmd([BASE + '1. python shared/patch-exec-trace-grep.py']);
    if (!r.out.includes('[OK]')) throw new Error('expected [OK]');
    if (!r.out.includes('PASS')) throw new Error('missing PASS');
  });

  await test('mkdir step1 → PASS', async () => {
    const r = await runCmd([BASE + '1. mkdir -p shared/test-dir']);
    if (!r.out.includes('[OK]')) throw new Error('expected [OK]');
    if (!r.out.includes('PASS')) throw new Error('missing PASS');
  });

  await test('node script.mjs step1 → PASS', async () => {
    const r = await runCmd([BASE + '1. node shared/step-parser.mjs']);
    if (!r.out.includes('[OK]')) throw new Error('expected [OK]');
    if (!r.out.includes('PASS')) throw new Error('missing PASS');
  });

  // ── Summary ──────────────────────────────────────────────────────────────────
  if (JSON_MODE) {
    console.log(JSON.stringify({ suite: 'add-seed', passed, failed, results }));
  } else {
    log(`\n=== Results: ${passed} passed, ${failed} failed ===\n`);
  }
  process.exit(failed > 0 ? 1 : 0);
}

run();
