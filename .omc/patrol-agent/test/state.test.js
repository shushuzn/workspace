// test/state.test.js
import { loadState, saveState } from '../src/state.js';
import { existsSync } from 'fs';
import { ok, equal } from 'assert';

// loadState returns object with expected fields
const state = loadState();
ok(typeof state.loop_count === 'number', 'loop_count is number');
ok(Array.isArray(state.completed_actions), 'completed_actions is array');
ok(Array.isArray(state.skipped), 'skipped is array');
ok(Array.isArray(state.patrol_log), 'patrol_log is array');

// saveState round-trips
const original = loadState();
const modified = { ...original, loop_count: original.loop_count + 1 };
saveState(modified);
const reloaded = loadState();
equal(reloaded.loop_count, modified.loop_count, 'state round-trips correctly');

// Restore original
saveState(original);
console.log('state.js: all tests passed');
