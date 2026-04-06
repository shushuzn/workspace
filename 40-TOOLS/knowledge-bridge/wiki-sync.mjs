/**
 * wiki-sync.mjs — Wikipedia articles → Knowledge Bridge graph sync
 *
 * Usage:
 *   node wiki-sync.mjs [--wiki DIR] [--output FILE]
 *
 * Reads wikipedia articles/, extracts nodes (id/title/category/tags)
 * and edges (wiki-links), outputs JSON graph for knowledge-bridge import.
 */

import { readFileSync, writeFileSync, existsSync, readdirSync } from 'fs';
import { join, dirname, basename } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));

const WIKI_DIR = process.env.WIKI_DIR || join(__DIR, '..', '..', 'knowledge', 'wikipedia');
const OUTPUT_FILE = process.env.OUTPUT_FILE || join(__DIR, 'data', 'wiki-nodes.json');
const ARTICLES_DIR = join(WIKI_DIR, 'articles');

function slugify(title) {
  return title.toLowerCase().replace(/[^\w\s\u4e00-\u9fa5]/g, '').replace(/\s+/g, '-').replace(/-+/g, '-').slice(0, 60);
}

function scanArticles() {
  const articles = [];
  const scan = (dir) => {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      if (entry.isDirectory()) scan(join(dir, entry.name));
      else if (entry.name.endsWith('.md')) {
        const file = join(dir, entry.name);
        const content = readFileSync(file, 'utf8');
        // Extract frontmatter
        const fmMatch = content.match(/^---\n([\s\S]*?)\n---\n/);
        const frontmatter = fmMatch ? fmMatch[1] : '';
        const titleMatch = frontmatter.match(/title:\s*(.+)/);
        const categoryMatch = frontmatter.match(/category:\s*(.+)/);
        const tagsMatch = frontmatter.match(/tags:\s*\[(.+)\]/);
        const idMatch = frontmatter.match(/id:\s*(.+)/);
        const title = titleMatch ? titleMatch[1].trim() : entry.name.replace('.md', '');
        const category = categoryMatch ? categoryMatch[1].trim() : '未分类';
        const tags = tagsMatch ? tagsMatch[1].split(',').map(t => t.trim()).filter(Boolean) : [];
        const id = idMatch ? idMatch[1].trim() : slugify(title);

        // Extract wiki-links
        const wikiLinks = [...content.matchAll(/\[\[([^\]]+)\]\]/g)].map(m => m[1]);
        const body = content.replace(/---[\s\S]*?---\n/, '').replace(/<[^>]+>/g, '').trim();

        articles.push({ id, title, category, tags, wikiLinks, body, file: entry.name });
      }
    }
  };
  if (!existsSync(ARTICLES_DIR)) {
    console.error('[wiki-sync] articles/ not found at', ARTICLES_DIR);
    process.exit(1);
  }
  scan(ARTICLES_DIR);
  return articles;
}

function main() {
  const articles = scanArticles();

  // Build nodes and edges
  const nodes = articles.map(a => ({
    id: `wiki:${a.id}`,
    label: a.title,
    group: 'wikipedia',
    category: a.category,
    tags: a.tags,
    summary: a.body.slice(0, 200)
  }));

  const edges = [];
  const addedEdges = new Set();
  for (const a of articles) {
    for (const link of (a.wikiLinks || [])) {
      const linkSlug = slugify(link);
      const target = articles.find(art =>
        art.id.includes(linkSlug) || slugify(art.title) === linkSlug
      );
      if (target) {
        const edgeId = `${a.id}->${target.id}`;
        if (!addedEdges.has(edgeId)) {
          addedEdges.add(edgeId);
          edges.push({
            from: `wiki:${a.id}`,
            to: `wiki:${target.id}`,
            type: 'wiki-link',
            label: 'wiki'
          });
        }
      }
    }
  }

  const output = { nodes, edges, meta: { source: 'wikipedia', count: articles.length, synced: new Date().toISOString() } };
  writeFileSync(OUTPUT_FILE, JSON.stringify(output, null, 2), 'utf8');
  console.log(`[wiki-sync] Wrote ${nodes.length} nodes + ${edges.length} edges → ${OUTPUT_FILE}`);
}

main();
