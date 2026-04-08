#!/usr/bin/env node
/**
 * OMC CLAUDE.md Incremental Patcher
 * Appends rule changes to .omc/claude-patches/ instead of directly editing CLAUDE.md.
 * Prevents merge conflicts when CLAUDE.md is modified from multiple sessions.
 *
 * Usage:
 *   node claude-patch.mjs --add "New rule content" [--section SECTION]
 *   node claude-patch.mjs --list    (show pending patches)
 *   node claude-patch.mjs --apply   (merge patches into CLAUDE.md)
 *   node claude-patch.mjs --status  (show patch status)
 *
 * Format: Each patch is a .patch.md file in .omc/claude-patches/
 * Naming: YYYY-MM-DD-HHMMSS-[category].patch.md
 */
import {
  existsSync, readFileSync, writeFileSync,
  mkdirSync, readdirSync, unlinkSync, appendFileSync
} from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PATCH_DIR = resolve(__dirname, '../claude-patches');
const CLAUDE_MD = resolve(__dirname, '../../CLAUDE.md');
const STATE_FILE = resolve(__dirname, '../state/claude-patch-state.json');

const STATE = {
  get() {
    if (!existsSync(STATE_FILE)) return { applied: [], pending: [] };
    try { return JSON.parse(readFileSync(STATE_FILE, 'utf-8')); }
    catch { return { applied: [], pending: [] }; }
  },
  set(s) { writeFileSync(STATE_FILE, JSON.stringify(s, null, 2), 'utf-8'); }
};

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i++) {
    if (argv[i].startsWith('--')) {
      const key = argv[i].slice(2);
      args[key] = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : true;
    }
  }
  return args;
}

// ── Section definitions ──────────────────────────────────────────────────────
const SECTIONS = {
  'rules':      '## §1-§11 核心规则',
  'memory':     '## 记忆系统',
  'projects':   '## 项目',
  'feedback':   '## 反馈',
  'skills':     '## 技能',
  'appendix':   '## 附录',
  'general':    null, // append to end
};

// ── Write a patch file ──────────────────────────────────────────────────────
function writePatch(content, category = 'general') {
  if (!existsSync(PATCH_DIR)) mkdirSync(PATCH_DIR, { recursive: true });
  const ts = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
  const filename = `${ts}-${category}.patch.md`;
  const path = resolve(PATCH_DIR, filename);

  const patchContent = `---
name: claude-patch
created: ${new Date().toISOString()}
category: ${category}
---

# CLAUDE.md Patch (auto-generated)

${content}

---
_applied: false
_date: ${new Date().toISOString()}
`;

  writeFileSync(path, patchContent, 'utf-8');

  // Track in state
  const state = STATE.get();
  state.pending.push({ filename, path, category, created: new Date().toISOString() });
  STATE.set(state);

  console.log(`patch created: ${filename}`);
  return path;
}

// ── Apply all pending patches ────────────────────────────────────────────────
function applyPatches(dryRun = false) {
  const state = STATE.get();
  if (!existsSync(CLAUDE_MD)) {
    console.error(`CLAUDE.md not found at ${CLAUDE_MD}`);
    return;
  }

  const patches = state.pending.map(p => {
    const content = readFileSync(p.path, 'utf-8');
    // Extract content between first --- markers and end
    const match = content.match(/^---\n[\s\S]*?\n---\n([\s\S]*)/);
    return { ...p, content: match ? match[1].trim() : '' };
  }).filter(p => p.content);

  if (patches.length === 0) {
    console.log('no patches to apply');
    return;
  }

  let current = readFileSync(CLAUDE_MD, 'utf-8');

  for (const patch of patches) {
    if (dryRun) {
      console.log(`\n[DRY RUN] Would apply: ${patch.filename}`);
      console.log(`  Category: ${patch.category}`);
      console.log(`  Content preview: ${patch.content.slice(0, 80)}...`);
    } else {
      current += '\n\n' + patch.content;
      // Mark as applied
      state.applied.push(patch.filename);
      state.pending = state.pending.filter(p => p.filename !== patch.filename);
    }
  }

  if (!dryRun) {
    // Update version number in CLAUDE.md
    current = updateVersion(current);
    writeFileSync(CLAUDE_MD, current, 'utf-8');
    STATE.set(state);
    console.log(`applied ${patches.length} patches → CLAUDE.md`);
  }
}

function updateVersion(content) {
  // Increment version in first line: v1.X → v1.X+1
  return content.replace(/^(# CLAUDE.md 工作规范\s*>\s*\*\*版本\*\*：)(v\d+\.\d+)/,
    (m, prefix, ver) => {
      const parts = ver.split('.');
      parts[1] = parseInt(parts[1]) + 1;
      return `${prefix}v${parts.join('.')} | 自动补丁 #${parts[1]}`;
    });
}

// ── List pending patches ─────────────────────────────────────────────────────
function listPatches() {
  const state = STATE.get();
  const patchFiles = existsSync(PATCH_DIR)
    ? readdirSync(PATCH_DIR).filter(f => f.endsWith('.patch.md'))
    : [];

  console.log(`\n📋 OMC CLAUDE.md Patch Status`);
  console.log(`  CLAUDE.md: ${CLAUDE_MD}`);
  console.log(`  Patch dir: ${PATCH_DIR}`);
  console.log(`  Pending:   ${state.pending.length}`);
  console.log(`  Applied:  ${state.applied.length}`);

  if (state.pending.length > 0) {
    console.log(`\n  Pending patches:`);
    for (const p of state.pending) {
      console.log(`    • ${p.filename} (${p.category})`);
    }
  }

  if (state.applied.length > 0) {
    console.log(`\n  Recently applied:`);
    for (const f of state.applied.slice(-5)) {
      console.log(`    ✓ ${f}`);
    }
  }
  console.log();
}

// ── Quick add helper ────────────────────────────────────────────────────────
function quickAdd(text, category = 'general') {
  if (!text) {
    console.error('usage: --add "rule text" [--category rules|memory|projects|feedback|skills|appendix]');
    return;
  }
  writePatch(text, category);
}

// ── Main ────────────────────────────────────────────────────────────────────
async function main() {
  const args = parseArgs(process.argv.slice(2));

  if (args.list || args.status) {
    listPatches();
    return;
  }

  if (args.apply) {
    applyPatches(false);
    return;
  }

  if (args['dry-run']) {
    applyPatches(true);
    return;
  }

  if (args.add) {
    quickAdd(args.add, args.category || 'general');
    return;
  }

  // Default: show status
  listPatches();
  console.log(`Usage:`);
  console.log(`  --add "text" [--category X]   Add a new patch`);
  console.log(`  --list                         List pending patches`);
  console.log(`  --apply                         Merge patches into CLAUDE.md`);
  console.log(`  --dry-run                       Preview merge without applying`);
}

main().catch(e => { console.error(e.message); process.exit(1); });
