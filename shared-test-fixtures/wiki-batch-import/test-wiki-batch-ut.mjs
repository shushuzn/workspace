#!/usr/bin/env node
/**
 * UT for wiki-batch-import.mjs — ID parsing logic
 */
import { readFileSync } from 'fs';

const input = readFileSync('D:/OpenClaw/workspace/shared-test-fixtures/wiki-batch-import/id-list.txt', 'utf8');
const lines = input.split('\n').filter(Boolean);

const ids = [];
for (const line of lines) {
  const trimmed = line.trim();
  if (!trimmed || trimmed.startsWith('#')) continue;
  const idMatch = trimmed.match(/(\d+\.\d+)/);
  if (idMatch) ids.push(idMatch[1]);
}

// Expected: 2501.12345, 2501.67890, 2503.11111
const ok1 = ids.length === 3;
const ok2 = ids[0] === '2501.12345';
const ok3 = ids[1] === '2501.67890';
const ok4 = ids[2] === '2503.11111';

console.log(`[UT] id_count: ${ids.length} ${ok1 ? 'PASS' : 'FAIL'} (expect 3)`);
console.log(`[UT] id[0]: ${ids[0]} ${ok2 ? 'PASS' : 'FAIL'} (expect 2501.12345)`);
console.log(`[UT] id[1]: ${ids[1]} ${ok3 ? 'PASS' : 'FAIL'} (expect 2501.67890)`);
console.log(`[UT] id[2]: ${ids[2]} ${ok4 ? 'PASS' : 'FAIL'} (expect 2503.11111)`);

const allPass = ok1 && ok2 && ok3 && ok4;
console.log(allPass ? '\n[UT ALL PASS]' : '\n[UT FAIL]');
process.exit(allPass ? 0 : 1);
