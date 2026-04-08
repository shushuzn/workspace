#!/usr/bin/env node
/**
 * OMC Hook Self-Improvement
 * Analyzes hook audit log → generates rule suggestions via LLM → can auto-apply.
 * Usage:
 *   node hook-self-improve.mjs --dry-run   (analyze + show suggestions, no apply)
 *   node hook-self-improve.mjs --apply     (analyze + show suggestions + prompt to apply)
 *   node hook-self-improve.mjs --auto-apply (fully automatic, apply all suggestions)
 */
import { existsSync, readFileSync, writeFileSync, mkdirSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const LOG_PATH = resolve(__dirname, '../state/hook-audit.jsonl');
const PATTERNS_PATH = resolve(__dirname, '../state/hook-patterns.json');
const RULES_DIR = resolve(__dirname, '../../.claude');

// ── Parse args ───────────────────────────────────────────────────────────────
const args = parseArgs(process.argv.slice(2));
const dryRun = args['dry-run'] || args.dryrun;
const autoApply = args['auto-apply'] || args.autoapply;
const apply = args.apply;
const minCount = parseInt(args['min-count'] || '2'); // Lowered from 3 — 2 occurrences is enough

// ── Read audit log ──────────────────────────────────────────────────────────
function readEntries() {
  if (!existsSync(LOG_PATH)) return [];
  const raw = readFileSync(LOG_PATH, 'utf-8');
  return raw.split('\n').filter(Boolean).map(l => {
    try { return JSON.parse(l); } catch { return null; }
  }).filter(Boolean);
}

function clusterEntries(entries) {
  const groups = {};
  for (const entry of entries) {
    if (entry.outcome !== 'blocked' && entry.outcome !== 'warned') continue;
    const cmd = entry.command || '';
    // Use first 40 chars of command/pattern as cluster key
    const k = `${entry.tool || '?'}|${(entry.pattern || cmd).slice(0, 40)}`;
    if (!groups[k]) groups[k] = [];
    groups[k].push(entry);
  }
  return groups;
}

// ── LLM Suggestion Generator ─────────────────────────────────────────────────
async function generateSuggestions(clusters) {
  // Group summary for LLM
  const clusterList = Object.entries(clusters).map(([key, entries]) => {
    const [tool, ...rest] = key.split('|');
    const pattern = rest.join('|');
    const uniqueCmds = [...new Set(entries.map(e => e.command).filter(Boolean))];
    const uniqueFiles = [...new Set(entries.map(e => e.filePath).filter(Boolean))];
    return { tool, pattern, count: entries.length, uniqueCmds, uniqueFiles };
  }).filter(c => c.count >= minCount);

  if (clusterList.length === 0) return [];

  const prompt = `You are a coding standards assistant. Generate hookify rules for the following repeated patterns.
Rules must be YAML format with name/enabled/event/pattern/message.
Return ONLY valid YAML without any explanation.

Patterns detected in audit log:
${clusterList.map(c => `Tool: ${c.tool} | Pattern: "${c.pattern}" | Occurrences: ${c.count} | Examples: ${c.uniqueCmds.join(', ') || c.uniqueFiles.join(', ')}`).join('\n')}

Generate hookify rules (one per pattern).`;

  const suggestions = [];
  for (const cluster of clusterList) {
    try {
      const result = await callLLM(prompt, cluster);
      if (result) suggestions.push({ cluster, rule: result });
    } catch {
      // LLM failed — skip this cluster
    }
  }
  return suggestions;
}

async function callLLM(clusterInfo, maxTokens = 512) {
  // Try gemma4:e2b (known working) or minimax API
  const url = 'http://127.0.0.1:11434/api/generate';
  const model = 'gemma4:e2b';

  const payload = {
    model,
    prompt: `Generate a hookify rule YAML for this repeated pattern.
Tool: ${clusterInfo.tool}
Pattern: "${clusterInfo.pattern}"
Occurrences: ${clusterInfo.count}
Example commands: ${clusterInfo.uniqueCmds.join(', ')}

Return ONLY valid YAML like:
---
name: warn-xxx
enabled: true
event: bash
pattern: some-regex
---
Message text here.`,
    options: { num_predict: maxTokens },
    stream: false,
  };

  try {
    const { default: fetch } = await import('fetch');
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) return null;
    const json = await res.json();
    return json.response?.trim() || null;
  } catch {
    return null;
  }
}

// ── Dangerous pattern detection ──────────────────────────────────────────────
const DANGEROUS_PREFIXES = [
  { prefix: 'git clean', name: 'git-clean-fd', severity: 'critical' },
  { prefix: 'rm -rf', name: 'rm-rf', severity: 'high' },
  { prefix: 'git reset --hard', name: 'git-reset-hard', severity: 'high' },
  { prefix: 'chmod -R 777', name: 'chmod-777', severity: 'medium' },
  { prefix: 'dd if=', name: 'dd-destroy', severity: 'critical' },
  { prefix: 'mkfs', name: 'mkfs', severity: 'critical' },
];

function detectDangerousPattern(pattern) {
  for (const dp of DANGEROUS_PREFIXES) {
    if (pattern.includes(dp.prefix) || pattern.includes(dp.name)) {
      return dp;
    }
  }
  return null;
}

function isDangerousCluster(cluster) {
  const combined = `${cluster.tool}|${cluster.pattern}`.toLowerCase();
  for (const dp of DANGEROUS_PREFIXES) {
    if (combined.includes(dp.prefix.toLowerCase()) || combined.includes(dp.name)) {
      return dp;
    }
  }
  return null;
}

function autoGenerateDangerousRule(cluster) {
  const dp = isDangerousCluster(cluster);
  if (!dp) return null;

  const ruleName = `prevent-${dp.name}`;
  const slug = ruleName.toLowerCase().replace(/[^a-z0-9-]/g, '-');
  const rulePath = resolve(RULES_DIR, `hookify.${slug}.local.md`);

  if (existsSync(rulePath)) return null; // Don't overwrite existing rules

  // Escape pattern for YAML regex
  const escaped = cluster.pattern.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const example = cluster.uniqueCmds[0] || cluster.uniqueFiles[0] || '';

  const yaml = `---
name: ${ruleName}
enabled: true
event: bash
pattern: ${escaped || dp.prefix}
---

**危险操作：${dp.name}** (${dp.severity} severity)

该命令具有破坏性。${example ? `示例：\`${example.slice(0, 80)}\`` : ''}

**替代方案**：
- 使用 \`--dry-run\` / \`-n\` 预览效果
- 分步执行而不是 combined flags（如 \`git clean -fd\` → 先 \`-n\` 预览再执行）
`;

  try {
    writeFileSync(rulePath, yaml, 'utf-8');
    return { ok: true, path: rulePath, ruleName };
  } catch (e) {
    return { ok: false, error: e.message };
  }
}

// ── Apply rules ───────────────────────────────────────────────────────────────
function generateRuleFilename(name) {
  // Convert "warn-dangerous-rm" → "warn-dangerous-rm.local.md"
  return `${name.toLowerCase().replace(/[^a-z0-9-]/g, '-')}.local.md`;
}

function extractRuleName(yaml) {
  const match = yaml.match(/^name:\s*(.+)$/m);
  return match ? match[1].trim() : null;
}

function applyRule(yamlContent) {
  const ruleName = extractRuleName(yamlContent);
  if (!ruleName) return { ok: false, error: 'Could not parse rule name from YAML' };

  const filename = generateRuleFilename(ruleName);
  const rulePath = resolve(RULES_DIR, `hookify.${filename}`);

  // Backup existing
  if (existsSync(rulePath)) {
    const backup = rulePath + `.bak.${Date.now()}`;
    writeFileSync(backup, readFileSync(rulePath, 'utf-8'), 'utf-8');
  }

  writeFileSync(rulePath, yamlContent, 'utf-8');
  return { ok: true, path: rulePath };
}

// ── Main ────────────────────────────────────────────────────────────────────
async function main() {
  console.log(`\n${'='.repeat(56)}`);
  console.log('  🛠  OMC Hook Self-Improvement');
  console.log(`${'='.repeat(56)}\n`);

  const entries = readEntries();
  console.log(`  Audit entries: ${entries.length}`);
  if (entries.length === 0) {
    console.log('  No audit entries found. Run some tasks first.');
    console.log('  Then re-run this script.\n');
    return;
  }

  const clusters = clusterEntries(entries);
  console.log(`  Clusters (blocked/warned): ${Object.keys(clusters).length}`);

  const filteredClusters = Object.fromEntries(
    Object.entries(clusters).filter(([, e]) => e.length >= minCount)
  );
  console.log(`  Clusters with count≥${minCount}: ${Object.keys(filteredClusters).length}\n`);

  if (Object.keys(filteredClusters).length === 0) {
    console.log('  ✅ No recurring patterns found. Nothing to improve.\n');
    return;
  }

  const suggestions = await generateSuggestions(filteredClusters);
  console.log(`  LLM suggestions: ${suggestions.length}\n`);

  if (suggestions.length === 0) {
    console.log('  ⚠️  Could not generate suggestions (LLM unavailable or error).');
    console.log('  Showing raw clusters instead:\n');
    for (const [key, entries] of Object.entries(filteredClusters)) {
      const [tool, ...rest] = key.split('|');
      console.log(`  📌 [${entries.length}x] ${tool}: ${rest.join('|')}`);
    }
    console.log();
    return;
  }

  // First pass: auto-apply dangerous patterns (count >= 2, no LLM needed)
  for (const [key, entries] of Object.entries(filteredClusters)) {
    const [tool, ...rest] = key.split('|');
    const pattern = rest.join('|');
    const cluster = { tool, pattern, count: entries.length, uniqueCmds: [...new Set(entries.map(e => e.command).filter(Boolean))], uniqueFiles: [...new Set(entries.map(e => e.filePath).filter(Boolean))] };
    const dp = isDangerousCluster(cluster);
    if (dp && entries.length >= 2) {
      const result = autoGenerateDangerousRule(cluster);
      if (result?.ok) {
        console.log(`  🔴 AUTO-APPLIED [${entries.length}x] ${dp.name} → ${result.path}`);
      }
    }
  }

  for (const { cluster, rule } of suggestions) {
    const ruleName = extractRuleName(rule) || 'unknown';
    console.log(`  📌 [${cluster.count}x] ${cluster.tool}: ${cluster.pattern}`);
    console.log(`     Suggested rule: ${ruleName}`);
    if (autoApply) {
      const result = applyRule(rule);
      if (result.ok) {
        console.log(`     ✅ Auto-applied → ${result.path}`);
      } else {
        console.log(`     ❌ Failed to apply: ${result.error}`);
      }
    } else if (apply) {
      console.log(`     To apply: ${apply ? 'manual' : 'dry-run mode'}`);
      console.log(`\n${rule}\n`);
    } else {
      console.log(`     (dry-run — not applied)\n${rule}\n`);
    }
  }

  if (autoApply) {
    console.log(`\n  ✅ Self-improvement complete. New rules saved to:`);
    console.log(`     ${RULES_DIR}/hookify.*.local.md\n`);
  } else if (apply) {
    console.log(`\n  Run with --auto-apply to apply all suggestions.\n`);
  } else {
    console.log(`\n  Run with --apply to interactively apply suggestions.\n`);
    console.log(`  Run with --auto-apply to apply all automatically.\n`);
  }
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

main().catch(err => { console.error(err); process.exit(1); });
