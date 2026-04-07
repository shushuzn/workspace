/**
 * hub-bridge-sync.mjs — Sync multi-agent-hub debate results into knowledge-bridge graph
 *
 * Reads: debates/*.json (transcript entries), memory-store.jsonl (summaries)
 * Outputs: hub-debates-graph.json (knowledge-bridge importable node/edge format)
 *
 * Usage: node scripts/hub-bridge-sync.mjs [--output ../knowledge-bridge/data/hub-debates-graph.json]
 */
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { parseArgs } from 'util';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const DEBATES_DIR = path.join(ROOT, 'debates');
const MEMORY_FILE = path.join(ROOT, 'memory-store.jsonl');

const { values } = parseArgs({
  args: process.argv.slice(2),
  options: {
    output: { type: 'string', default: path.join(ROOT, 'knowledge-bridge-data', 'hub-debates-graph.json') },
    hubData: { type: 'string', default: '../knowledge-bridge/data/hub-debates-graph.json' },
  },
});

// ─── Load debates ───────────────────────────────────────────
function loadDebates() {
  if (!fs.existsSync(DEBATES_DIR)) return [];
  return fs.readdirSync(DEBATES_DIR)
    .filter(f => f.startsWith('debate_') && f.endsWith('.json'))
    .map(f => {
      try {
        return JSON.parse(fs.readFileSync(path.join(DEBATES_DIR, f), 'utf8'));
      } catch { return null; }
    })
    .filter(Boolean);
}

// ─── Load memory summaries ──────────────────────────────────
function loadSummaries() {
  if (!fs.existsSync(MEMORY_FILE)) return [];
  return fs.readFileSync(MEMORY_FILE, 'utf8')
    .trim()
    .split('\n')
    .filter(Boolean)
    .map(line => { try { return JSON.parse(line); } catch { return null; } })
    .filter(Boolean);
}

// ─── Extract key claims from transcript ────────────────────
function extractClaims(transcript) {
  const claims = [];
  const seen = new Set();
  for (const entry of transcript || []) {
    const text = (entry.text || '').replace(/\x1b\[[0-9;]*m/g, '').trim();
    if (!text || text.length < 20) continue;
    // Skip error/warning messages
    if (text.includes('没有任何可用 LLM') || text.includes('no available')) continue;
    // Deduplicate by first 60 chars
    const key = text.slice(0, 60);
    if (seen.has(key)) continue;
    seen.add(key);
    claims.push({ persona: entry.persona?.name || 'unknown', text, temp: entry.temp });
  }
  return claims;
}

// ─── Build graph ────────────────────────────────────────────
function buildGraph() {
  const debates = loadDebates();
  const summaries = loadSummaries();

  const nodes = [];
  const edges = [];
  const nodeIdSet = new Set();

  function addNode(id, name, type, description, meta = {}) {
    if (nodeIdSet.has(id)) return;
    nodeIdSet.add(id);
    nodes.push({ id, name, type, description, ...meta });
  }

  function addEdge(source, target, label = '') {
    edges.push({ source, target, label });
  }

  // Add debate topic nodes + claim nodes
  for (const debate of debates) {
    const topicId = `debate_${debate.topic.replace(/\s+/g, '_')}`;
    const topicName = debate.topic;
    const modeLabel = debate.mode || 'discuss';
    const timestamp = debate.timestamp || '';

    // Topic node
    addNode(topicId, topicName, 'debate_topic',
      `辩论话题: ${topicName} | 模式: ${modeLabel} | 轮次: ${debate.rounds || 1} | 时间: ${timestamp.slice(0, 10)}`,
      { domain: 'multi-agent-debate', tags: [modeLabel, 'debate'] }
    );

    // Extract claims as sub-nodes, link to topic
    const claims = extractClaims(debate.transcript);
    for (let i = 0; i < Math.min(claims.length, 10); i++) {
      const claim = claims[i];
      const claimId = `${topicId}_claim_${i}`;
      const claimText = claim.text.slice(0, 200);
      addNode(claimId, `${claim.persona}: ${claim.text.slice(0, 50)}...`,
        'debate_claim', claimText,
        { domain: 'multi-agent-debate', tags: [claim.persona], source: topicName }
      );
      addEdge(topicId, claimId, 'contains_claim');
    }

    // Link to summary if exists
    const summary = summaries.find(s => s.topic === topicName);
    if (summary) {
      const summaryId = `summary_${topicName.replace(/\s+/g, '_')}`;
      addNode(summaryId, `总结: ${topicName}`, 'debate_summary',
        summary.summary || '',
        { domain: 'multi-agent-debate', tags: ['summary'] }
      );
      addEdge(topicId, summaryId, 'has_summary');
    }
  }

  // Add summary nodes that don't have a matching debate file
  const debateTopics = new Set(debates.map(d => d.topic));
  for (const summary of summaries) {
    if (debateTopics.has(summary.topic)) continue;
    const summaryId = `summary_${summary.topic.replace(/\s+/g, '_')}`;
    addNode(summaryId, `总结: ${summary.topic}`, 'debate_summary',
      summary.summary || '',
      { domain: 'multi-agent-debate', tags: ['summary', 'standalone'] }
    );
  }

  return { nodes, edges };
}

// ─── Main ──────────────────────────────────────────────────
const graph = buildGraph();
const outputPath = path.resolve(values.output);
const outputDir = path.dirname(outputPath);
fs.mkdirSync(outputDir, { recursive: true });
fs.writeFileSync(outputPath, JSON.stringify(graph, null, 2), 'utf8');

console.log(`Synced ${graph.nodes.length} nodes, ${graph.edges.length} edges`);
console.log(`Output: ${outputPath}`);
console.log(`Topics: ${graph.nodes.filter(n => n.type === 'debate_topic').length}`);
console.log(`Claims: ${graph.nodes.filter(n => n.type === 'debate_claim').length}`);
console.log(`Summaries: ${graph.nodes.filter(n => n.type === 'debate_summary').length}`);
