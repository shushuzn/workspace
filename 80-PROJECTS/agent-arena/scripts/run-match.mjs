#!/usr/bin/env node
/**
 * run-match.mjs — Agent Arena Match Runner
 * Runs head-to-head matches between two agents and scores via MiniMax API.
 *
 * Usage:
 *   node scripts/run-match.mjs opencli task-orchestrator
 *   node scripts/run-match.mjs opencli task-orchestrator --rounds 5
 *   node scripts/run-match.mjs opencli task-orchestrator --prompt "Explain quantum computing"
 *   node scripts/run-match.mjs opencli task-orchestrator --verbose
 */

import { readFileSync, existsSync } from 'fs';
import { execSync } from 'child_process';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const WORKSPACE_ROOT = join(__dirname, '..', '..');

const args = process.argv.slice(2);

function parseArgs() {
  const out = { agentA: null, agentB: null, rounds: 3, prompt: null, verbose: false };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--rounds' && i + 1 < args.length) { out.rounds = parseInt(args[++i]); }
    else if (args[i] === '--prompt' && i + 1 < args.length) { out.prompt = args[++i]; }
    else if (args[i] === '--verbose') { out.verbose = true; }
    else if (!out.agentA) { out.agentA = args[i]; }
    else if (!out.agentB) { out.agentB = args[i]; }
  }
  return out;
}

const { agentA, agentB, rounds, prompt, verbose } = parseArgs();

if (!agentA || !agentB) {
  console.error('Usage: node scripts/run-match.mjs <agentA> <agentB> [--rounds N] [--prompt TEXT] [--verbose]');
  console.error('\nAvailable agents (from workspace manifests):\n');
  const manifests = [
    join(WORKSPACE_ROOT, '80-PROJECTS/opencli/manifest.json'),
    join(WORKSPACE_ROOT, '80-PROJECTS/task-orchestrator/manifest.json'),
    join(WORKSPACE_ROOT, '80-PROJECTS/multi-agent-discuss/manifest.json'),
  ];
  for (const m of manifests) {
    if (existsSync(m)) {
      try {
        const data = JSON.parse(readFileSync(m, 'utf8'));
        console.log(`  ${' '.repeat(20)} ${data.project.name.padEnd(25)} ${data.project.description?.slice(0, 50) || ''}`);
      } catch {}
    }
  }
  process.exit(1);
}

const DEFAULT_PROMPTS = [
  '解释量子计算的核心原理，用普通人都能理解的方式',
  '写一个Python函数来判断一个数是否为质数',
  '分析一下当前全球经济的主要风险点',
  '用JavaScript实现一个简单的防抖函数',
  '解释什么是RESTful API设计原则',
];

/** Load agent manifest */
async function loadManifest(name) {
  const candidates = [
    join(WORKSPACE_ROOT, '80-PROJECTS', name, 'manifest.json'),
    join(WORKSPACE_ROOT, '80-PROJECTS', name.replace(/-/g, '_'), 'manifest.json'),
  ];
  for (const p of candidates) {
    if (existsSync(p)) return JSON.parse(readFileSync(p, 'utf8'));
  }
  // Search workspace via fs (cross-platform)
  try {
    const { readdirSync } = await import('fs');
    const projectsDir = join(WORKSPACE_ROOT, '80-PROJECTS');
    const projects = readdirSync(projectsDir);
    for (const proj of projects) {
      const manifestPath = join(projectsDir, proj, 'manifest.json');
      if (existsSync(manifestPath)) {
        try {
          const data = JSON.parse(readFileSync(manifestPath, 'utf8'));
          if (data.project?.name === name) return data;
        } catch {}
      }
    }
  } catch {}
  return null;
}

/** Invoke agent via its manifest-defined CLI */
async function invokeAgent(manifest, promptText) {
  const { spawn } = await import('child_process');
  const cap = manifest.capabilities?.[0];
  if (!cap) return { output: '[no capabilities]', score: 0 };

  if (cap.type === 'cli' || cap.type === 'shell') {
    const { spawn } = await import('child_process').catch(() => require('child_process'));
    const bin = join(WORKSPACE_ROOT, '80-PROJECTS', manifest.project.name, 'src', 'cli.js');
    return new Promise(resolve => {
      const proc = spawn('node', [bin, ...cap.examples?.[0]?.split(' ').slice(1) || ['--help']], { timeout: 15000 });
      let stdout = '', stderr = '';
      proc.stdout?.on('data', d => stdout += d);
      proc.stderr?.on('data', d => stderr += d);
      proc.on('close', () => resolve({ output: stdout || stderr, score: 0 }));
      proc.on('error', e => resolve({ output: String(e), score: 0 }));
    });
  }

  // For adapter-type agents, just return prompt as output
  return { output: `[${manifest.project.name}] ${promptText.slice(0, 100)}`, score: 0 };
}

/** Score two outputs via MiniMax API */
async function scoreMatch(outputA, outputB, roundIdx) {
  const apiKey = process.env.MINIMAX_API_KEY || process.env.VITE_MINIMAX_API_KEY;
  if (!apiKey) {
    // Fallback: length-based tiebreaker
    return outputA.length > outputB.length ? 'A' : outputB.length > outputA.length ? 'B' : 'tie';
  }

  try {
    const { default: fetch } = await import('node-fetch');
    const res = await fetch('https://api.minimaxi.com/v1/chat/completions', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${apiKey}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'MiniMax-M2.7-highspeed',
        max_tokens: 50,
        messages: [
          { role: 'system', content: `你是一个公正的裁判，评判两个AI对同一问题的回答质量。回复只能是一个字母：A、B或tie（平局）。评判标准：准确性(40%)、清晰度(30%)、实用性(30%)。` },
          { role: 'user', content: `Round ${roundIdx + 1}\n\nAgent A输出:\n${String(outputA).slice(0, 500)}\n\nAgent B输出:\n${String(outputB).slice(0, 500)}\n\n谁的回答更好？回复A、B或tie。` }
        ]
      })
    });
    const data = await res.json();
    const answer = (data.choices?.[0]?.message?.content || 'tie').trim().toLowerCase();
    if (answer.includes('a') && !answer.includes('b')) return 'A';
    if (answer.includes('b') && !answer.includes('a')) return 'B';
    return 'tie';
  } catch (e) {
    if (verbose) console.error('  [score error]', e.message);
    return 'tie';
  }
}

// ── Main ──────────────────────────────────────────────────────────────────────
console.log(`\n  Agent Arena Match Runner`);
console.log(`  ─────────────────────────────────`);
console.log(`  Agent A: ${agentA}`);
console.log(`  Agent B: ${agentB}`);
console.log(`  Rounds:  ${rounds}`);
console.log(`  Prompt:   ${prompt || '(random from pool)'}`);
console.log('');

const manifestA = loadManifest(agentA);
const manifestB = loadManifest(agentB);

if (!manifestA) { console.error(`  Agent A "${agentA}" not found (no manifest.json)`); process.exit(1); }
if (!manifestB) { console.error(`  Agent B "${agentB}" not found (no manifest.json)`); process.exit(1); }

let scoreA = 0, scoreB = 0, ties = 0;
const eloA = 1500, eloB = 1500;

for (let r = 0; r < rounds; r++) {
  const promptText = prompt || DEFAULT_PROMPTS[r % DEFAULT_PROMPTS.length];
  if (verbose) console.log(`\n  Round ${r + 1}/${rounds}: ${promptText.slice(0, 60)}...`);

  const [resA, resB] = await Promise.all([
    invokeAgent(manifestA, promptText),
    invokeAgent(manifestB, promptText),
  ]);

  const winner = await scoreMatch(resA.output, resB.output, r);

  if (verbose) {
    console.log(`    ${manifestA.project.name}: ${String(resA.output).slice(0, 80).replace(/\n/g, ' ')}`);
    console.log(`    ${manifestB.project.name}: ${String(resB.output).slice(0, 80).replace(/\n/g, ' ')}`);
    console.log(`    → Winner: ${winner}`);
  } else {
    process.stdout.write(`  Round ${r + 1}: ${winner === 'A' ? `✓ ${agentA}` : winner === 'B' ? `✓ ${agentB}` : '  tie'}\n`);
  }

  if (winner === 'A') scoreA++;
  else if (winner === 'B') scoreB++;
  else ties++;
}

// Elo update (simplified K=32)
const expectedA = 1 / (1 + 10 ** ((eloB - eloA) / 400));
const K = 32;
const actualA = scoreA / rounds;
const newEloA = Math.round(eloA + K * (actualA - expectedA));
const newEloB = Math.round(eloB + K * ((scoreB / rounds) - (1 - expectedA)));

console.log(`\n  ─────────────────────────────────`);
console.log(`  Result: ${scoreA} – ${ties} – ${scoreB}`);
console.log(`  Elo:    ${agentA} ${eloA}→${newEloA}  |  ${agentB} ${eloB}→${newEloB}`);
console.log('');
