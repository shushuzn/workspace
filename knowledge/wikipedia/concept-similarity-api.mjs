/**
 * concept-similarity-api.mjs — Wikipedia concept similarity B2B API
 *
 * Usage:
 *   node concept-similarity-api.mjs [--port 3001]
 *
 * Endpoints:
 *   GET  /health
 *   GET  /concept/distance?a=<conceptA>&b=<conceptB>
 *   POST /concept/batch  { pairs: [[a,b], [c,d]] }
 *
 * Requires Ollama running for embeddings.
 */

import { createServer } from 'http';
import { readFileSync, existsSync, readdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const ARTICLES_DIR = join(__DIR, 'articles');
const PORT = parseInt(process.env.PORT || '3001');
const OLLAMA = 'http://127.0.0.1:11434';

const EMBED_MODEL = 'nomic-embed-text:latest';

function slugify(title) {
  return title.toLowerCase().replace(/[^\w\s\u4e00-\u9fa5]/g, '').replace(/\s+/g, '-').replace(/-+/g, '-').slice(0, 60);
}

function cosineSim(a, b) {
  let dot = 0, na = 0, nb = 0;
  for (let i = 0; i < a.length; i++) { dot += a[i] * b[i]; na += a[i] * a[i]; nb += b[i] * b[i]; }
  return dot / (Math.sqrt(na) * Math.sqrt(nb) + 1e-9);
}

async function embed(text) {
  const res = await fetch(`${OLLAMA}/api/embeddings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model: EMBED_MODEL, prompt: text }),
    signal: AbortSignal.timeout(30000)
  });
  const data = await res.json();
  return data.embedding || [];
}

function buildConceptIndex() {
  const index = {};
  const scan = (dir) => {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      if (entry.isDirectory()) scan(join(dir, entry.name));
      else if (entry.name.endsWith('.md')) {
        const file = join(dir, entry.name);
        const content = readFileSync(file, 'utf8');
        const fm = content.match(/^---\n([\s\S]*?)\n---\n/)?.[1] || '';
        const title = fm.match(/title:\s*(.+)/)?.[1]?.trim() || entry.name.replace('.md', '');
        const body = content.replace(/---[\s\S]*?---\n/, '').replace(/<[^>]+>/g, '').trim().slice(0, 500);
        const id = slugify(title);
        index[id] = { id, title, text: `${title} ${body}` };
      }
    }
  };
  scan(ARTICLES_DIR);
  return index;
}

const index = buildConceptIndex();

async function computeSimilarity(a, b) {
  const embA = await embed(index[slugify(a)]?.text || a);
  const embB = await embed(index[slugify(b)]?.text || b);
  return cosineSim(embA, embB);
}

const server = createServer(async (req, res) => {
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.setHeader('Access-Control-Allow-Origin', '*');
  try {
    const url = new URL(req.url, `http://localhost:${PORT}`);
    if (url.pathname === '/health') {
      res.end(JSON.stringify({ status: 'ok', concepts: Object.keys(index).length }));
    } else if (url.pathname === '/concept/distance') {
      const a = url.searchParams.get('a') || '';
      const b = url.searchParams.get('b') || '';
      if (!a || !b) { res.writeHead(400); res.end(JSON.stringify({ error: 'a and b required' })); return; }
      const sim = await computeSimilarity(a, b);
      res.end(JSON.stringify({ concept_a: a, concept_b: b, similarity: parseFloat(sim.toFixed(4)), api: 'wikipedia-concept-similarity' }));
    } else if (url.pathname === '/concept/batch' && req.method === 'POST') {
      let body = '';
      req.on('data', c => body += c);
      req.on('end', async () => {
        const { pairs } = JSON.parse(body || '{}');
        if (!Array.isArray(pairs)) { res.writeHead(400); res.end(JSON.stringify({ error: 'pairs array required' })); return; }
        const results = await Promise.all(pairs.map(async ([a, b]) => ({ a, b, similarity: parseFloat((await computeSimilarity(a, b)).toFixed(4)) })));
        res.end(JSON.stringify({ results, api: 'wikipedia-concept-similarity' }));
      });
    } else {
      res.writeHead(404);
      res.end(JSON.stringify({ error: 'Not found. Try /concept/distance?a=X&b=Y or /concept/batch' }));
    }
  } catch (e) {
    res.writeHead(500);
    res.end(JSON.stringify({ error: e.message }));
  }
});

server.listen(PORT, () => {
  console.log(`[concept-api] Concept similarity API running at http://localhost:${PORT}`);
  console.log(`  GET  /health`);
  console.log(`  GET  /concept/distance?a=X&b=Y`);
  console.log(`  POST /concept/batch  { pairs: [[x,y], [z,w]] }`);
});
