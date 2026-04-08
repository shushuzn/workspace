#!/usr/bin/env node
/**
 * OMC Hookify Rules Test
 * Verifies all dangerous command rules match expected commands.
 */
import { existsSync, readFileSync, readdirSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const RULES_DIR = resolve(__dirname, '../../.claude');

// Per-rule test cases: [command, shouldMatch]
const TESTS = {
  'git-clean-fd': [
    ['git clean -fd', true],
    ['git clean -f -d', true],
    ['git clean -fd --dry-run', true],
    ['git clean -n', false],
    ['git clean', false],
  ],
  'git-reset-hard': [
    ['git reset --hard HEAD~1', true],
    ['git reset --hard origin/main', true],
    ['git reset --soft', false],
    ['git reset --mixed', false],
  ],
  'rm-rf-root': [
    ['rm -rf /', true],
    ['rm -rf /root', true],
    ['rm -rf /usr/local', true],
    ['rm -rf ~/Downloads', false],
    ['rm -rf node_modules', false],
  ],
  'dd-destroy': [
    ['dd if=/dev/zero of=/dev/sda', true],
    ['dd if=input.bin of=output.bin bs=1M', true],
    ['ls dd', false],
  ],
  'chmod-777': [
    ['chmod -R 777 /tmp', true],
    ['chmod 777 file', true],
    ['chmod -R 755 /home', false],
    ['chmod +x script.sh', false],
  ],
  'git-push-force': [
    ['git push --force origin main', true],
    ['git push -f', true],
    ['git push -f origin', true],
    ['git push origin main', false],
  ],
  'fork-bomb': [
    [':(){ :|:& };: &', true],  // full fork bomb with backgrounding &
    [':(){ :|:& };:', false],    // no & — not backgrounded
    ['(){ :|:& };:', false],    // missing leading ':'
    ['while :; do :; done &', true],
    ['echo fork()', false],
  ],
};

// Parse YAML frontmatter (simple parser)
function parseFrontmatter(content) {
  const fm = {};
  if (!content.startsWith('---')) return fm;
  const end = content.indexOf('\n---', 3);
  if (end === -1) return fm;
  const yaml = content.slice(4, end);
  for (const line of yaml.split('\n')) {
    const idx = line.indexOf(':');
    if (idx === -1) continue;
    const key = line.slice(0, idx).trim();
    const val = line.slice(idx + 1).trim().replace(/^["']|["']$/g, '');
    fm[key] = val;
  }
  return fm;
}

function main() {
  // Load all rules
  const ruleFiles = readdirSync(RULES_DIR)
    .filter(f => f.startsWith('hookify.') && f.endsWith('.local.md'));

  const rules = {};
  for (const f of ruleFiles) {
    const content = readFileSync(resolve(RULES_DIR, f), 'utf-8');
    const fm = parseFrontmatter(content);
    const name = fm.name;
    const pattern = fm.pattern;
    if (name && pattern) {
      rules[name] = { file: f, pattern, event: fm.event, enabled: fm.enabled === 'true' };
    }
  }

  console.log(`\n=== Hookify Rules Test ===\n`);
  console.log(`Found ${Object.keys(rules).length} rules in .claude/\n`);

  let pass = 0, fail = 0;

  // Test each dangerous rule
  for (const [name, testCases] of Object.entries(TESTS)) {
    const rule = rules[name];
    if (!rule) {
      console.log(`  ❌ ${name}: MISSING — not found in .claude/`);
      fail++;
      continue;
    }

    let rulePass = true;
    const regex = new RegExp(rule.pattern, 'i');

    for (const [cmd, expected] of testCases) {
      const matched = regex.test(cmd);
      if (matched !== expected) {
        console.log(`  ❌ ${name}: "${cmd}" expected=${expected} got=${matched}`);
        console.log(`     pattern: ${rule.pattern}`);
        rulePass = false;
      }
    }

    if (rulePass) {
      const icon = rule.enabled ? '✅' : '⚠️ ';
      console.log(`  ${icon} ${name}: ${testCases.length} tests passed (enabled=${rule.enabled})`);
      pass++;
    } else {
      fail++;
    }

    // Verify YAML validity
    const fm = parseFrontmatter(readFileSync(resolve(RULES_DIR, rule.file), 'utf-8'));
    const missing = ['name', 'enabled', 'event', 'pattern'].filter(k => !fm[k]);
    if (missing.length > 0) {
      console.log(`    ❌ YAML missing: ${missing.join(', ')}`);
      fail++;
      pass--;
    }
  }

  // Verify all required rules exist
  console.log(`\n=== Required Dangerous Rules ===\n`);
  const REQUIRED = Object.keys(TESTS);
  for (const name of REQUIRED) {
    if (rules[name]) {
      console.log(`  ✅ ${name}`);
    } else {
      console.log(`  ❌ MISSING: ${name}`);
      fail++;
    }
  }

  // Test: dangerous commands SHOULD be detected
  console.log(`\n=== Live Dangerous Command Detection ===\n`);
  const dangerousCmds = [
    'git clean -fd',
    'git reset --hard HEAD~1',
    'rm -rf /',
    'dd if=/dev/zero of=/dev/sda',
    'chmod -R 777 /tmp',
    'git push --force',
  ];
  for (const cmd of dangerousCmds) {
    const matched = [];
    for (const [name, rule] of Object.entries(rules)) {
      if (new RegExp(rule.pattern, 'i').test(cmd)) matched.push(name);
    }
    if (matched.length > 0) {
      console.log(`  ✅ "${cmd}" → ${matched.join(', ')}`);
    } else {
      console.log(`  ❌ "${cmd}" → NO RULE MATCHED`);
      fail++;
    }
  }

  // Test: safe commands should NOT match critical rules
  console.log(`\n=== Safe Commands (should not trigger) ===\n`);
  const safeCmds = [
    'ls -la',
    'git status',
    'git add .',
    'echo hello',
    'node script.js',
  ];
  for (const cmd of safeCmds) {
    const matched = [];
    for (const name of Object.keys(TESTS)) {
      const rule = rules[name];
      if (rule && new RegExp(rule.pattern, 'i').test(cmd)) matched.push(name);
    }
    if (matched.length === 0) {
      console.log(`  ✅ "${cmd}" → clean (no false positives)`);
    } else {
      console.log(`  ❌ "${cmd}" → FALSE POSITIVE: ${matched.join(', ')}`);
      fail++;
    }
  }

  console.log(`\n=== Results: ${pass} rule-sets passed, ${fail} failed ===\n`);
  if (fail > 0) process.exit(1);
}

main();
