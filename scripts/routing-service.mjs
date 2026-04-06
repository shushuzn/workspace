#!/usr/bin/env node
/**
 * Semantic Task Router HTTP service.
 * GET /rank?task=<natural language task>
 * Returns ranked project list with similarity scores.
 */
import http from 'http';
import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const MANIFEST = join(__dirname, '..', '80-PROJECTS', '.capability-manifest.json');

// Lazy-load embed + cosine
let embedFn, cosineFn, manifest;

async function loadDeps() {
  if (embedFn) return;
  const { embed, cosineSimilarity } = await import('./embed.mjs');
  embedFn = embed;
  cosineFn = cosineSimilarity;
  if (existsSync(MANIFEST)) {
    manifest = JSON.parse(readFileSync(MANIFEST, 'utf-8'));
  } else {
    manifest = [];
  }
}

const server = http.createServer(async (req, res) => {
  await loadDeps();
  const url = new URL(req.url, 'http://localhost');
  if (url.pathname === '/rank' && url.searchParams.has('task')) {
    const task = url.searchParams.get('task');
    try {
      const taskEmb = await embedFn(task);
      const scored = manifest.map((p) => {
        // Combine description + keywords as project text
        const text = `${p.name} ${p.description} ${(p.keywords || []).join(' ')}`;
        // For now use simple keyword overlap as proxy (embed is optional/lazy)
        const keywords = (p.keywords || []).map(k => k.toLowerCase());
        const taskLower = task.toLowerCase();
        const overlap = keywords.filter(k => taskLower.includes(k)).length;
        return { ...p, score: overlap, reason: overlap > 0 ? `matched: ${keywords.filter(k => taskLower.includes(k)).join(', ')}` : 'no keyword match' };
      }).filter(p => p.score > 0)
        .sort((a, b) => b.score - a.score)
        .slice(0, 5);
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ task, results: scored }, null, 2));
    } catch (err) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: err.message }));
    }
  } else if (url.pathname === '/manifest') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(manifest, null, 2));
  } else {
    res.writeHead(404);
    res.end();
  }
});

const PORT = process.env.ROUTING_PORT ?? 9876;
server.listen(PORT, () => {
  process.stderr.write(`[routing] Semantic Task Router listening on port ${PORT}\n`);
});
