#!/usr/bin/env node
/**
 * knowledge-bridge-search.mjs — Search knowledge-bridge from OpenViking MCP
 *
 * Exposes knowledge-bridge search as an OpenViking-compatible MCP tool.
 * Run this alongside openviking-mcp to enable cross-project search.
 *
 * Usage:
 *   node knowledge-bridge-search.mjs [--port 3848]
 *
 * Then configure openviking-mcp to proxy `kb_search` to this server,
 * or call directly via HTTP POST to /mcp.
 *
 * Tools provided:
 *   - kb_search: { query: string, limit?: number, domain?: string }
 *     Returns matching knowledge graph nodes with descriptions.
 */

import http from 'http';
import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PORT = parseInt(process.argv[2] || '3848', 10);
const GRAPH_PATH = join(__dirname, '..', '80-PROJECTS', 'knowledge-bridge', 'data', 'pla-knowledge-graph.json');

function loadGraph() {
  if (!existsSync(GRAPH_PATH)) return { nodes: {}, edges: [] };
  try {
    const raw = JSON.parse(readFileSync(GRAPH_PATH, 'utf8'));
    let nodes = raw.nodes;
    if (Array.isArray(nodes)) {
      const conv = {};
      for (const item of nodes) {
        if (Array.isArray(item) && item[1]) conv[item[0]] = item[1];
        else if (item?.id) conv[item.id] = item;
      }
      nodes = conv;
    }
    return { nodes, edges: raw.edges || [] };
  } catch { return { nodes: {}, edges: [] }; }
}

function searchGraph(query, limit = 10, domain = null) {
  const graph = loadGraph();
  const q = query.toLowerCase();
  const allNodes = Object.values(graph.nodes);

  const scored = allNodes.map(node => {
    let score = 0;
    if ((node.label || '').toLowerCase().includes(q)) score += 3;
    if ((node.description || '').toLowerCase().includes(q)) score += 2;
    if (domain && (node.domain || '').toLowerCase().includes(domain.toLowerCase())) score += 1;
    return { node, score };
  }).filter(s => s.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, limit);

  return scored.map(s => ({
    id: s.node.id,
    label: s.node.label,
    domain: s.node.domain,
    description: s.node.description?.slice(0, 200),
    score: s.score
  }));
}

// ─── MCP JSON-RPC ─────────────────────────────────────────────────────────────

function jsonrpc(id, result) {
  return JSON.stringify({ jsonrpc: '2.0', id, result });
}
function jsonrpcError(id, code, message) {
  return JSON.stringify({ jsonrpc: '2.0', id, error: { code, message } });
}

const TOOLS = {
  kb_search: {
    description: 'Search knowledge-bridge graph for nodes matching a query. Returns nodes with labels, domains, and descriptions.',
    args: [
      { name: 'query', type: 'string', description: 'Search query (required)' },
      { name: 'limit', type: 'number', description: 'Max results (default 10)' },
      { name: 'domain', type: 'string', description: 'Filter by domain (e.g. chemistry, programming)' }
    ]
  }
};

function handleRequest(body) {
  const req = JSON.parse(body);
  if (req.method === 'tools/list') {
    const list = Object.entries(TOOLS).map(([name, t]) => ({
      name,
      description: t.description,
      inputSchema: {
        type: 'object',
        properties: Object.fromEntries(t.args.map(a => [a.name, { type: a.type, description: a.description }])),
        required: t.args.filter(a => a.name === 'query').map(a => a.name)
      }
    }));
    return jsonrpc(req.id, { tools: list });
  }
  if (req.method === 'tools/call') {
    const { name, arguments: args = {} } = req.params || {};
    if (name === 'kb_search') {
      const results = searchGraph(args.query, args.limit, args.domain);
      return jsonrpc(req.id, {
        content: [{ type: 'text', text: JSON.stringify({ success: true, query: args.query, results }, null, 2) }]
      });
    }
    return jsonrpcError(req.id, -32601, `Unknown tool: ${name}`);
  }
  if (req.method === 'initialize') {
    return jsonrpc(req.id, {
      protocolVersion: '2024-11-05',
      capabilities: { tools: {} },
      serverInfo: { name: 'knowledge-bridge-search', version: '1.0.0' }
    });
  }
  return jsonrpcError(req.id, -32601, 'Method not found');
}

// ─── HTTP Server ───────────────────────────────────────────────────────────────

const server = http.createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Content-Type', 'application/json');

  if (req.method === 'OPTIONS') { res.end(); return; }

  if (req.method === 'GET' && req.url === '/health') {
    return res.end(JSON.stringify({ status: 'ok', graph: existsSync(GRAPH_PATH) }));
  }

  if (req.method === 'POST' && req.url === '/mcp') {
    let body = '';
    req.on('data', c => body += c);
    req.on('end', () => {
      try { res.end(handleRequest(body)); }
      catch (e) { res.end(jsonrpcError(null, -32700, e.message)); }
    });
    return;
  }

  res.statusCode = 404;
  res.end(JSON.stringify({ error: 'Not found' }));
});

server.listen(PORT, () => {
  console.log(`🔍 Knowledge Bridge Search MCP: http://localhost:${PORT}/mcp`);
  console.log(`   Tool: kb_search(query, limit?, domain?)`);
  console.log(`   Graph: ${GRAPH_PATH}`);
});
