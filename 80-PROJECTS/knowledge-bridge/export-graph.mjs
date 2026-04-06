/**
 * export-graph.mjs — Export knowledge graph to DOT (Graphviz) or GraphML format
 *
 * Usage:
 *   node export-graph.mjs --file output.dot --format dot
 *   node export-graph.mjs --file output.graphml --format graphml
 *   node export-graph.mjs --file output.dot --format dot --graph data/pla-knowledge-graph.json
 *   node export-graph.mjs --file output.dot --format dot --domain chemistry
 *   node export-graph.mjs --help
 */

import { readFileSync, writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const DATA_DIR = join(__dirname, 'data');

const args = process.argv.slice(2);

function getArg(name) {
  const i = args.indexOf(`--${name}`);
  return i >= 0 ? args[i + 1] : null;
}

const file = getArg('file');
const format = (getArg('format') || (file?.endsWith('.graphml') ? 'graphml' : 'dot')).toLowerCase();
const graphFile = getArg('graph') || join(DATA_DIR, 'pla-knowledge-graph.json');
const domain = getArg('domain');

if (args.includes('--help') || !file) {
  console.log(`export-graph.mjs — Export knowledge graph to DOT (Graphviz) or GraphML

Usage:
  node export-graph.mjs --file <output> --format dot|graphml [--graph <graph.json>] [--domain <domain>]

Examples:
  node export-graph.mjs --file out.dot --format dot
  node export-graph.mjs --file out.graphml --format graphml
  node export-graph.mjs --file out.dot --format dot --domain chemistry
  node export-graph.mjs --file out.dot --format dot --graph my-graph.json

Output formats:
  dot    — Graphviz DOT format, viewable in Gephi (via GraphML), xdot, etc.
  graphml — Gephi native format with node colors by domain`);
  process.exit(0);
}

// Domain → DOT color mapping
const DOMAIN_COLORS = {
  programming: '#4285F4',
  chemistry: '#34A853',
  biology: '#EA4335',
  physics: '#9C27B0',
  cooking: '#FF9800',
  medicine: '#00BCD4',
  business: '#795548',
  daily: '#607D8B'
};

function loadGraph() {
  const raw = readFileSync(graphFile, 'utf8');
  const data = JSON.parse(raw);
  // Support both Map-format [[id, obj]] and plain [{id, ...}]
  if (Array.isArray(data.nodes[0]) && data.nodes[0].length === 2 && typeof data.nodes[0][0] === 'string') {
    return data;
  }
  // Convert plain array to Map format
  return {
    nodes: data.nodes.map(n => [n.id, n]),
    edges: data.edges || []
  };
}

function exportDOT(graph, domainFilter) {
  const nodeMap = new Map(graph.nodes);
  const nodes = domainFilter
    ? graph.nodes.filter(([, n]) => n.domain === domainFilter)
    : graph.nodes;

  const nodeIds = new Set(nodes.map(([id]) => id));
  const edges = graph.edges.filter(e => nodeIds.has(e.from) && nodeIds.has(e.to));

  const lines = ['digraph KnowledgeGraph {'];
  lines.push('  rankdir=LR;');
  lines.push('  node [shape=ellipse, style=filled, fontname="Arial"];');
  lines.push('  edge [fontname="Arial", fontsize=10];');

  for (const [id, node] of nodes) {
    const color = DOMAIN_COLORS[node.domain] || '#9E9E9E';
    const label = node.label.replace(/"/g, '\\"');
    const title = (node.description || '').replace(/"/g, '\\"').slice(0, 60);
    lines.push(`  "${id}" [label="${label}", fillcolor="${color}", tooltip="${title}"];`);
  }

  for (const edge of edges) {
    const weight = edge.strength || 1;
    const etype = edge.type || 'related';
    lines.push(`  "${edge.from}" -> "${edge.to}" [label="${etype}", penwidth=${weight}];`);
  }

  lines.push('}');
  return lines.join('\n');
}

function exportGraphML(graph, domainFilter) {
  const nodeMap = new Map(graph.nodes);
  const nodes = domainFilter
    ? graph.nodes.filter(([, n]) => n.domain === domainFilter)
    : graph.nodes;

  const nodeIds = [...nodes.map(([id]) => id)];

  const lines = ['<?xml version="1.0" encoding="UTF-8"?>'];
  lines.push('<graphml xmlns="http://graphml.graphdrawing.org/xmlns">');

  // Node attributes
  lines.push('  <key id="label" for="node" attr.name="label" attr.type="string"/>');
  lines.push('  <key id="domain" for="node" attr.name="domain" attr.type="string"/>');
  lines.push('  <key id="description" for="node" attr.name="description" attr.type="string"/>');
  lines.push('  <key id="color" for="node" attr.name="color" attr.type="string"/>');
  lines.push('  <key id="etype" for="edge" attr.name="type" attr.type="string"/>');
  lines.push('  <key id="strength" for="edge" attr.name="strength" attr.type="double"/>');

  lines.push(`  <graph id="KG" edgedefault="directed">`);

  for (const [id, node] of nodes) {
    const color = DOMAIN_COLORS[node.domain] || '#9E9E9E';
    const label = node.label.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    const desc = (node.description || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    lines.push(`    <node id="${id}">`);
    lines.push(`      <data key="label">${label}</data>`);
    lines.push(`      <data key="domain">${node.domain || ''}</data>`);
    lines.push(`      <data key="description">${desc.slice(0, 200)}</data>`);
    lines.push(`      <data key="color">${color}</data>`);
    lines.push('    </node>');
  }

  const edgeSet = new Set();
  for (const edge of graph.edges) {
    if (!nodeIds.includes(edge.from) || !nodeIds.includes(edge.to)) continue;
    const key = `${edge.from}-${edge.to}`;
    if (edgeSet.has(key)) continue;
    edgeSet.add(key);
    const etype = edge.type || 'related';
    const strength = edge.strength || 1;
    lines.push(`    <edge source="${edge.from}" target="${edge.to}">`);
    lines.push(`      <data key="etype">${etype}</data>`);
    lines.push(`      <data key="strength">${strength}</data>`);
    lines.push('    </edge>');
  }

  lines.push('  </graph>');
  lines.push('</graphml>');
  return lines.join('\n');
}

const graph = loadGraph();

if (domain) {
  console.log(`Exporting nodes in domain: ${domain}`);
}

const content = format === 'graphml'
  ? exportGraphML(graph, domain)
  : exportDOT(graph, domain);

writeFileSync(file, content);
console.log(`Exported to ${file} (${format.toUpperCase()}) — ${graph.nodes.length} nodes, ${graph.edges.length} edges${domain ? ` [domain: ${domain}]` : ''}`);
