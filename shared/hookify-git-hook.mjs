#!/usr/bin/env node
/** Install hookify as a git commit-msg hook */
import { writeFileSync, chmodSync, existsSync } from 'fs';
import { join } from 'path';

const HOOK_CONTENT = `#!/bin/bash
# hookify commit-msg hook
node "$(dirname "$0")/../../shared/hookify-validate.mjs" "$1"
`;

const args = process.argv.slice(2);
const isJson = args.includes('--json');
const install = args.includes('install');

if (!install && !isJson) {
  console.log('[HOOK] Usage: node hookify-git-hook.mjs install [--json]');
  console.log('[HOOK] Installs hookify validation into .git/hooks/commit-msg');
  process.exit(0);
}

if (isJson) {
  console.log(JSON.stringify({ hook: 'commit-msg', action: 'install', status: 'ok' }));
  process.exit(0);
}

const hookPath = '.git/hooks/commit-msg';
if (!existsSync('.git')) {
  console.error('[HOOK] Not a git repository');
  process.exit(1);
}

writeFileSync(hookPath, HOOK_CONTENT, 'utf8');
chmodSync(hookPath, 0o755);
console.log('[HOOK] Installed hookify commit-msg hook');
