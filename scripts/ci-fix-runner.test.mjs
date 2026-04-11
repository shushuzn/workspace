#!/usr/bin/env node
/**
 * scripts/ci-fix-runner.test.mjs
 * Self-test for ci-fix-runner. Verifies check-file behavior.
 * Run: node scripts/ci-fix-runner.test.mjs
 */
import { spawn } from 'child_process';
import { existsSync, writeFileSync, unlinkSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..');
const FIX_RUNNER = join(__dirname, 'ci-fix-runner.mjs');

let passed = 0, failed = 0;

function run(...args) {
  return new Promise((resolve) => {
    const p = spawn(process.execPath, [FIX_RUNNER, ...args], { cwd: ROOT });
    let out = '', err = '';
    p.stdout.on('data', d => out += d.toString());
    p.stderr.on('data', d => err += d.toString());
    p.on('close', code => resolve({ code, out, err }));
  });
}

async function test(name, fn) {
  process.stdout.write(`  ${name}... `);
  try {
    await fn();
    console.log('✅');
    passed++;
  } catch (e) {
    console.log(`❌ ${e.message}`);
    failed++;
  }
}

function assert(condition, msg) {
  if (!condition) throw new Error(msg);
}

// Temp workflow files for testing
const TEST_WF = join(ROOT, '.github', 'workflows', 'test-ci.yml');
const TEST_SCRIPT = join(ROOT, 'scripts', 'test-script.mjs');
const TEST_SCRIPT_BAD = join(ROOT, 'scripts', 'test-bad.mjs');

async function main() {
  console.log('\n=== ci-fix-runner self-test ===\n');

  // Setup: create test workflow with known patterns
  mkdirSync(join(ROOT, '.github', 'workflows'), { recursive: true });

  // Test 1: list command works
  await test('list returns exit 0', async () => {
    const r = await run('list');
    assert(r.code === 0, `exit ${r.code}`);
    assert(r.out.includes('setup-node cache failure'), 'missing patterns');
  });

  // Test 2: check-file clean workflow → 0
  await test('check-file: clean workflow → exit 0', async () => {
    writeFileSync(TEST_WF, `name: Test\non: push\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - uses: actions/setup-node@v4\n        with:\n          node-version: '20'\n`);
    const r = await run('check-file', TEST_WF);
    assert(r.code === 0, `exit ${r.code}: ${r.out.trim()}`);
  });

  // Test 3: workflow with cache: npm → exit 2 (P0)
  await test('check-file: cache npm → exit 2 (P0)', async () => {
    writeFileSync(TEST_WF, `name: Test\non: push\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - uses: actions/setup-node@v4\n        with:\n          node-version: '20'\n          cache: 'npm'\n`);
    const r = await run('check-file', TEST_WF);
    assert(r.code === 2, `exit ${r.code}: ${r.out.trim()}`);
    assert(r.out.includes('setup-node cache failure'), 'should detect cache:npm');
  });

  // Test 4: workflow with setup-node but no node-version → exit 1 (P0)
  await test('check-file: setup-node no version → exit 2 (P0)', async () => {
    writeFileSync(TEST_WF, `name: Test\non: push\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - uses: actions/setup-node@v4\n`);
    const r = await run('check-file', TEST_WF);
    assert(r.code === 2, `exit ${r.code}: ${r.out.trim()}`);
    assert(r.out.includes('node not found'), 'should detect missing node-version');
  });

  // Test 5: script with node -e inline → exit 1 (P1)
  await test('check-file: node -e inline → exit 1 (P1)', async () => {
    writeFileSync(TEST_SCRIPT_BAD, `#!/usr/bin/env node\nnode -e "console.log('test')"\n`);
    const r = await run('check-file', TEST_SCRIPT_BAD);
    assert(r.code === 1, `exit ${r.code}: ${r.out.trim()}`);
    assert(r.out.includes('exit code 126') || r.out.includes('node -e'), 'should detect node -e');
  });

  // Test 6: script with proper shebang → exit 0
  await test('check-file: proper shebang script → exit 0', async () => {
    writeFileSync(TEST_SCRIPT, `#!/usr/bin/env node\nconsole.log('test')\n`);
    const r = await run('check-file', TEST_SCRIPT);
    assert(r.code === 0, `exit ${r.code}: ${r.out.trim()}`);
  });

  // Test 7: nonexistent file → exit 1
  await test('check-file: nonexistent file → exit 1', async () => {
    const r = await run('check-file', 'DOES_NOT_EXIST.yml');
    assert(r.code === 1, `exit ${r.code}`);
  });

  // Test 8: git-check with no changes → exit 0
  await test('git-check: no workflow changes → exit 0', async () => {
    const r = await run('git-check', 'HEAD');
    assert(r.code === 0, `exit ${r.code}: ${r.out.trim()}`);
  });

  // Test 9: dry-run for known fix
  await test('dry-run: setup-node cache failure → exit 0', async () => {
    const r = await run('dry-run', 'setup-node cache failure');
    assert(r.code === 0, `exit ${r.code}`);
    assert(r.out.includes('Remove the cache'), 'should describe fix');
  });

  // Cleanup
  try { unlinkSync(TEST_WF); } catch {}
  try { unlinkSync(TEST_SCRIPT); } catch {}
  try { unlinkSync(TEST_SCRIPT_BAD); } catch {}

  console.log(`\n${passed} passed, ${failed} failed\n`);
  process.exit(failed > 0 ? 1 : 0);
}

main().catch(e => { console.error(e); process.exit(1); });
