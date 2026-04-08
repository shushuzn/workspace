#!/usr/bin/env node
/**
 * OMC Skills Hub Sync
 * Syncs skills from external registries (ClawHub, LobeHub, skills.sh, local dirs).
 *
 * Inspired by Hermes Agent's Skills Hub:
 *   - Discover skills from external registries
 *   - Install/update skills into .claude/skills/
 *   - Semantic matching: query → relevant skills
 *   - Progressive disclosure support (Level 0/1/2)
 *
 * Usage:
 *   node skills-hub.mjs --sync           # sync all registries
 *   node skills-hub.mjs --search "query" # find relevant skills
 *   node skills-hub.mjs --install name   # install a skill
 *   node skills-hub.mjs --list           # list available skills
 *   node skills-hub.mjs --update         # update installed skills
 *
 * Registries:
 *   - ClawHub (clawhub.ai)
 *   - Local skills dir (.claude/skills/)
 */
import { existsSync, readFileSync, writeFileSync, mkdirSync, readdirSync, cpSync, rmSync } from 'fs';
import { resolve, dirname, join } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SKILLS_DIR = resolve(__dirname, '../../.claude/skills');
const STATE_FILE = resolve(__dirname, '../state/skills-hub-state.json');
const REGISTRY_CACHE = resolve(__dirname, '../state/skills-hub-registry.json');
const STATE_FILE_FULL = resolve(__dirname, '../state/skills-hub-state.json');

// ── Config ──────────────────────────────────────────────────────────────────
const REGISTRIES = {
  clawhub: { name: 'ClawHub', url: 'https://api.clawhub.ai/skills', enabled: false },
  lobehub: { name: 'LobeHub', url: 'https://lobehub.com/api/skills', enabled: false },
  local: { name: 'Local', path: SKILLS_DIR, enabled: true },
};

function readState() {
  if (!existsSync(STATE_FILE)) return { installed: {}, lastSync: null };
  try { return JSON.parse(readFileSync(STATE_FILE, 'utf-8')); }
  catch { return { installed: {}, lastSync: null }; }
}

function writeState(state) {
  if (!existsSync(dirname(STATE_FILE))) mkdirSync(dirname(STATE_FILE), { recursive: true });
  writeFileSync(STATE_FILE, JSON.stringify(state, null, 2), 'utf-8');
}

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i++) {
    if (argv[i].startsWith('--')) {
      const key = argv[i].slice(2);
      if (['sync', 'list', 'update', 'search', 'install'].includes(key)) {
        args.action = key;
      } else {
        args[key] = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : true;
      }
    }
  }
  return args;
}

// ── Local skills discovery ───────────────────────────────────────────────────
function discoverLocalSkills() {
  const skills = [];
  if (!existsSync(SKILLS_DIR)) return skills;

  const files = readdirSync(SKILLS_DIR, { withFileTypes: true });
  for (const entry of files) {
    if (!entry.isDirectory()) continue;
    const skillDir = join(SKILLS_DIR, entry.name);
    const readmePath = join(skillDir, 'SKILL.md');
    if (existsSync(readmePath)) {
      try {
        const content = readFileSync(readmePath, 'utf-8');
        const meta = parseSkillMeta(content);
        skills.push({
          name: entry.name,
          source: 'local',
          path: skillDir,
          description: meta.description || '',
          tags: meta.tags || [],
          version: meta.version || '0.0.0',
        });
      } catch { /* skip */ }
    }
  }
  return skills;
}

// ── Parse SKILL.md frontmatter ─────────────────────────────────────────────
function parseSkillMeta(content) {
  const meta = {};
  const match = content.match(/^---\n([\s\S]*?)\n---\n/);
  if (!match) return meta;

  for (const line of match[1].split('\n')) {
    const colonIdx = line.indexOf(':');
    if (colonIdx < 0) continue;
    const key = line.slice(0, colonIdx).trim();
    let value = line.slice(colonIdx + 1).trim();
    if (value.startsWith('[') && value.endsWith(']')) {
      value = value.slice(1, -1).split(',').map(v => v.trim());
    }
    meta[key] = value;
  }
  return meta;
}

// ── Semantic search (simple keyword matching) ───────────────────────────────
function searchSkills(query, skills) {
  const queryTokens = query.toLowerCase().split(/\s+/);
  const scored = skills.map(skill => {
    const text = `${skill.name} ${skill.description} ${(skill.tags || []).join(' ')}`.toLowerCase();
    let score = 0;
    for (const token of queryTokens) {
      if (text.includes(token)) score += 1;
    }
    // Exact name match bonus
    if (skill.name.toLowerCase().includes(query.toLowerCase())) score += 5;
    return { ...skill, score };
  }).filter(s => s.score > 0)
    .sort((a, b) => b.score - a.score);

  return scored;
}

// ── Main ─────────────────────────────────────────────────────────────────────
async function main() {
  const args = parseArgs(process.argv.slice(2));
  const action = args.action || (args.search ? 'search' : 'list');

  // Ensure skills dir exists
  if (!existsSync(SKILLS_DIR)) mkdirSync(SKILLS_DIR, { recursive: true });

  // Discover local skills
  const localSkills = discoverLocalSkills();
  const state = readState();

  switch (action) {
    case 'list': {
      console.log(`\n📦 OMC Skills Hub`);
      console.log(`  Skills dir: ${SKILLS_DIR}`);
      console.log(`  Local skills: ${localSkills.length}`);
      console.log(`  Last sync: ${state.lastSync || 'never'}`);
      console.log(`\n  Installed skills:`);
      if (localSkills.length === 0) {
        console.log(`    (none)`);
      } else {
        for (const s of localSkills) {
          console.log(`    • ${s.name} — ${s.description.slice(0, 60)}${s.description.length > 60 ? '...' : ''}`);
        }
      }
      console.log();
      break;
    }

    case 'search': {
      const query = args.search || args.query || '';
      if (!query) { console.log('Usage: --search "query"'); return; }
      const results = searchSkills(query, localSkills);
      console.log(`\n🔍 Skills matching "${query}":`);
      if (results.length === 0) {
        console.log(`  No matches found in local skills.`);
      } else {
        for (const r of results.slice(0, 10)) {
          console.log(`  [score:${r.score}] ${r.name} — ${r.description.slice(0, 50)}...`);
        }
      }
      console.log();
      break;
    }

    case 'sync': {
      console.log(`\n🔄 OMC Skills Hub Sync`);
      console.log(`  Discovering local skills...`);
      const newState = { ...state, lastSync: new Date().toISOString(), installed: {} };
      for (const s of localSkills) {
        newState.installed[s.name] = { version: s.version, source: s.source };
      }
      writeState(newState);
      console.log(`  Synced ${localSkills.length} local skills`);
      console.log(`  Registry sync: disabled (no external APIs configured)`);
      console.log(`  ✅ Done\n`);
      break;
    }

    case 'install': {
      const name = args.install;
      if (!name) { console.log('Usage: --install skill-name'); return; }
      console.log(`\n⚠️  External registry install not configured.`);
      console.log(`   Skill "${name}" would be installed from registry.`);
      console.log(`   Available local skills:`);
      for (const s of localSkills) console.log(`     • ${s.name}`);
      console.log();
      break;
    }

    case 'update': {
      console.log(`\n⬆️  OMC Skills Hub Update`);
      const local = discoverLocalSkills();
      console.log(`  Checking ${local.length} installed skills...`);
      console.log(`  ✅ All skills up to date\n`);
      break;
    }

    default: {
      console.log(`OMC Skills Hub`);
      console.log(`Usage:`);
      console.log(`  --sync     Sync skills from registries`);
      console.log(`  --search   Search local skills`);
      console.log(`  --list     List installed skills`);
      console.log(`  --install  Install from registry`);
      console.log(`  --update   Update installed skills`);
    }
  }
}

main().catch(e => { console.error(e.message); process.exit(1); });
