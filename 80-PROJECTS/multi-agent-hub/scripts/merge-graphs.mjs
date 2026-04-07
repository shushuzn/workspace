/**
 * merge-knowledge-graphs.mjs — Merge hub-debates-graph into pla-knowledge-graph
 *
 * Usage: node scripts/merge-knowledge-graphs.mjs
 * Reads: knowledge-bridge-data/hub-debates-graph.json + ../../knowledge-bridge/data/pla-knowledge-graph.json
 * Writes: knowledge-bridge-data/merged-knowledge-graph.json
 */
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const HUB_DATA = path.join(ROOT, 'knowledge-bridge-data');
// Walk up from multi-agent-hub → 80-PROJECTS → workspace → knowledge-bridge/data
const WORKSPACE_KB = path.resolve(ROOT, '..', '..', 'knowledge-bridge', 'data');

function loadJson(filepath) {
  try {
    return JSON.parse(fs.readFileSync(filepath, 'utf8'));
  } catch { return { nodes: [], edges: [] }; }
}

function mergeGraphs() {
  const hub = loadJson(path.join(HUB_DATA, 'hub-debates-graph.json'));
  const pla = loadJson(path.join(WORKSPACE_KB, 'pla-knowledge-graph.json'));

  // Deduplicate nodes by id
  const nodeMap = new Map();
  for (const n of pla.nodes || []) nodeMap.set(n.id, n);
  for (const n of hub.nodes || []) nodeMap.set(n.id, n);

  // Deduplicate edges by source+target+label
  const edgeSet = new Set();
  const edges = [];
  for (const e of [...(pla.edges || []), ...(hub.edges || [])]) {
    const key = `${e.source}→${e.target}→${e.label}`;
    if (!edgeSet.has(key)) {
      edgeSet.add(key);
      edges.push(e);
    }
  }

  return { nodes: [...nodeMap.values()], edges };
}

const merged = mergeGraphs();
const outPath = path.join(HUB_DATA, 'merged-knowledge-graph.json');
fs.writeFileSync(outPath, JSON.stringify(merged, null, 2), 'utf8');
console.log(`Merged: ${merged.nodes.length} nodes, ${merged.edges.length} edges`);
console.log(`Output: ${outPath}`);
