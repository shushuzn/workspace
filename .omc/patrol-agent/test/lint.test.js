// test/lint.test.js
import { checkLint, hasLintErrors } from '../src/lint.js';
import { ok, equal } from 'assert';

const results = checkLint();
ok(Array.isArray(results), 'checkLint returns array');

for (const r of results) {
  ok(typeof r.project === 'string', `project name: ${r.project}`);
  ok(typeof r.errors === 'number', `errors is number for ${r.project}`);
  if (r.errors === 0) {
    console.log(`  ${r.project}: ${r.errors} errors`);
  } else {
    console.log(`  ${r.project}: ${r.errors} ERRORS`);
  }
}

const hasErrors = hasLintErrors();
equal(typeof hasErrors, 'boolean', 'hasLintErrors returns boolean');

console.log('lint.js: checked', results.length, 'projects');
