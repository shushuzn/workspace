#!/usr/bin/env node
/**
 * shared/step-parser.test.mjs
 * Unit tests for step-parser.mjs step-type classification.
 */
import { equal, deepEqual } from 'assert';
import {
  stepTypeClassification,
  isReadOnlyStep,
  hasFileCreation,
  extractFirstStep,
  extractAllSteps,
  READONLY_PREFIXES,
  FILE_CREATION_PATTERNS,
  DANGEROUS_PATTERNS,
} from './step-parser.mjs';

// ── Test helpers ────────────────────────────────────────────────────────────────
const JSON_MODE = process.argv.includes('--json');
const log = JSON_MODE ? () => {} : console.log;
let passed = 0, failed = 0;
const results = [];
function test(name, fn) {
  try { fn(); passed++; if (JSON_MODE) results.push({ name, status: 'pass' }); else log(`  ✓ ${name}`); }
  catch (e) { failed++; if (JSON_MODE) results.push({ name, status: 'fail', error: e.message }); else { log(`  ✗ ${name}`); log(`    ${e.message}`); }}
}
function eq(actual, expected, msg) {
  if (actual !== expected) throw new Error(`${msg}: expected ${expected}, got ${actual}`);
}

log('\n=== step-parser.mjs tests ===\n');

// ── READONLY classification ────────────────────────────────────────────────────
log('READONLY_PREFIXES:');
READONLY_PREFIXES.forEach(p => log(' ', p));

log('\nFILE_CREATION_PATTERNS:');
FILE_CREATION_PATTERNS.forEach(p => log(' ', p));

log('\nDANGEROUS_PATTERNS:');
DANGEROUS_PATTERNS.forEach(d => log(' ', d.name, '→', d.alt));

// ── stepTypeClassification tests ───────────────────────────────────────────────
log('\n--- stepTypeClassification ---');

test('grep is READONLY', () => {
  const r = stepTypeClassification('grep -r "pattern" .');
  eq(r.type, 'READONLY');
});

test('ls is READONLY', () => {
  const r = stepTypeClassification('ls shared/');
  eq(r.type, 'READONLY');
});

test('cat is READONLY', () => {
  const r = stepTypeClassification('cat file.txt');
  eq(r.type, 'READONLY');
});

test('python script.py is IMPLEMENT', () => {
  const r = stepTypeClassification('python shared/patch-xxx.py');
  eq(r.type, 'IMPLEMENT');
});

test('Edit is IMPLEMENT', () => {
  const r = stepTypeClassification('Edit src/file.mjs');
  eq(r.type, 'IMPLEMENT');
});

test('Write is IMPLEMENT', () => {
  const r = stepTypeClassification('Write src/test.mjs content');
  eq(r.type, 'IMPLEMENT');
});

test('node script.mjs is IMPLEMENT', () => {
  const r = stepTypeClassification('node shared/run-seed.mjs');
  eq(r.type, 'IMPLEMENT');
});

test('mkdir is IMPLEMENT', () => {
  const r = stepTypeClassification('mkdir -p path/to/dir');
  eq(r.type, 'IMPLEMENT');
});

test('node -e is INVALID', () => {
  const r = stepTypeClassification('node -e "console.log(1)"');
  eq(r.type, 'INVALID');
  eq(r.dangerous.name, 'node -e/p/c inline');
});

test('node -p is INVALID', () => {
  const r = stepTypeClassification('node -p "1+1"');
  eq(r.type, 'INVALID');
});

test('node -c is INVALID', () => {
  const r = stepTypeClassification('node -c "1+1"');
  eq(r.type, 'INVALID');
});

test('bash tee <<EOF is INVALID', () => {
  const r = stepTypeClassification('bash tee <<EOF');
  eq(r.type, 'INVALID');
  eq(r.dangerous.name, 'heredoc tee');
});

test('bash node -e is INVALID', () => {
  const r = stepTypeClassification('bash node -e "console.log(1)"');
  eq(r.type, 'INVALID');
  eq(r.dangerous.name, 'bash node -e/p/c');
});

test('python -c with heredoc is INVALID', () => {
  const r = stepTypeClassification('python -c "open(\'f\',\'w\').write(<<EOF)"');
  eq(r.type, 'INVALID');
  eq(r.dangerous.name, 'python heredoc in -c');
});

test('bash -c pipeline is IMPLEMENT (allowed)', () => {
  const r = stepTypeClassification('bash -c "grep x | head"');
  eq(r.type, 'IMPLEMENT');
});

test('cd is READONLY', () => {
  const r = stepTypeClassification('cd shared/');
  eq(r.type, 'READONLY');
});

// ── isReadOnlyStep tests ───────────────────────────────────────────────────────
log('\n--- isReadOnlyStep ---');

test('grep returns true', () => eq(isReadOnlyStep('grep x y'), true));
test('ls returns true', () => eq(isReadOnlyStep('ls shared/'), true));
test('cat returns true', () => eq(isReadOnlyStep('cat file'), true));
test('python returns false', () => eq(isReadOnlyStep('python x.py'), false));
test('Edit returns false', () => eq(isReadOnlyStep('Edit file.mjs'), false));
test('node -e returns false (dangerous, not readonly)', () => eq(isReadOnlyStep('node -e x'), false));

// ── hasFileCreation tests ──────────────────────────────────────────────────────
log('\n--- hasFileCreation ---');

test('step2 python script.py → true', () => {
  eq(hasFileCreation('1. grep pattern\n2. python shared/patch-xxx.py'), true);
});

test('step2 Edit → true', () => {
  eq(hasFileCreation('1. grep pattern\n2. Edit src/file.mjs'), true);
});

test('step2 Write → true', () => {
  eq(hasFileCreation('1. grep pattern\n2. Write src/file.mjs'), true);
});

test('step2 ls only → false', () => {
  eq(hasFileCreation('1. grep pattern\n2. ls shared/'), false);
});

test('step2 mkdir → true', () => {
  eq(hasFileCreation('1. grep pattern\n2. mkdir -p path'), true);
});

test('single step grep → false', () => {
  eq(hasFileCreation('1. grep pattern'), false);
});

// ── extractFirstStep tests ─────────────────────────────────────────────────────
log('\n--- extractFirstStep ---');

test('extracts first step', () => {
  const r = extractFirstStep('1. python x.py\n2. Edit y.mjs');
  eq(r.stepNum, '1');
  eq(r.firstStep, 'python x.py');
});

test('returns null on no match', () => {
  const r = extractFirstStep('no numbered steps');
  eq(r, null);
});

// ── extractAllSteps tests ───────────────────────────────────────────────────────
log('\n--- extractAllSteps ---');

test('extracts all steps', () => {
  const r = extractAllSteps('1. python x.py\n2. Edit y.mjs\n3. node z.mjs');
  eq(r.length, 3);
  eq(r[0].stepNum, '1');
  eq(r[1].stepNum, '2');
  eq(r[2].stepNum, '3');
});

test('handles step with newline content', () => {
  const r = extractAllSteps('1. node -e "console.log(1)"\n2. Edit file.mjs');
  eq(r.length, 2);
  eq(r[0].stepText, 'node -e "console.log(1)"');
});

// ── Summary ───────────────────────────────────────────────────────────────────
if (JSON_MODE) {
  console.log(JSON.stringify({ suite: 'step-parser', passed, failed, results }));
} else {
  console.log(`\n=== Results: ${passed} passed, ${failed} failed ===\n`);
}
process.exit(failed > 0 ? 1 : 0);
