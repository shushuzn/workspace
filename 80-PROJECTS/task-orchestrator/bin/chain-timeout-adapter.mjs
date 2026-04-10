#!/usr/bin/env node
/**
 * chain-timeout-adapter.mjs — adaptive timeout strategy for task chains
 * Chains are assigned timeout based on their length: short chains get tighter timeouts
 * Usage: node chain-timeout-adapter.mjs --test
 */
import { execSync } from 'child_process';

const MODE = process.argv.includes('--test') ? 'test' : 'live';
const TIMEOUT_MAP = {
  // chain_length → timeout_seconds
  1: 30,
  2: 60,
  3: 120,
  4: 180,
  5: 300,
};

function getTimeout(chainLength) {
  if (TIMEOUT_MAP[chainLength] !== undefined) return TIMEOUT_MAP[chainLength];
  return 300; // default 5min
}

if (MODE === 'test') {
  const tests = [[1, 30], [2, 60], [3, 120], [4, 180], [5, 300], [10, 300]];
  let passed = 0;
  for (const [len, expected] of tests) {
    const got = getTimeout(len);
    if (got === expected) {
      console.log(`[OK] chain=${len} → ${got}s`);
      passed++;
    } else {
      console.error(`[FAIL] chain=${len}: expected ${expected}s, got ${got}s`);
    }
  }
  console.log(`\n${passed}/${tests.length} tests passed`);
  process.exit(passed === tests.length ? 0 : 1);
}

console.log('[chain-timeout-adapter] Available timeouts:', TIMEOUT_MAP);
console.log('[chain-timeout-adapter] Usage: node chain-timeout-adapter.mjs --test');
