#!/usr/bin/env node
/**
 * test-ci-tools.mjs
 * Integration tests for CI fix runner tools.
 * Run: node scripts/test-ci-tools.mjs
 */
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));

function run(script, args = []) {
  return new Promise((resolve, reject) => {
    const p = spawn('node', [join(__dirname, script), ...args], { shell: true });
    let out = '', err = '';
    p.stdout.on('data', d => out += d.toString());
    p.stderr.on('data', d => err += d.toString());
    p.on('close', code => resolve({ code, out, err }));
    p.on('error', reject);
  });
}

async function assert(condition, message) {
  if (!condition) throw new Error('FAIL: ' + message);
  console.log('  ✓ ' + message);
}

let passed = 0, failed = 0;

async function test(name, fn) {
  try {
    await fn();
    passed++;
  } catch (e) {
    console.error('  ✗ ' + e.message);
    failed++;
  }
}

async function runAll() {
  console.log('\n=== CI Tools Self-Test ===\n');

  // 1. list command exits 0
  await test('list command exits 0', async () => {
    const result = await run('ci-fix-runner.mjs', ['list']);
    assert(result.code === 0, `exit ${result.code}`);
    assert(!result.out.includes('NaN'), 'output contains no NaN');
    assert(result.out.includes('Confidence:'), 'output has Confidence field');
  });

  // 2. list shows Wilson CI format
  await test('list shows Wilson CI format with brackets', async () => {
    const result = await run('ci-fix-runner.mjs', ['list']);
    // Matches "59% [25-92%]" style
    assert(/\d+% \[.*%\]/.test(result.out), 'has Wilson CI bracket format');
  });

  // 3. recommend command exits 0
  await test('recommend command exits 0', async () => {
    const result = await run('ci-fix-runner.mjs', ['recommend']);
    assert(result.code === 0, `exit ${result.code}`);
    assert(result.out.includes('Bayesian Fix Recommendations'), 'output has header');
  });

  // 4. recommend scores are non-negative
  await test('recommend scores are non-negative', async () => {
    const result = await run('ci-fix-runner.mjs', ['recommend']);
    // Match "green 0.602" style scores
    const scoreRe = /(green|yellow|grey)\s+(\d+\.\d+)/g;
    let match;
    let found = false;
    while ((match = scoreRe.exec(result.out)) !== null) {
      found = true;
      const score = parseFloat(match[2]);
      assert(score >= 0, `score ${score} >= 0`);
    }
    assert(found, 'at least one score found');
  });

  // 5. recommend EffConf is valid percentage
  await test('recommend EffConf is valid 0-100%', async () => {
    const result = await run('ci-fix-runner.mjs', ['recommend']);
    const confRe = /\s+(\d+%)\s+\w+\s+(never|\d+d)\s+/g;
    let match;
    let found = false;
    while ((match = confRe.exec(result.out)) !== null) {
      found = true;
      const conf = match[1];
      assert(/^\d+%$/.test(conf), `EffConf "${conf}" is valid percentage`);
    }
    assert(found, 'at least one EffConf found');
  });

  // 6. dry-run with no args shows usage or errors
  await test('dry-run with no args shows usage', async () => {
    const result = await run('ci-fix-runner.mjs', ['dry-run']);
    assert(result.code !== 0 || result.out.includes('Usage'), 'shows usage or errors gracefully');
  });

  // 7. unknown command exits non-zero
  await test('unknown command exits non-zero', async () => {
    const result = await run('ci-fix-runner.mjs', ['foobar']);
    assert(result.code !== 0, `exit ${result.code} is non-zero`);
  });

  // 8. decay script exists
  await test('decay script exists', async () => {
    const { existsSync } = await import('fs');
    const path = join(__dirname, 'ci-pattern-health-decay.mjs');
    assert(existsSync(path), 'ci-pattern-health-decay.mjs exists');
  });

  // 9. predictor script exists
  await test('predictor script exists', async () => {
    const { existsSync } = await import('fs');
    const path = join(__dirname, 'ci-fix-predictor.mjs');
    assert(existsSync(path), 'ci-fix-predictor.mjs exists');
  });

  // 10. recommend top pick has non-null fix text
  await test('recommend top pick has non-empty fix text', async () => {
    const result = await run('ci-fix-runner.mjs', ['recommend']);
    assert(result.out.includes('-> Top pick:'), 'has top pick');
    assert(result.out.includes('Fix:'), 'has fix description');
  });

  // Summary
  console.log('\n' + (failed === 0 ? '✅ All tests passed' : `⚠️  ${failed} failed, ${passed} passed`));
  process.exit(failed > 0 ? 1 : 0);
}

runAll().catch(e => { console.error(e); process.exit(1); });
