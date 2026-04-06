/**
 * embed-cluster.mjs — Wikipedia articles embedding + similarity clustering
 *
 * Usage:
 *   node embed-cluster.mjs [--output DIR]
 *
 * Uses Ollama to embed all articles, computes pairwise cosine similarity,
 * outputs similarity.json and cluster-report.md.
 */

import { readFileSync, writeFileSync, existsSync, readdirSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const ARTICLES_DIR = join(__DIR, 'articles');
const OUTPUT_DIR = process.argv.includes('--output')
  ? process.argv[process.argv.indexOf('--output') + 1]
  : __DIR;
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
  try {
    const res = await fetch(`${OLLAMA}/api/embeddings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: EMBED_MODEL, prompt: text }),
      signal: AbortSignal.timeout(30000)
    });
    const data = await res.json();
    return data.embedding || null;
  } catch { return null; }
}

function scanArticles() {
  const articles = [];
  const scan = (dir) => {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      if (entry.isDirectory()) scan(join(dir, entry.name));
      else if (entry.name.endsWith('.md')) {
        const file = join(dir, entry.name);
        const content = readFileSync(file, 'utf8');
        const fm = content.match(/^---\n([\s\S]*?)\n---\n/)?.[1] || '';
        const title = fm.match(/title:\s*(.+)/)?.[1]?.trim() || entry.name.replace('.md', '');
        const category = fm.match(/category:\s*(.+)/)?.[1]?.trim() || '未分类';
        const tags = ((fm.match(/tags:\s*\[(.+)\]/)?.[1]) || '').split(',').map(t => t.trim()).filter(Boolean);
        const body = content.replace(/---[\s\S]*?---\n/, '').replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim();
        articles.push({ id: slugify(title), title, category, tags, body });
      }
    }
  };
  scan(ARTICLES_DIR);
  return articles;
}

async function main() {
  mkdirSync(OUTPUT_DIR, { recursive: true });
  const articles = scanArticles();
  console.log(`[embed] Embedding ${articles.length} articles...`);

  // Embed all articles
  const embeddings = {};
  for (const art of articles) {
    const emb = await embed(`${art.title}: ${art.body.slice(0, 500)}`);
    if (emb) {
      embeddings[art.id] = emb;
      console.log(`  ✓ ${art.title}`);
    } else {
      console.log(`  ✗ ${art.title} (embedding failed)`);
    }
  }

  // Compute pairwise similarity
  const ids = Object.keys(embeddings);
  const similarity = {};
  for (let i = 0; i < ids.length; i++) {
    for (let j = i + 1; j < ids.length; j++) {
      const sim = cosineSim(embeddings[ids[i]], embeddings[ids[j]]);
      similarity[`${ids[i]}<->${ids[j]}`] = parseFloat(sim.toFixed(4));
    }
  }

  // Write similarity.json
  const simFile = join(OUTPUT_DIR, 'similarity.json');
  writeFileSync(simFile, JSON.stringify({ articles: articles.map(a => ({ id: a.id, title: a.title, category: a.category })), similarity }, null, 2));
  console.log(`\n[embed] Wrote ${simFile}`);

  // Hierarchical clustering (single-linkage, threshold 0.7)
  const THRESHOLD = 0.7;
  const clusters = [];
  const assigned = new Set();
  const pairs = Object.entries(similarity).sort((a, b) => b[1] - a[1]);

  for (const [pair, sim] of pairs) {
    if (sim < THRESHOLD) break;
    const [idA, idB] = pair.split('<->');
    const artA = articles.find(a => a.id === idA);
    const artB = articles.find(a => a.id === idB);
    if (!artA || !artB) continue;

    const clusterA = clusters.find(c => c.members.includes(idA));
    const clusterB = clusters.find(c => c.members.includes(idB));

    if (!clusterA && !clusterB) {
      clusters.push({ members: [idA, idB], sim, label: artA.category });
    } else if (clusterA && !clusterB) {
      clusterA.members.push(idB);
    } else if (!clusterA && clusterB) {
      clusterB.members.push(idA);
    } else if (clusterA && clusterB && clusterA !== clusterB) {
      clusterA.members.push(...clusterB.members);
      clusters.splice(clusters.indexOf(clusterB), 1);
    }
  }

  // Singletons as their own clusters
  const allMembers = new Set(clusters.flatMap(c => c.members));
  for (const art of articles) {
    if (!allMembers.has(art.id)) {
      clusters.push({ members: [art.id], sim: 1.0, label: art.category });
    }
  }

  // Generate report
  const report = `# Wikipedia 知识聚类报告

生成时间: ${new Date().toISOString()}
聚类阈值: ${THRESHOLD}

## 聚类结果

${clusters.map((c, i) => {
  const arts = c.members.map(id => articles.find(a => a.id === id)).filter(Boolean);
  return `### 知识领域 ${i + 1}

- 成员: ${arts.map(a => a.title).join(', ')}
- 分类: ${[...new Set(arts.map(a => a.category))].join(', ')}
- 内部相似度: ${c.sim.toFixed(3)}
`;
}).join('\n')}

## 知识领域分布

${Object.entries(articles.reduce((acc, a) => { acc[a.category] = (acc[a.category] || 0) + 1; return acc; }, {})).map(([c, n]) => `- ${c}: ${n}篇`).join('\n')}

## 相似度矩阵

|  | ${ids.map(id => articles.find(a => a.id === id)?.title.slice(0, 10)).join(' | ')} |
${'|---'.repeat(ids.length + 1)}|
${ids.map(idA => {
  const row = ids.map(idB => {
    if (idA === idB) return '1.000';
    return similarity[`${idA}<->${idB}`]?.toFixed(3) || '-';
  });
  return `| ${articles.find(a => a.id === idA)?.title.slice(0, 10)} | ${row.join(' | ')} |`;
}).join('\n')}
`;

  const reportFile = join(OUTPUT_DIR, 'cluster-report.md');
  writeFileSync(reportFile, report, 'utf8');
  console.log(`[embed] Wrote ${reportFile}`);
}

main().catch(e => { console.error('[embed]', e.message); process.exit(1); });
