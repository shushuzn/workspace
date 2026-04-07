/**
 * Knowledge Query API Server
 * FastAPI-style HTTP server for cross-project knowledge search.
 *
 * Endpoints:
 *   GET /search?query=X        — keyword search across knowledge graph
 *   GET /projects               — list all indexed projects
 *   GET /graph                  — full knowledge graph
 *   GET /health                 — server health
 *
 * Usage:
 *   node src/api-server.js [--port 7892]
 */

import http from 'http';
import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { parseArgs } from 'util';

const __dirname = dirname(fileURLToPath(import.meta.url));
const DATA_FILE = join(__dirname, '..', 'data', 'merged-knowledge-graph.json');
const PORT = parseArgs({ args: process.argv.slice(2), options: { port: { type: 'string', default: '7892' } } }).values.port || 7892;

// ─── Load Knowledge Graph ───────────────────────────────────

function loadGraph() {
  try {
    if (!existsSync(DATA_FILE)) return { nodes: [], edges: [] };
    return JSON.parse(readFileSync(DATA_FILE, 'utf8'));
  } catch { return { nodes: [], edges: [] }; }
}

// ─── Search Logic ─────────────────────────────────────────

function keywordMatch(text, query) {
  if (!text || !query) return false;
  const q = query.toLowerCase();
  return text.toLowerCase().includes(q);
}

function searchGraph(query, limit = 20) {
  const graph = loadGraph();
  const q = query.trim().toLowerCase();
  if (!q) return [];

  const scored = [];

  for (const node of graph.nodes || []) {
    let score = 0;
    const nameMatch = keywordMatch(node.name, q) ? 3 : 0;
    const descMatch = keywordMatch(node.description, q) ? 2 : 0;
    const tagMatch = (node.tags || []).some(t => keywordMatch(t, q)) ? 1 : 0;
    const domainMatch = keywordMatch(node.domain, q) ? 1 : 0;
    score = nameMatch + descMatch + tagMatch + domainMatch;

    if (score > 0) {
      // Find connected nodes
      const connectedIds = (graph.edges || [])
        .filter(e => e.source === node.id || e.target === node.id)
        .flatMap(e => [e.source, e.target])
        .filter(id => id !== node.id);
      const connected = (graph.nodes || [])
        .filter(n => connectedIds.includes(n.id))
        .slice(0, 5)
        .map(n => n.name);

      scored.push({
        id: node.id,
        name: node.name,
        domain: node.domain,
        description: node.description,
        score,
        matchedOn: [
          ...(nameMatch ? ['name'] : []),
          ...(descMatch ? ['description'] : []),
          ...(tagMatch ? ['tags'] : []),
          ...(domainMatch ? ['domain'] : []),
        ],
        connections: connected,
      });
    }
  }

  return scored
    .sort((a, b) => b.score - a.score)
    .slice(0, limit)
    .map(({ score: _score, matchedOn, ...rest }) => ({ ...rest, matchedOn }));
}

// ─── HTTP Server ───────────────────────────────────────────

function sendJSON(res, status, data) {
  res.writeHead(status, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' });
  res.end(JSON.stringify(data, null, 2));
}

function sendText(res, status, text) {
  res.writeHead(status, { 'Content-Type': 'text/plain', 'Access-Control-Allow-Origin': '*' });
  res.end(text);
}

async function handleRequest(req, res) {
  const url = new URL(req.url, `http://localhost:${PORT}`);
  const path = url.pathname;
  const query = url.searchParams.get('query') || '';
  const limit = parseInt(url.searchParams.get('limit') || '20');

  if (path === '/search' && req.method === 'GET') {
    if (!query) return sendJSON(res, 400, { error: 'query parameter required' });
    const results = searchGraph(query, limit);
    return sendJSON(res, 200, {
      query,
      count: results.length,
      results,
    });
  }

  if (path === '/projects' && req.method === 'GET') {
    const graph = loadGraph();
    const domains = [...new Set((graph.nodes || []).map(n => n.domain).filter(Boolean))];
    return sendJSON(res, 200, {
      nodeCount: (graph.nodes || []).length,
      edgeCount: (graph.edges || []).length,
      domains,
    });
  }

  if (path === '/graph' && req.method === 'GET') {
    const graph = loadGraph();
    return sendJSON(res, 200, graph);
  }


  if (path === '/hub/search' && req.method === 'GET') {
    const hubQuery = url.searchParams.get('query') || '';
    if (!hubQuery) return sendJSON(res, 400, { error: 'query required' });
    const graph = loadGraph();
    const hubNodes = (graph.nodes || []).filter(n => n.domain === 'multi-agent-debate');
    const scored = hubNodes.map(n => {
      const q = hubQuery.toLowerCase();
      const nameScore = n.name.toLowerCase().includes(q) ? 3 : 0;
      const descScore = (n.description || '').toLowerCase().includes(q) ? 2 : 0;
      return { ...n, relevanceScore: nameScore + descScore };
    }).filter(n => n.relevanceScore > 0)
      .sort((a, b) => b.relevanceScore - a.relevanceScore);
    return sendJSON(res, 200, { query: hubQuery, count: scored.length, debates: scored });
  }
  if (path === '/health' && req.method === 'GET') {
    return sendJSON(res, 200, {
      status: 'ok',
      port: PORT,
      uptime: process.uptime(),
      dataFile: DATA_FILE,
    });
  }

  if (path === '/') {
    return sendText(res, 200, [
      'Knowledge Bridge API — v1.0',
      'GET  /search?query=X&limit=N  — search knowledge graph',
      'GET  /projects              — list indexed projects/domains',
      'GET  /graph                 — full knowledge graph',
      'GET  /health                — server health',
      'GET  /hub/search?query=X  — search multi-agent debate graph',
    ].join('\n'));
  }

  sendJSON(res, 404, { error: 'Not found' });
}

const server = http.createServer(handleRequest);
server.listen(PORT, () => {
  console.log(`🔍 Knowledge Bridge API running on http://localhost:${PORT}`);
  console.log(`   GET  /search?query=X  — search knowledge graph`);
  console.log(`   GET  /projects       — list indexed projects`);
  console.log(`   GET  /graph          — full knowledge graph`);
  console.log(`   GET  /health          — server health`);
  console.log('   GET  /hub/search  — search multi-agent debates');
});
