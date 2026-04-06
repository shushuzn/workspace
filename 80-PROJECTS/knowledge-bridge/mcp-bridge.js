/**
 * knowledge-bridge/mcp-bridge.js — MCP Tool Bridge
 *
 * Exposes knowledge graph as MCP tools:
 *   list_nodes   — list all nodes (optional: --domain, --json)
 *   search_nodes — fuzzy search nodes (required: --query)
 *   get_analogies — get analogy chains
 *
 * Usage:
 *   node mcp-bridge.js [port]  (default: 3849)
 *
 * MCP protocol: JSON-RPC 2.0 over HTTP POST
 * POST http://localhost:3849/mcp
 * Body: { "jsonrpc": "2.0", "method": "tools/call", "params": { "name": "list_nodes", "arguments": {} }, "id": 1 }
 * Response: { "jsonrpc": "2.0", "result": { "content": [{ "type": "text", "text": "..." }] }, "id": 1 }
 */

import http from 'http';
import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PORT = parseInt(process.argv[2] || '3849', 10);
const GRAPH_PATH = join(__dirname, 'data', 'pla-knowledge-graph.json');

function loadGraph() {
  if (!existsSync(GRAPH_PATH)) return null;
  return JSON.parse(readFileSync(GRAPH_PATH, 'utf8'));
}

// ─── Tool Implementations ─────────────────────────────────────────────────────

function list_nodes(args = {}) {
  const graph = loadGraph();
  if (!graph) return { content: [{ type: 'text', text: 'Graph file not found at ' + GRAPH_PATH }] };
  const { domain, format = 'text' } = args;
  let nodes = graph.nodes ? Object.values(graph.nodes) : [];
  if (domain) nodes = nodes.filter(n => (n.domain || '').toLowerCase().includes(domain.toLowerCase()));
  if (format === 'json') return { content: [{ type: 'text', text: JSON.stringify(nodes, null, 2) }] };
  const lines = nodes.map(n => `• ${n.label || n.id} [${n.domain || '?'}]${n.description ? ' — ' + n.description.slice(0, 60) : ''}`);
  return { content: [{ type: 'text', text: lines.join('\n') || '(no nodes)' }] };
}

function search_nodes(args = {}) {
  const graph = loadGraph();
  if (!graph) return { content: [{ type: 'text', text: 'Graph file not found' }] };
  const { query } = args;
  if (!query) return { content: [{ type: 'text', text: 'query argument required' }] };
  const q = query.toLowerCase();
  const nodes = graph.nodes ? Object.values(graph.nodes) : [];
  const matched = nodes.filter(n =>
    (n.label || '').toLowerCase().includes(q) ||
    (n.description || '').toLowerCase().includes(q) ||
    (n.domain || '').toLowerCase().includes(q)
  );
  const edges = graph.edges || [];
  const lines = matched.slice(0, 20).map(n => {
    const conn = edges.filter(e => {
      const src = typeof e.source === 'string' ? e.source : e.source.id;
      const tgt = typeof e.target === 'string' ? e.target : e.target.id;
      return src === n.id || tgt === n.id;
    }).length;
    return `• ${n.label || n.id} [${n.domain || '?'}] — ${n.description || ''}`.slice(0, 120);
  });
  return { content: [{ type: 'text', text: lines.join('\n') || `No results for "${query}"` }] };
}

function get_analogies(args = {}) {
  const graph = loadGraph();
  if (!graph) return { content: [{ type: 'text', text: 'Graph file not found' }] };
  const analogies = graph.analogyBank || [];
  const nodes = graph.nodes ? Object.values(graph.nodes) : [];
  const result = analogies.slice(0, 20).map(a => {
    const src = nodes.find(n => n.id === a.source || n.label === a.source);
    const tgt = nodes.find(n => n.id === a.target || n.label === a.target);
    return `⟳ ${src?.label || a.source} ≈ ${tgt?.label || a.target}\n  ${(a.text || a.description || '').slice(0, 80)}`;
  });
  return { content: [{ type: 'text', text: result.join('\n\n') || '(no analogies)' }] };
}

const TOOLS = {
  list_nodes: { description: 'List all knowledge graph nodes, optionally filtered by domain.', args: [{ name: 'domain', type: 'string', description: 'Filter by domain (e.g. programming, chemistry)' }, { name: 'format', type: 'string', description: 'Output format: text (default) or json' }] },
  search_nodes: { description: 'Fuzzy search knowledge graph nodes by label, description, or domain.', args: [{ name: 'query', type: 'string', description: 'Search query (required)' }] },
  get_analogies: { description: 'Get all analogy chains from the knowledge graph.', args: [] },
};

// ─── MCP JSON-RPC ─────────────────────────────────────────────────────────────

function jsonrpc(id, result) {
  return JSON.stringify({ jsonrpc: '2.0', id, result });
}

function jsonrpcError(id, code, message) {
  return JSON.stringify({ jsonrpc: '2.0', id, error: { code, message } });
}

function handleRequest(body) {
  const req = JSON.parse(body);
  if (req.method === 'tools/list') {
    const list = Object.entries(TOOLS).map(([name, t]) => ({ name, description: t.description, inputSchema: { type: 'object', properties: Object.fromEntries(t.args.map(a => [a.name, { type: a.type, description: a.description })), required: [] } }));
    return jsonrpc(req.id, { tools: list });
  }
  if (req.method === 'tools/call') {
    const { name, arguments: args = {} } = req.params || {};
    if (name === 'list_nodes') return jsonrpc(req.id, list_nodes(args));
    if (name === 'search_nodes') return jsonrpc(req.id, search_nodes(args));
    if (name === 'get_analogies') return jsonrpc(req.id, get_analogies(args));
    return jsonrpcError(req.id, -32601, `Unknown tool: ${name}`);
  }
  if (req.method === 'initialize') {
    return jsonrpc(req.id, { protocolVersion: '2024-11-05', capabilities: { tools: {} }, serverInfo: { name: 'knowledge-bridge', version: '1.0.0' } });
  }
  return jsonrpcError(req.id, -32601, 'Method not found');
}

// ─── HTTP Server ─────────────────────────────────────────────────────────────

const server = http.createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Content-Type', 'application/json');

  if (req.method === 'OPTIONS') { res.end(); return; }

  if (req.method === 'GET' && req.url === '/health') {
    const graph = loadGraph();
    res.end(JSON.stringify({ status: 'ok', hasGraph: !!graph, tools: Object.keys(TOOLS).length }));
    return;
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
  console.log(`🔌 knowledge-bridge MCP Bridge: http://localhost:${PORT}/mcp`);
  console.log(`   GET  /health           — health check`);
  console.log(`   POST /mcp             — MCP JSON-RPC endpoint`);
  console.log(`   Tools: ${Object.keys(TOOLS).join(', ')}`);
});
