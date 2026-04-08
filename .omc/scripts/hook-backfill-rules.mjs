#!/usr/bin/env node
/**
 * OMC Hook Backfill Scanner
 * Scans audit log for dangerous command patterns → generates missing hookify rules.
 *
 * Usage:
 *   node hook-backfill-rules.mjs         Scan and show missing rules
 *   node hook-backfill-rules.mjs --apply  Generate missing rules automatically
 */
import { existsSync, readFileSync, writeFileSync, readdirSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const STATE_DIR = resolve(__dirname, '../state');
const AUDIT_LOG = resolve(STATE_DIR, 'hook-audit.jsonl');
const RULES_DIR = resolve(__dirname, '../../.claude');

// ── Known dangerous patterns ─────────────────────────────────────────────────
const DANGEROUS_PATTERNS = [
  {
    name: 'git-clean-fd',
    event: 'bash',
    pattern: 'git\\s+clean\\s+.*-[fF][dD]',
    severity: 'high',
    message: `⚠️ **git clean -fd detected**

This command deletes untracked files permanently.

**Why dangerous:**
- Removes all untracked files (git clean -f) and directories (git clean -d)
- Cannot be undone — no git history for untracked files
- May delete generated files that should be preserved

**Safer alternatives:**
- Preview first: \`git clean -n -fd\` (dry run)
- Delete specific files manually
- Use \`git stash\` instead of clean
`,
  },
  {
    name: 'git-reset-hard',
    event: 'bash',
    pattern: 'git\\s+reset\\s+.*--hard',
    severity: 'high',
    message: `⚠️ **git reset --hard detected**

This command rewrites history and destroys uncommitted changes.

**Why dangerous:**
- Discards all uncommitted changes
- Rewrites commit history (dangerous on shared branches)
- Cannot be undone without reflog

**Safer alternatives:**
- \`git stash\` — save changes temporarily
- \`git reset --soft\` — keep changes staged
- \`git reset --mixed\` — keep changes unstaged
`,
  },
  {
    name: 'rm-rf-root',
    event: 'bash',
    pattern: 'rm\\s+-rf\\s+/|rm\\s+-rf\\s+root',
    severity: 'critical',
    message: `⚠️ **rm -rf / or root detected**

This command attempts to delete the entire filesystem.

**This will destroy your system.**

**STOP — do not proceed.**
`,
  },
  {
    name: 'dd-destroy',
    event: 'bash',
    pattern: 'dd\\s+.*if=.*of=',
    severity: 'critical',
    message: `⚠️ **dd with input/output files detected**

Direct disk operations can permanently destroy data.

**Why dangerous:**
- \`dd\` bypasses all safety checks
- Wrong device = complete data loss
- No confirmation prompts

**Safer alternatives:**
- Use \`cp\` or \`rsync\` for file copies
- Use disk imaging tools with verification
`,
  },
  {
    name: 'chmod-777',
    event: 'bash',
    pattern: 'chmod\\s+.*-R\\s+777',
    severity: 'medium',
    message: `⚠️ **chmod -R 777 detected**

World-writable permissions on files or directories.

**Why dangerous:**
- Makes files executable by anyone
- Security risk — any user can modify
- Common target for malware

**Safer alternatives:**
- \`chmod 755\` for directories
- \`chmod 644\` for files
- \`chmod 600\` for sensitive files
`,
  },
  {
    name: 'git-push-force',
    event: 'bash',
    pattern: 'git\\s+push\\s+.*--force|git\\s+push\\s+.*-f\\s',
    severity: 'high',
    message: `⚠️ **git push --force detected**

Force-pushing rewrites remote history.

**Why dangerous:**
- Overwrites remote branch history
- Can destroy teammates' commits
- Violates collaboration norms

**Safer alternatives:**
- \`git push --force-with-lease\` — safer force push
- Use pull requests instead of direct pushes
- Discuss with team before force-pushing
`,
  },
  {
    name: 'fork-bomb',
    event: 'bash',
    pattern: ':\\(\\)\\{:\\|:\\&\\};:|\\b:\\(\\)\\{:\\|:&\\};:|fork\\(\\)|while\\s*\\(.*\\)\\s*fork\\s*;',
    severity: 'critical',
    message: `⚠️ **Fork bomb or recursive process creation detected**

This will spawn unlimited processes and crash the system.

**STOP — this will freeze or crash your machine.**
`,
  },
];

// ── Read audit log ───────────────────────────────────────────────────────────
function readAudit() {
  if (!existsSync(AUDIT_LOG)) return [];
  return readFileSync(AUDIT_LOG, 'utf-8')
    .split('\n').filter(Boolean)
    .map(l => { try { return JSON.parse(l); } catch { return null; } })
    .filter(Boolean);
}

// ── Read existing hookify rules ──────────────────────────────────────────────
function readExistingRules() {
  if (!existsSync(RULES_DIR)) return new Set();
  const files = readdirSync(RULES_DIR)
    .filter(f => f.startsWith('hookify.') && f.endsWith('.local.md'));
  const names = new Set();
  for (const f of files) {
    const content = readFileSync(resolve(RULES_DIR, f), 'utf-8');
    const nameMatch = content.match(/^name:\s*(.+)$/m);
    if (nameMatch) names.add(nameMatch[1].trim());
  }
  return names;
}

// ── Scan audit for patterns ─────────────────────────────────────────────────
function scanAudit(audit, patterns) {
  const results = [];
  for (const dp of patterns) {
    const regex = new RegExp(dp.pattern, 'i');
    const matches = audit.filter(e => {
      const cmd = e.tool_input_preview || '';
      return regex.test(cmd);
    });
    results.push({ ...dp, count: matches.length, examples: matches.slice(0, 3).map(e => e.tool_input_preview) });
  }
  return results;
}

// ── Generate hookify rule file ─────────────────────────────────────────────
function generateRule(name, event, pattern, message) {
  const safeName = name.replace(/[^a-z0-9-]/g, '-');
  return `---
name: ${safeName}
enabled: true
event: ${event}
pattern: ${pattern}
---

${message}`;
}

// ── Main ─────────────────────────────────────────────────────────────────────
function main() {
  const args = {};
  for (let i = 0; i < process.argv.length; i++) {
    if (process.argv[i].startsWith('--')) {
      const k = process.argv[i].slice(2);
      args[k] = process.argv[i + 1] && !process.argv[i + 1].startsWith('--') ? process.argv[i + 1] : true;
      if (typeof args[k] === 'string' && args[k] !== true) i++;
    }
  }

  const audit = readAudit();
  const existing = readExistingRules();
  const results = scanAudit(audit, DANGEROUS_PATTERNS);

  console.log(`\nOMC Hook Backfill Scanner`);
  console.log(`  Audit entries: ${audit.length}`);
  console.log(`  Existing rules: ${existing.size}\n`);

  const missing = results.filter(r => !existing.has(r.name));
  const covered = results.filter(r => existing.has(r.name));
  const detected = results.filter(r => r.count > 0);

  console.log(`=== Coverage ===`);
  for (const r of covered) {
    console.log(`  ✅ ${r.name} (covered, ${r.count}x in audit)`);
  }
  for (const r of missing) {
    console.log(`  ⬜ ${r.name} (missing)`);
  }

  if (detected.length > 0) {
    console.log(`\n=== Detected in audit log ===`);
    for (const r of detected) {
      console.log(`  ⚠️  ${r.name}: ${r.count}x`);
      for (const ex of r.examples) {
        console.log(`      → ${ex}`);
      }
    }
  }

  if (missing.length > 0) {
    console.log(`\n=== Missing rules ===`);
    for (const r of missing) {
      console.log(`  ${r.name}: \`${r.pattern}\` (${r.severity})`);
    }

    if (args.apply) {
      console.log(`\n=== Applying rules ===`);
      for (const r of missing) {
        const rule = generateRule(r.name, r.event, r.pattern, r.message);
        const path = resolve(RULES_DIR, `hookify.${r.name}.local.md`);
        writeFileSync(path, rule, 'utf-8');
        console.log(`  ✅ created: ${path}`);
      }
    } else {
      console.log(`\nRun with --apply to generate missing rules.`);
    }
  }
}

main();
