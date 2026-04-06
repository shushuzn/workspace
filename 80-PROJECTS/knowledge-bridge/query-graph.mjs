/**
 * query-graph.mjs — Query knowledge graph by domain, relation, or similarity
 *
 * Usage:
 *   node query-graph.mjs                                      # list all nodes
 *   node query-graph.mjs --domain programming                # filter by domain
 *   node query-graph.mjs --relation contains                 # filter by edge relation
 *   node query-graph.mjs --similar-to "neural network"      # fuzzy match node labels
 *   node query-graph.mjs --json                              # output as JSON
 *   node query-graph.mjs --graph data/my-graph.json         # custom graph file
 */

import { readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));

const args = process.argv.slice(2);
const graphIdx = args.indexOf('--graph');
const jsonPath = graphIdx >= 0 ? args[graphIdx + 1] : join(__dirname, 'data', 'pla-knowledge-graph.json');

let graph;
try {
  graph = JSON.parse(readFileSync(jsonPath, 'utf8'));
} catch (e) {
  console.error('Failed to load graph:', e.message);
  process.exit(1);
}

const domainIdx = args.indexOf('--domain');
const relIdx = args.indexOf('--relation');
const similarIdx = args.indexOf('--similar-to');
const jsonOut = args.includes('--json');

const domain = domainIdx >= 0 ? args[domainIdx + 1].toLowerCase() : null;
const relation = relIdx >= 0 ? args[relIdx + 1].toLowerCase() : null;
const similar = similarIdx >= 0 ? args[similarIdx + 1].toLowerCase() : null;

const nodes = graph.nodes ? Object.values(graph.nodes) : [];
const edges = graph.edges || [];

// Filter nodes
let filtered = nodes;
if (domain) {
  filtered = filtered.filter(n => (n.domain || '').toLowerCase().includes(domain));
}
if (similar) {
  const sim = similar;
  filtered = filtered.filter(n =>
    (n.label || '').toLowerCase().includes(sim) ||
    (n.description || '').toLowerCase().includes(sim)
  );
}

// Filter edges
let filteredEdges = edges;
if (relation) {
  filteredEdges = filteredEdges.filter(e =>
    (e.relation || '').toLowerCase().includes(relation)
  );
}

// Build result
const nodeIds = new Set(filtered.map(n => n.id));
const relevantEdges = filteredEdges.filter(e => {
  const src = typeof e.source === 'string' ? e.source : e.source.id || e.source.label;
  const tgt = typeof e.target === 'string' ? e.target : e.target.id || e.target.label;
  return nodeIds.has(src) || nodeIds.has(tgt);
});

if (jsonOut) {
  console.log(JSON.stringify({ nodes: filtered, edges: relevantEdges }, null, 2));
} else {
  console.log(`\n  Graph: ${graph.name || jsonPath}`);
  console.log(`  Matched nodes: ${filtered.length}  |  Edges: ${relevantEdges.length}\n`);
  for (const n of filtered.slice(0, 50)) {
    const conn = relevantEdges.filter(e => {
      const src = typeof e.source === 'string' ? e.source : e.source.id || e.source.label;
      const tgt = typeof e.target === 'string' ? e.target : e.target.id || e.target.label;
      return src === n.id || tgt === n.id;
    }).length;
    console.log(`  • ${n.label} ${n.domain ? `[${n.domain}]` : ''} (${conn} edges)`);
    if (n.description) console.log(`    ${n.description.slice(0, 80)}`);
  }
  if (filtered.length > 50) console.log(`\n  ... and ${filtered.length - 50} more nodes`);
  console.log('');
}
