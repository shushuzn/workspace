#!/usr/bin/env python3
"""Patch hookify-git-hook.mjs to add --json output mode"""
import sys

filepath = "shared/hookify-git-hook.mjs"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

if '--json' in content:
    print("already has --json")
    sys.exit(0)

# Replace install detection to support --json flag
old = """const install = process.argv.includes('install');

if (!install) {
  console.log('[HOOK] Usage: node hookify-git-hook.mjs install');
  console.log('[HOOK] Installs hookify validation into .git/hooks/commit-msg');
  process.exit(0);
}

const hookPath = '.git/hooks/commit-msg';
if (!existsSync('.git')) {
  console.error('[HOOK] Not a git repository');
  process.exit(1);
}

writeFileSync(hookPath, HOOK_CONTENT, 'utf8');
chmodSync(hookPath, 0o755);
console.log('[HOOK] Installed hookify commit-msg hook');"""

new = """const args = process.argv.slice(2);
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
console.log('[HOOK] Installed hookify commit-msg hook');"""

if old in content:
    content = content.replace(old, new)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("added --json")
else:
    print("skip: pattern not found")
