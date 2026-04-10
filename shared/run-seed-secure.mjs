#!/usr/bin/env node
/**
 * shared/run-seed-secure.mjs
 *
 * Adds dangerous command blacklist to Gate4b in run-seed.mjs.
 * Intercepts: python -c, node -e/p/c, bash -c with dangerous patterns.
 *
 * Usage:
 *   node shared/run-seed-secure.mjs --init
 */
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const RUN_SEED = join(__DIR, 'run-seed.mjs');

const mode = process.argv.includes('--init') ? 'init' : process.argv.includes('--check') ? 'check' : 'help';

const DANGEROUS_PATTERNS = [
  { pattern: /python\s+-c\s+["'].*['"]/i, name: 'python -c inline code' },
  { pattern: /node\s+-[epc]\s+/i, name: 'node -e/p/c inline' },
  { pattern: /bash\s+-c\s+["'].*['"]/i, name: 'bash -c inline code' },
];

function help() {
  console.log('Usage:');
  console.log('  node shared/run-seed-secure.mjs --init   # patch run-seed.mjs with blacklist');
  console.log('  node shared/run-seed-secure.mjs --check   # check if patched');
}

function check() {
  const content = readFileSync(RUN_SEED, 'utf-8');
  const hasBlacklist = content.includes('DANGEROUS_COMMAND_BLACKLIST');
  const hasGate4bEnhancement = content.includes('Gate4b blacklist check');
  if (hasBlacklist && hasGate4bEnhancement) {
    console.log('[OK] run-seed.mjs already has dangerous command blacklist');
  } else {
    console.log('[WARN] run-seed.mjs missing dangerous command blacklist');
  }
}

function patchRunSeed() {
  if (!existsSync(RUN_SEED)) {
    console.error('[ERROR] run-seed.mjs not found');
    process.exit(1);
  }
  const content = readFileSync(RUN_SEED, 'utf-8');
  if (content.includes('DANGEROUS_COMMAND_BLACKLIST')) {
    console.log('[OK] Already patched');
    return;
  }

  // Find Gate4b check location and add blacklist validation
  const GATE4B_CHECK = `const EXEC_PREFIXES = ['python ', 'bash ', 'sh ', 'cd ', 'mkdir ', '//', '#', '/'];`;
  const PATCH = `const DANGEROUS_COMMAND_BLACKLIST = [
    { pattern: /python\\s+-c\\s+["'][\\s\\S]+["']/i, name: 'python -c inline code' },
    { pattern: /node\\s+-[epc]\\s+/i, name: 'node -e/p/c inline' },
    { pattern: /bash\\s+-c\\s+["'][\\s\\S]+["']/i, name: 'bash -c inline code' },
  ];
  const isDangerousCommand = DANGEROUS_COMMAND_BLACKLIST.some(d => d.pattern.test(firstStep));
  if (isDangerousCommand) {
    console.error(\`[Gate4b FAIL] Dangerous command pattern detected: \${firstStep.slice(0, 60)}\`);
    process.exit(1);
  }
  const EXEC_PREFIXES = ['python ', 'bash ', 'sh ', 'cd ', 'mkdir ', '//', '#', '/'];`;

  const newContent = content.replace(GATE4B_CHECK, PATCH);
  writeFileSync(RUN_SEED, newContent, 'utf-8');
  console.log('[PATCHED] Added dangerous command blacklist to run-seed.mjs');
}

if (mode === 'help') {
  help();
} else if (mode === 'check') {
  check();
} else if (mode === 'init') {
  patchRunSeed();
}
