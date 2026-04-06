#!/usr/bin/env node
/**
 * generate-levels.mjs — Procedural Level Generator for Agent Arena
 *
 * Generates level configs using LLM based on difficulty tier.
 * Falls back to random generation if LLM unavailable.
 *
 * Usage:
 *   node scripts/generate-levels.mjs              # generate all tiers
 *   node scripts/generate-levels.mjs --tier easy   # generate specific tier
 *   node scripts/generate-levels.mjs --count 5     # count per tier (default 3)
 *   node scripts/generate-levels.mjs --llm         # use LLM generation
 */
import { writeFileSync, existsSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..');
const LEVELS_DIR = join(ROOT, 'src', 'levels');
const OLLAMA_URL = 'http://127.0.0.1:11434/api/generate';

const args = parseArgs(process.argv.slice(2));
const TIER = args.tier || 'all';
const COUNT = parseInt(args.count || '3');
const USE_LLM = args.llm || false;

// ── Level templates by difficulty ───────────────────────────────────────────

const TERRAIN_TYPES = ['grass', 'desert', 'snow', 'volcano', 'forest', 'cave', 'space', 'city'];
const ENEMY_TYPES = ['goblin', 'dragon', 'robot', 'spirit', 'beast', 'undead', 'demon', 'elemental'];
const OBJECTIVE_TYPES = ['defeat_all', 'survive_waves', 'capture_point', 'escort', 'collect'];
const BUFF_TYPES = ['attack_up', 'defense_up', 'speed_up', 'heal', 'shield', 'critical_up'];
const DEBUFF_TYPES = ['poison', 'burn', 'freeze', 'curse', 'blind', 'slow'];

const ADJECTIVES = ['Ancient', 'Frozen', 'Burning', 'Dark', 'Crystal', 'Thunder', 'Shadow', 'Golden', 'Storm', 'Abyssal'];
const NOUNS = ['Fortress', 'Temple', 'Arena', 'Colosseum', 'Ruin', 'Citadel', 'Pyramid', 'Tower', 'Sanctum', 'Vault'];

function randomChoice(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function genId(prefix) {
  return `${prefix}_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 6)}`;
}

// ── Difficulty tier configs ──────────────────────────────────────────────────

const TIERS = {
  easy: {
    name: 'Easy',
    emoji: '🌱',
    enemyLevelRange: [1, 5],
    waveCount: [2, 3],
    enemyCountRange: [2, 4],
    enemyStats: { hp: [20, 40], atk: [5, 10], def: [2, 5] },
    buffCount: [1, 2],
    debuffCount: [0, 1],
    terrain: ['grass', 'forest'],
    scoreMultiplier: 1,
  },
  medium: {
    name: 'Medium',
    emoji: '⚔️',
    enemyLevelRange: [5, 15],
    waveCount: [3, 5],
    enemyCountRange: [3, 6],
    enemyStats: { hp: [40, 80], atk: [10, 20], def: [5, 12] },
    buffCount: [1, 3],
    debuffCount: [1, 2],
    terrain: ['desert', 'city', 'ruins'],
    scoreMultiplier: 2,
  },
  hard: {
    name: 'Hard',
    emoji: '🔥',
    enemyLevelRange: [15, 30],
    waveCount: [4, 6],
    enemyCountRange: [5, 8],
    enemyStats: { hp: [80, 150], atk: [20, 40], def: [12, 25] },
    buffCount: [0, 2],
    debuffCount: [2, 3],
    terrain: ['volcano', 'cave', 'abyss'],
    scoreMultiplier: 3,
  },
  extreme: {
    name: 'Extreme',
    emoji: '💀',
    enemyLevelRange: [30, 50],
    waveCount: [5, 8],
    enemyCountRange: [6, 10],
    enemyStats: { hp: [150, 300], atk: [40, 80], def: [25, 50] },
    buffCount: [0, 1],
    debuffCount: [3, 5],
    terrain: ['space', 'void', 'abyss'],
    scoreMultiplier: 5,
  },
};

function generateEnemy(tier, level) {
  const t = TIERS[tier];
  const type = randomChoice(ENEMY_TYPES);
  const stats = t.enemyStats;
  const levelMult = 1 + (level - t.enemyLevelRange[0]) / t.enemyLevelRange[0];
  return {
    id: genId('enemy'),
    type,
    name: `${randomChoice(ADJECTIVES)} ${type.charAt(0).toUpperCase() + type.slice(1)}`,
    level,
    stats: {
      hp: Math.round(randomInt(stats.hp[0], stats.hp[1]) * levelMult),
      atk: Math.round(randomInt(stats.atk[0], stats.atk[1]) * levelMult),
      def: Math.round(randomInt(stats.def[0], stats.def[1]) * levelMult),
      speed: randomInt(10, 30) + level,
    },
    skills: [],
    reward: Math.round(level * 10 * t.scoreMultiplier),
  };
}

function generateLevel(tier, index) {
  const t = TIERS[tier];
  const levelNum = index + 1;
  const terrain = randomChoice(t.terrain);
  const waves = randomInt(t.waveCount[0], t.waveCount[1]);
  const baseEnemyLevel = randomInt(t.enemyLevelRange[0], t.enemyLevelRange[1]);

  const enemies = [];
  for (let w = 0; w < waves; w++) {
    const waveEnemyCount = randomInt(t.enemyCountRange[0], t.enemyCountRange[1]);
    const wave = {
      wave: w + 1,
      enemies: [],
    };
    for (let e = 0; e < waveEnemyCount; e++) {
      const scaling = 1 + w * 0.1;
      wave.enemies.push(generateEnemy(tier, Math.round(baseEnemyLevel * scaling)));
    }
    enemies.push(wave);
  }

  const buffs = [];
  for (let b = 0; b < randomInt(t.buffCount[0], t.buffCount[1]); b++) {
    buffs.push({ id: genId('buff'), type: randomChoice(BUFF_TYPES), value: randomInt(10, 30) });
  }

  const debuffs = [];
  for (let d = 0; d < randomInt(t.debuffCount[0], t.debuffCount[1]); d++) {
    debuffs.push({ id: genId('debuff'), type: randomChoice(DEBUFF_TYPES), value: randomInt(5, 20) });
  }

  return {
    id: `${tier}_level_${levelNum}`,
    name: `${randomChoice(ADJECTIVES)} ${randomChoice(NOUNS)}`,
    tier,
    terrain,
    difficulty: t.name,
    waves,
    enemies,
    buffs,
    debuffs,
    objectives: [{ type: randomChoice(OBJECTIVE_TYPES), description: `Complete ${t.name} challenge` }],
    rewards: {
      exp: Math.round(100 * levelNum * t.scoreMultiplier),
      coins: Math.round(50 * levelNum * t.scoreMultiplier),
      gems: tier === 'extreme' ? randomInt(1, 3) : tier === 'hard' ? randomInt(0, 2) : 0,
    },
    unlocksAt: tier === 'easy' ? 1 : tier === 'medium' ? 5 : tier === 'hard' ? 15 : 35,
    scoreMultiplier: t.scoreMultiplier,
  };
}

// ── LLM enhancement ─────────────────────────────────────────────────────────

async function llmEnhanceLevel(level) {
  const prompt = `You are a creative game designer. Enhance this game level config with thematic descriptions and special mechanics.

Level so far:
${JSON.stringify(level, null, 2)}

Return ONLY valid JSON like:
{
  "theme": "short thematic description",
  "narrative": "2-sentence backstory for this level",
  "specialMechanics": ["mechanic1", "mechanic2"],
  "ambientEffects": ["effect1", "effect2"]
}`;

  try {
    const { default: fetch } = await import('fetch');
    const res = await fetch(OLLAMA_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'qwen3.5:0.8b',
        prompt,
        options: { num_predict: 300 },
        stream: false,
      }),
    });
    if (!res.ok) return null;
    const json = await res.json();
    const response = json.response?.trim();
    if (!response) return null;
    return JSON.parse(response);
  } catch {
    return null;
  }
}

// ── Save level ──────────────────────────────────────────────────────────────

function saveLevel(level) {
  mkdirSync(LEVELS_DIR, { recursive: true });
  const path = join(LEVELS_DIR, `${level.id}.json`);
  writeFileSync(path, JSON.stringify(level, null, 2), 'utf-8');
  console.log(`  Saved: ${level.id}.json`);
  return path;
}

// ── Main ────────────────────────────────────────────────────────────────────

async function main() {
  console.log(`\n  Agent Arena Level Generator\n  ${'─'.repeat(44)}`);
  console.log(`  Tier: ${TIER}  |  Count per tier: ${COUNT}  |  LLM: ${USE_LLM ? 'on' : 'off'}`);
  console.log(`  Output: ${LEVELS_DIR}\n`);

  mkdirSync(LEVELS_DIR, { recursive: true });

  const tiers = TIER === 'all' ? Object.keys(TIERS) : [TIER];

  for (const t of tiers) {
    if (!TIERS[t]) { console.warn(`Unknown tier: ${t}`); continue; }
    console.log(`  Generating ${COUNT}x ${t} levels...`);
    for (let i = 0; i < COUNT; i++) {
      let level = generateLevel(t, i);
      if (USE_LLM) {
        const enhanced = await llmEnhanceLevel(level);
        if (enhanced) {
          level = { ...level, theme: enhanced.theme, narrative: enhanced.narrative, specialMechanics: enhanced.specialMechanics, ambientEffects: enhanced.ambientEffects };
        }
      }
      saveLevel(level);
    }
  }

  console.log(`\n  Done. ${COUNT * tiers.length} levels generated in ${LEVELS_DIR}\n`);
}

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

main().catch(console.error);
