/**
 * graph-to-ascii.mjs — Render knowledge graph as ASCII tree in terminal
 *
 * Usage:
 *   node graph-to-ascii.mjs                    # default: data/pla-knowledge-graph.json
 *   node graph-to-ascii.mjs graph.json         # custom graph file
 *   node graph-to-ascii.mjs --max-depth 3    # limit tree depth
 *   node graph-to-ascii.mjs --max-children 5 # limit children per node
 */

import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));

const args = process.argv.slice(2);
const maxDepth = parseInt(args.includes('--max-depth') ? args[args.indexOf('--max-depth') + 1] : '99');
const maxChildren = parseInt(args.includes('--max-children') ? args[args.indexOf('--max-children') + 1] : '20');

const jsonPath = args.find(a => !a.startsWith('--')) || join(__dirname, 'data', 'pla-knowledge-graph.json');

let graph;
try {
  graph = JSON.parse(readFileSync(jsonPath, 'utf8'));
} catch (e) {
  console.error('Failed to load graph:', e.message);
  console.error('Usage: node graph-to-ascii.mjs [graph.json] [--max-depth N] [--max-children N]');
  process.exit(1);
}

const nodes = graph.nodes ? Object.values(graph.nodes) : [];
const edges = graph.edges || [];
const rootId = graph.rootId || Object.keys(graph.nodes)[0];
const root = nodes.find(n => n.id === rootId || n.id === graph.name);

function buildTree(nodeId, depth = 0, visited = new Set()) {
  if (depth > maxDepth || visited.has(nodeId)) return null;
  visited.add(nodeId);
  const node = nodes.find(n => n.id === nodeId);
  const children = edges
    .filter(e => e.source === nodeId || e.source.id === nodeId)
    .map(e => typeof e.target === 'string' ? e.target : e.target.id)
    .filter(id => id !== nodeId)
    .slice(0, maxChildren);
  return {
    label: node?.label || nodeId,
    domain: node?.domain || '',
    children: children.map(id => buildTree(id, depth + 1, visited)).filter(Boolean)
  };
}

function printTree(node, prefix = '', isLast = true) {
  const connector = isLast ? '└── ' : '├── ';
  const domain = node.domain ? ` [${node.domain}]` : '';
  console.log(prefix + connector + node.label + domain);
  const newPrefix = prefix + (isLast ? '    ' : '│   ');
  node.children.forEach((child, i) => {
    printTree(child, newPrefix, i === node.children.length - 1);
  });
}

console.log('\n📊 Knowledge Graph: ' + (graph.name || jsonPath));
console.log('─'.repeat(50));
console.log('Nodes: ' + nodes.length + '  |  Edges: ' + edges.length + '\n');

if (root) {
  const tree = buildTree(root.id);
  if (tree) printTree(tree);
} else {
  // No root found — print all nodes in order
  nodes.slice(0, 20).forEach((n, i) => {
    console.log((i === 0 ? '└── ' : '├── ') + n.label + (n.domain ? ` [${n.domain}]` : ''));
  });
}
console.log('');
