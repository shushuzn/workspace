// test/plans.test.js
import { getPendingPlans } from '../src/plans.js';
import { ok } from 'assert';

const plans = getPendingPlans();
// Returns array (possibly empty)
ok(Array.isArray(plans), 'returns array');
if (plans.length > 0) {
  const p = plans[0];
  ok(typeof p.id === 'string', 'plan has id');
  ok(typeof p.file === 'string', 'plan has file');
  ok(p.updated_at !== undefined, 'plan has updated_at');
}
console.log(`plans.js: found ${plans.length} pending plans`);
