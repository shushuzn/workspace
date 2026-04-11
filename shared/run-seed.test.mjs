#!/usr/bin/env node
/**
 * shared/run-seed.test.mjs
 * Tests for run-seed.mjs --validate-approach key paths.
 */
import { execSync } from 'child_process';

const JSON_MODE = process.argv.includes('--json');
const log = JSON_MODE ? () => {} : console.log;
let passed = 0, failed = 0;
const results = [];
function test(name, fn) {
  try { fn(); passed++; if (JSON_MODE) results.push({ name, status: 'pass' }); else log(`  ✓ ${name}`); }
  catch (e) { failed++; if (JSON_MODE) results.push({ name, status: 'fail', error: e.message }); else { log(`  ✗ ${name}`); log(`    ${e.message}`); }}
}
function run(cmd) {
  try {
    const out = execSync(cmd, { stdio: 'pipe', timeout: 10000 });
    return { exit: 0, out: (out || '').toString() };
  } catch (e) {
    return { exit: e.status || 1, out: ((e.stdout && e.stdout.toString()) || (e.stderr && e.stderr.toString()) || '').trim() };
  }
}

log('\n=== run-seed.mjs --validate-approach tests ===\n');

// ── Gate4b dangerous pattern detection ──────────────────────────────────────────
log('--- Gate4b dangerous patterns ---');

test('node -e fails', () => {
  const r = run('node shared/run-seed.mjs --validate-approach "1. node -e console.log(1)" --reason test');
  if (r.exit === 0) throw new Error('expected non-zero exit');
  if (!r.out.includes('Gate4b')) throw new Error('missing Gate4b: ' + r.out);
});

test('node -p fails', () => {
  const r = run('node shared/run-seed.mjs --validate-approach "1. node -p 1+1" --reason test');
  if (r.exit === 0) throw new Error('expected non-zero exit');
  if (!r.out.includes('Gate4b')) throw new Error('missing Gate4b: ' + r.out);
});

test('bash tee heredoc fails', () => {
  const r = run('node shared/run-seed.mjs --validate-approach "1. bash tee <<EOF" --reason test');
  if (r.exit === 0) throw new Error('expected non-zero exit');
});

test('bash node -e fails', () => {
  const r = run('node shared/run-seed.mjs --validate-approach "1. bash node -e console.log(1)" --reason test');
  if (r.exit === 0) throw new Error('expected non-zero exit');
  if (!r.out.includes('Gate4b')) throw new Error('missing Gate4b: ' + r.out);
});

// ── Valid executable prefixes ───────────────────────────────────────────────────
log('\n--- Valid executable prefixes ---');

test('python script passes', () => {
  const r = run('node shared/run-seed.mjs --validate-approach "1. python shared/patch-exec-trace-grep.py" --reason test');
  if (r.exit !== 0) throw new Error('expected zero exit: ' + r.out);
  if (!r.out.includes('PASS')) throw new Error('missing PASS: ' + r.out);
});

test('node script.mjs passes', () => {
  const r = run('node shared/run-seed.mjs --validate-approach "1. node shared/step-parser.mjs" --reason test');
  if (r.exit !== 0) throw new Error('expected zero exit: ' + r.out);
  if (!r.out.includes('PASS')) throw new Error('missing PASS: ' + r.out);
});

test('Edit fails (tool-name, not shell command)', () => {
  const r = run('node shared/run-seed.mjs --validate-approach "1. Edit shared/test.mjs" --reason test');
  if (r.exit === 0) throw new Error('expected non-zero exit');
  if (!r.out.includes('tool-name')) throw new Error('missing tool-name check: ' + r.out);
});

test('Write fails (tool-name, not shell command)', () => {
  const r = run('node shared/run-seed.mjs --validate-approach "1. Write shared/test.mjs content" --reason test');
  if (r.exit === 0) throw new Error('expected non-zero exit');
  if (!r.out.includes('tool-name')) throw new Error('missing tool-name check: ' + r.out);
});

test('mkdir passes', () => {
  const r = run('node shared/run-seed.mjs --validate-approach "1. mkdir -p shared/test-dir" --reason test');
  if (r.exit !== 0) throw new Error('expected zero exit: ' + r.out);
  if (!r.out.includes('PASS')) throw new Error('missing PASS: ' + r.out);
});

test('bash -c pipeline passes (allowed)', () => {
  const r = run('node shared/run-seed.mjs --validate-approach "1. bash -c grep" --reason test');
  if (r.exit !== 0) throw new Error('expected zero exit: ' + r.out);
  if (!r.out.includes('PASS')) throw new Error('missing PASS: ' + r.out);
});

// ── Script existence check ───────────────────────────────────────────────────────
log('\n--- Script existence check ---');

test('non-existent script fails', () => {
  const r = run('node shared/run-seed.mjs --validate-approach "1. python shared/nonexistent-script-xyz.py" --reason test');
  if (r.exit === 0) throw new Error('expected non-zero exit');
  if (!r.out.includes('does not exist')) throw new Error('missing existence check: ' + r.out);
});

// ── No executable prefix ───────────────────────────────────────────────────────
log('\n--- No executable prefix ---');

test('grep fails (no executable prefix)', () => {
  const r = run('node shared/run-seed.mjs --validate-approach "1. grep -r pattern ." --reason test');
  if (r.exit === 0) throw new Error('expected non-zero exit');
  if (!r.out.includes('no executable prefix')) throw new Error('missing prefix check: ' + r.out);
});

// ── Approach vs reason consistency (Gate 4c supplement) ─────────────────────────────────
log('\n--- Approach vs reason consistency ---');

test('echo approach + implement reason -> FAIL', () => {
  const r = run('node shared/run-seed.mjs --validate-approach "1. echo hello" --reason "新增功能"');
  if (r.exit === 0) throw new Error('expected non-zero exit');
  if (!r.out.includes('approach drift')) throw new Error('missing approach drift check: ' + r.out);
});

test('validation-only approach + implement reason -> FAIL', () => {
  const r = run('node shared/run-seed.mjs --validate-approach "1. node shared/run-seed.mjs --validate-approach" --reason "新增功能"');
  if (r.exit === 0) throw new Error('expected non-zero exit');
  if (!r.out.includes('approach drift')) throw new Error('missing approach drift check: ' + r.out);
});

// ── Summary ───────────────────────────────────────────────────────────────────
if (JSON_MODE) {
  console.log(JSON.stringify({ suite: 'run-seed', passed, failed, results }));
} else {
  log(`\n=== Results: ${passed} passed, ${failed} failed ===\n`);
}
process.exit(failed > 0 ? 1 : 0);
