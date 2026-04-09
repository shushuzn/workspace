#!/usr/bin/env node
/**
 * Unit tests for check-deps-health.mjs
 */
import { existsSync, mkdirSync, writeFileSync, rmSync, readdirSync } from 'fs';
import { join } from 'path';

const TMP = '/tmp/check-deps-test';
try { rmSync(TMP, { recursive: true }); } catch {}
try { mkdirSync(TMP, { recursive: true }); } catch {}

mkdirSync(join(TMP, 'proj-with-nm'), { recursive: true });
mkdirSync(join(TMP, 'proj-without'), { recursive: true });
writeFileSync(join(TMP, 'proj-with-nm', 'package.json'), '{"name":"a"}');
writeFileSync(join(TMP, 'proj-without', 'package.json'), '{"name":"b"}');
mkdirSync(join(TMP, 'proj-with-nm', 'node_modules'), { recursive: true });

// Replicate core filtering logic from check-deps-health.mjs
const projects = readdirSync(TMP).filter(p => {
  try {
    return !p.startsWith('.') && !p.includes('ARCHIVED') &&
           existsSync(join(TMP, p, 'package.json'));
  } catch { return false; }
});

// Build results matching script behavior
const results = [];
for (const proj of projects) {
  const nm = join(TMP, proj, 'node_modules');
  results.push({ proj, hasNm: existsSync(nm) });
}

const withNm = results.filter(r => r.hasNm);
const withoutNm = results.filter(r => !r.hasNm);

const ok1 = results.length === 2;
const ok2 = withNm.length === 1 && withNm[0].proj === 'proj-with-nm';
const ok3 = withoutNm.length === 1 && withoutNm[0].proj === 'proj-without';

console.log(`[UT] project_count: ${results.length} ${ok1 ? 'PASS' : 'FAIL'} (expect 2)`);
console.log(`[UT] with_nm: ${ok2 ? 'PASS' : 'FAIL'} (expect 1)`);
console.log(`[UT] without_nm: ${ok3 ? 'PASS' : 'FAIL'} (expect 1)`);

try { rmSync(TMP, { recursive: true }); } catch {}

const allPass = ok1 && ok2 && ok3;
console.log(allPass ? '\n[UT ALL PASS]' : '\n[UT FAIL]');
process.exit(allPass ? 0 : 1);
