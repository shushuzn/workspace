/**
 * scrapeToGraph.mjs — Bridge: scrape URLs → knowledge graph
 *
 * Usage:
 *   node scrapeToGraph.mjs <url>                        # single URL
 *   node scrapeToGraph.mjs --url-list urls.txt          # batch from file (one URL per line)
 *   node scrapeToGraph.mjs --url-list urls.txt --concurrent 5  # max 5 parallel fetches
 *   node scrapeToGraph.mjs --url-list urls.txt --output graph.json
 *   node scrapeToGraph.mjs --url-list urls.txt --format d3   # D3.js-compatible {nodes, links} format
 */

import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));

// ─── CLI Args ───────────────────────────────────────────────────────────────

const args = process.argv.slice(2);

function getArg(flag, fallback) {
  const idx = args.indexOf(flag);
  return idx >= 0 ? args[idx + 1] : fallback;
}
function hasArg(flag) { return args.includes(flag); }

const url = args.find(a => !a.startsWith('--'));
const urlListPath = getArg('--url-list', null);
const outputPath = getArg('--output', urlListPath
  ? join(__dirname, 'data', 'batch-graph.json')
  : join(__dirname, 'data', 'scraped-graph.json'));
const maxConcurrent = parseInt(getArg('--concurrent', '3'));
const useD3Format = hasArg('--format') && getArg('--format', '') === 'd3';
const verbose = hasArg('--verbose');

// ─── Fetch ─────────────────────────────────────────────────────────────────

async function safeFetch(url, timeoutMs = 15000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(url, {
      signal: controller.signal,
      headers: { 'User-Agent': 'Mozilla/5.0 (compatible; KnowledgeBridge/1.0)' },
    });
    clearTimeout(timer);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.text();
  } catch (e) {
    clearTimeout(timer);
    return null;
  }
}

// ─── Extraction ──────────────────────────────────────────────────────────────

function extractEntities(text) {
  // Simple keyword extraction — noun phrases via capital words + common entity patterns
  const entities = [];
  // Capitalized multi-word phrases
  const caps = text.match(/[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+/g) || [];
  entities.push(...caps.map(e => ({ type: 'entity', value: e })));
  // CamelCase words
  const camel = text.match(/[a-z]+[A-Z][a-z]+/g) || [];
  entities.push(...camel.map(e => ({ type: 'entity', value: e })));
  return entities.slice(0, 20);
}

function extractKeywords(text) {
  const stopWords = new Set(['the','a','an','and','or','but','in','on','at','to','for','of','with','by','from','as','is','was','are','were','be','have','has','had','this','that','these','those','which','what','who','when','where','how','not','all','each','every','some','any','no','than','then','more','most','also','very','just','only','own','same','so','too','can','will','would','could','should','may','might','must','shall']);
  return text.toLowerCase()
    .replace(/[^\w\s]/g, ' ')
    .split(/\s+/)
    .filter(w => w.length > 4 && !stopWords.has(w))
    .slice(0, 30);
}

function extractGraphFromHtml(html, url) {
  const titleMatch = html.match(/<title>(.*?)<\/title>/is);
  const title = titleMatch ? titleMatch[1].trim() : new URL(url).hostname;

  const headings = [...html.matchAll(/<h[1-3][^>]*>(.*?)<\/h[1-3]>/gi)]
    .map(m => m[1].replace(/<[^>]+>/g, '').trim())
    .filter(t => t.length > 3)
    .slice(0, 8);

  const links = [...html.matchAll(/<a[^>]+href=["'](https?:\/\/[^"']+)["'][^>]*>(.*?)<\/a>/gi)]
    .map(m => ({ url: m[1], text: m[2].replace(/<[^>]+>/g, '').trim() }))
    .filter(l => l.text.length > 3 && l.url.startsWith('http'))
    .slice(0, 15);

  const descMatch = html.match(/<meta[^>]+name=["']description["'][^>]+content=["']([^"']+)["']/i)
    || html.match(/<meta[^>]+content=["']([^"']+)["'][^>]+name=["']description["']/i);
  const description = descMatch ? descMatch[1].trim() : '';

  // Strip HTML for text analysis
  const plainText = html.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
  const keywords = extractKeywords(plainText);
  const entities = extractEntities(plainText);

  return { title, description, headings, links, keywords, entities, url };
}

// ─── Graph Builder ───────────────────────────────────────────────────────────

function buildGraph(pages) {
  const graph = {
    name: 'Knowledge Graph',
    domain: 'web',
    timestamp: new Date().toISOString(),
    nodes: {},
    edges: [],
    analogyBank: [],
    _meta: { pageCount: pages.length },
  };

  const addNode = (id, label, domain, description, meta = {}) => {
    if (!graph.nodes[id]) {
      graph.nodes[id] = { id, label, domain, description, ...meta };
    }
    return id;
  };

  const rootId = addNode('root', 'Knowledge Graph', 'meta', `Aggregated from ${pages.length} sources`);

  for (const page of pages) {
    if (!page.data) continue;
    const { title, description, headings, links, keywords, entities, url: pageUrl } = page.data;
    const domain = (() => { try { return new URL(pageUrl).hostname; } catch { return 'unknown'; } })();

    const pageId = addNode(
      `page-${page.index}`,
      title.slice(0, 80),
      'web',
      description,
      { url: pageUrl, domain, keywords, entities }
    );
    graph.edges.push({ source: rootId, target: pageId, relation: 'contains', weight: 1.0 });

    // Heading nodes
    for (const h of headings) {
      const hId = addNode(`h-${page.index}-${graph.edges.length}`, h, 'section', `From: ${title}`);
      graph.edges.push({ source: pageId, target: hId, relation: 'contains', weight: 0.8 });
    }

    // Entity nodes
    for (const entity of entities.slice(0, 5)) {
      const eId = addNode(`entity-${page.index}-${graph.edges.length}`, entity.value, 'entity', `Extracted from ${title}`);
      graph.edges.push({ source: pageId, target: eId, relation: 'mentions', weight: 0.6 });
    }

    // Keyword nodes
    for (const kw of keywords.slice(0, 10)) {
      const kwId = addNode(`kw-${kw}`, kw, 'keyword', `Keyword across sources`);
      // Connect keyword to page
      if (!graph.edges.some(e => e.source === pageId && e.target === kwId)) {
        graph.edges.push({ source: pageId, target: kwId, relation: 'has_keyword', weight: 0.4 });
      }
    }
  }

  return graph;
}

function toD3Format(graph) {
  const nodeMap = new Map(Object.values(graph.nodes).map(n => [n.id, n]));
  return {
    nodes: Object.values(graph.nodes).map(n => ({
      id: n.id,
      label: n.label,
      domain: n.domain,
      url: n.url || '',
      keywords: n.keywords || [],
    })),
    links: graph.edges.map(e => ({
      source: e.source,
      target: e.target,
      relation: e.relation,
      weight: e.weight,
    })),
  };
}

// ─── Batch Fetcher ─────────────────────────────────────────────────────────

async function fetchUrlBatch(urls, concurrency = 3) {
  const results = [];
  for (let i = 0; i < urls.length; i += concurrency) {
    const batch = urls.slice(i, i + concurrency);
    const batchResults = await Promise.all(
      batch.map(async (url, offset) => {
        if (verbose) console.log(`[${i + offset + 1}/${urls.length}] Fetching: ${url}`);
        const html = await safeFetch(url);
        if (!html) return { index: i + offset, url, data: null, error: 'fetch_failed' };
        try {
          return { index: i + offset, url, data: extractGraphFromHtml(html, url) };
        } catch (e) {
          return { index: i + offset, url, data: null, error: e.message };
        }
      })
    );
    results.push(...batchResults);
    if (verbose) {
      const ok = batchResults.filter(r => r.data).length;
      console.log(`  → ${ok}/${batchResults.length} succeeded in batch`);
    }
  }
  return results;
}

// ─── Main ───────────────────────────────────────────────────────────────────

async function main() {
  const pages = [];

  if (urlListPath) {
    if (!existsSync(urlListPath)) {
      console.error(`URL list not found: ${urlListPath}`);
      process.exit(1);
    }
    const urlTexts = readFileSync(urlListPath, 'utf-8').split('\n').map(l => l.trim()).filter(l => l && !l.startsWith('#') && l.startsWith('http'));
    console.log(`Batch mode: ${urlTexts.length} URLs, concurrency=${maxConcurrent}`);
    pages.push(...await fetchUrlBatch(urlTexts, maxConcurrent));
  } else if (url) {
    console.log(`Single URL: ${url}`);
    const html = await safeFetch(url);
    if (!html) { console.error('Failed to fetch'); process.exit(1); }
    pages.push({ index: 0, url, data: extractGraphFromHtml(html, url) });
  } else {
    console.log('Usage:');
    console.log('  node scrapeToGraph.mjs <url>');
    console.log('  node scrapeToGraph.mjs --url-list urls.txt [--concurrent 5] [--output graph.json] [--format d3]');
    process.exit(1);
  }

  const graph = buildGraph(pages);
  const ok = pages.filter(p => p.data).length;
  console.log(`\nGraph built: ${ok}/${pages.length} pages → ${Object.keys(graph.nodes).length} nodes, ${graph.edges.length} edges`);

  const output = useD3Format ? toD3Format(graph) : graph;
  writeFileSync(outputPath, JSON.stringify(output, null, 2), 'utf-8');
  console.log(`Written to: ${outputPath}`);
  if (useD3Format) console.log('(D3.js format: {nodes, links})');
}

main().catch(e => { console.error(e.message); process.exit(1); });
