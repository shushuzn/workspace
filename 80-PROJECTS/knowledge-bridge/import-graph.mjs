/**
 * import-graph.mjs — Import entities/relations into knowledge graph
 *
 * Usage:
 *   node import-graph.mjs --file entities.csv --format csv
 *   node import-graph.mjs --file graph.json --format json
 *   node import-graph.mjs --file relations.csv --format csv --mode relations-only
 *   node import-graph.mjs --help
 *
 * CSV format (entities):
 *   id,label,domain,description
 *   uuid-1,PLA,chemistry,聚乳酸
 *
 * CSV format (relations):
 *   source,target,type,strength
 *   uuid-1,uuid-2,related,1
 *
 * JSON format:
 *   { nodes: [[id,{...}],...], edges:[{source,target,type,strength},...] }
 *   or plain: { nodes: [{id,label,domain,description},...], edges:[...] }
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
const format = getArg('format') || (file && file.endsWith('.csv') ? 'csv' : 'json');
const mode = getArg('mode') || 'full';
const output = getArg('output') || join(DATA_DIR, 'pla-knowledge-graph.json');
const graphFile = getArg('graph') || join(DATA_DIR, 'pla-knowledge-graph.json');

if (!file || args.includes('--help')) {
  console.log(`import-graph.mjs — Import entities/relations into knowledge graph

Usage:
  node import-graph.mjs --file <path> --format csv|json [--mode full|entities-only|relations-only] [--output <graph.json>] [--graph <target-graph.json>]

Examples:
  node import-graph.mjs --file entities.csv --format csv
  node import-graph.mjs --file relations.csv --format csv --mode relations-only
  node import-graph.mjs --file data.json --format json
  node import-graph.mjs --file nodes.csv --format csv --graph my-graph.json

CSV format (entities.csv):
  id,label,domain,description
  uuid-1,PLA,chemistry,聚乳酸

CSV format (relations.csv):
  source,target,type,strength
  uuid-1,uuid-2,related,1

JSON format:
  { nodes: [[id,{...}],...], edges:[{source,target,type,strength},...] }
  or: { nodes:[{id,label,domain,description},...], edges:[...] }`);
  process.exit(0);
}

function loadGraph() {
  try {
    const raw = readFileSync(graphFile, 'utf8');
    return JSON.parse(raw);
  } catch {
    return { nodes: [], edges: [] };
  }
}

function saveGraph(graph) {
  writeFileSync(output, JSON.stringify(graph, null, 2));
  console.log(`Saved ${graph.nodes.length} nodes and ${graph.edges.length} edges to ${output}`);
}

// Normalize Map-format or plain-format nodes to Map format
function normalizeNodes(nodes) {
  if (!nodes || nodes.length === 0) return [];
  if (Array.isArray(nodes[0]) && nodes[0].length === 2 && typeof nodes[0][0] === 'string') {
    return nodes;
  }
  return nodes.map(n => [n.id, { ...n, connections: n.connections || [] }]);
}

// Simple CSV parser — handles quoted fields
function parseCSVLine(line) {
  const fields = [];
  let inQuotes = false;
  let field = '';
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (ch === '"') {
      if (inQuotes && line[i + 1] === '"') { field += '"'; i++; }
      else inQuotes = !inQuotes;
    } else if (ch === ',' && !inQuotes) {
      fields.push(field.trim());
      field = '';
    } else {
      field += ch;
    }
  }
  fields.push(field.trim());
  return fields;
}

function parseCSV(filepath) {
  const lines = readFileSync(filepath, 'utf8').split('\n').filter(l => l.trim());
  const headers = parseCSVLine(lines[0]);
  return lines.slice(1).map(line => {
    const values = parseCSVLine(line);
    const row = {};
    headers.forEach((h, i) => { row[h] = values[i] || ''; });
    return row;
  });
}

function importCSVEntities(filepath) {
  const records = parseCSV(filepath);
  return records.map(r => [
    r.id || r.label,
    {
      id: r.id || r.label,
      label: r.label,
      domain: r.domain || '',
      description: r.description || '',
      connections: [],
      createdAt: new Date().toISOString()
    }
  ]);
}

function importCSVRelations(filepath, existingNodes) {
  const records = parseCSV(filepath);
  const nodeSet = new Set(existingNodes.map(([id]) => id));
  const edges = [];
  for (const r of records) {
    if (nodeSet.has(r.source) && nodeSet.has(r.target)) {
      edges.push({
        id: `edge-${r.source}-${r.target}`,
        from: r.source,
        to: r.target,
        type: r.type || 'related',
        strength: parseFloat(r.strength || 1)
      });
    }
  }
  return edges;
}

function importJSON(filepath) {
  const raw = readFileSync(filepath, 'utf8');
  return JSON.parse(raw);
}

// Main logic
const graph = loadGraph();
const existingNodes = normalizeNodes(graph.nodes || []);
const existingEdges = graph.edges || [];

if (format === 'csv') {
  if (mode === 'full' || mode === 'entities-only') {
    const newNodes = importCSVEntities(file);
    const nodeMap = new Map(existingNodes);
    for (const [id, node] of newNodes) {
      if (!nodeMap.has(id)) nodeMap.set(id, node);
    }
    graph.nodes = [...nodeMap.entries()];
    console.log(`Imported ${newNodes.length} entities`);
  }
  if (mode === 'full' || mode === 'relations-only') {
    const newEdges = importCSVRelations(file, graph.nodes);
    const seen = new Set(existingEdges.map(e => `${e.from}-${e.to}`));
    const filtered = newEdges.filter(e => !seen.has(`${e.from}-${e.to}`));
    graph.edges = [...existingEdges, ...filtered];
    console.log(`Imported ${filtered.length} new relations`);
  }
} else if (format === 'json') {
  const data = importJSON(file);
  const newNodes = normalizeNodes(data.nodes || []);
  const nodeMap = new Map(existingNodes);
  for (const [id, node] of newNodes) {
    if (!nodeMap.has(id)) nodeMap.set(id, node);
  }
  graph.nodes = [...nodeMap.entries()];

  const newEdges = (data.edges || []).map(e => ({
    id: e.id || `edge-${e.from}-${e.to}`,
    from: e.from || e.source,
    to: e.to || e.target,
    type: e.type || e.relation || 'related',
    strength: parseFloat(e.strength || 1)
  }));
  const seen = new Set(existingEdges.map(e => `${e.from}-${e.to}`));
  const filtered = newEdges.filter(e => !seen.has(`${e.from}-${e.to}`));
  graph.edges = [...existingEdges, ...filtered];
  console.log(`Merged JSON: added ${newNodes.length} nodes, ${filtered.length} new edges`);
}

saveGraph(graph);
