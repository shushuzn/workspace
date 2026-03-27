// test/git.test.js
import { hasWorkingTreeChanges, getChangedFiles, getCurrentBranch } from '../src/git.js';
import { ok, equal } from 'assert';

const branch = getCurrentBranch();
ok(typeof branch === 'string' && branch.length > 0, 'getCurrentBranch returns non-empty string');

const changed = getChangedFiles();
ok(Array.isArray(changed), 'getChangedFiles returns array');

// hasWorkingTreeChanges with empty array returns false
equal(hasWorkingTreeChanges([]), false, 'empty files = no conflict');

console.log(`git.js: branch=${branch}, changed=${changed.length} files`);
