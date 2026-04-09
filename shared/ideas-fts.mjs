#!/usr/bin/env node
/**
 * ideas-fts.mjs
 * PostgreSQL pgvector semantic search for ideas.md
 * Usage:
 *   node shared/ideas-fts.mjs init    # build vector index from ideas.md
 *   node shared/ideas-fts.mjs search "query"
 */
import { existsSync, readFileSync, writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import pg from 'pg';

const { Client } = pg;
const __DIR = dirname(fileURLToPath(import.meta.url));
const IDEAS_PATH = join(__DIR, '..', '.omc', 'innovation', 'ideas.md');
const CONFIG_PATH = join(__DIR, '..', '.omc', 'innovation', 'ideas-pgvector.json');

const EMBED_URL = 'https://api.jina.ai/v1/embeddings';
const EMBED_MODEL = 'jina-embeddings-v3';
const EMBED_API_KEY = 'jina_c4041ff26456495ba4596e9805764c05pxC5qrO7A27XGrtp_K5830Sausul';

const PG_CONFIG = {
  host: '127.0.0.1',
  port: 5432,
  database: 'postgres',
  user: 'postgres',
  password: '123456'
};

// ── Embedding ───────────────────────────────────────────────────────────────
import { ProxyAgent } from 'undici';

const proxyDispatcher = new ProxyAgent('http://127.0.0.1:7897');

async function embedText(text) {
  const { request } = await import('undici');
  const res = await request(EMBED_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${EMBED_API_KEY}`
    },
    body: JSON.stringify({ model: EMBED_MODEL, input: text }),
    dispatcher: proxyDispatcher
  });
  if (res.statusCode !== 200) throw new Error(`Embedding API error: ${res.statusCode}`);
  const data = await res.body.json();
  return data.data?.[0]?.embedding;
}

// ── Parse ideas.md ─────────────────────────────────────────────────────────
function parseIdeas(content) {
  const lines = content.split('\n');
  const entries = [];
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    const match = line.match(/^- \[(\d{8})\] seed \[([^\]]+)\] \[score:([^\]]+)\] \[f:(\d+)\] \[angle:([^\]]+)\]/);
    if (match) {
      const [, date, source, score, f, angle] = match;
      const bodyLines = [];
      let j = i + 1;
      while (j < lines.length && lines[j].match(/^\s{2}/)) {
        bodyLines.push(lines[j].trim());
        j++;
      }
      const bodyText = bodyLines.join('\n');
      const focusMatch = line.match(/\[focus:([^\]]+)\]/);
      const benefitMatch = bodyText.match(/benefit:\s*(.+?)(?:\s*\| reason:|$)/s);

      entries.push({
        date, source, score, f: parseInt(f), angle,
        focus: focusMatch ? focusMatch[1] : '',
        desc: line.replace(/^\s*/, '').split('|')[0].replace(/.*\]\s*[\w-]+\s*/, '').trim(),
        benefit: benefitMatch ? benefitMatch[1].trim() : '',
        full_text: line + '\n' + bodyText
      });
      i = j;
    } else {
      i++;
    }
  }
  return entries;
}

// ── Init command ──────────────────────────────────────────────────────────────
async function cmdInit() {
  const client = new Client(PG_CONFIG);
  await client.connect();

  // Enable vector extension
  await client.query('CREATE EXTENSION IF NOT EXISTS vector');

  // Create table
  await client.query(`
    CREATE TABLE IF NOT EXISTS ideas_vec (
      id SERIAL PRIMARY KEY,
      date TEXT,
      score TEXT,
      f INTEGER,
      angle TEXT,
      focus TEXT,
      "desc" TEXT,
      benefit TEXT,
      embedding vector(1024)
    )
  `);

  // Clear old data
  await client.query('DELETE FROM ideas_vec');

  const content = readFileSync(IDEAS_PATH, 'utf8');
  const entries = parseIdeas(content);

  console.log(`[ideas-pgvector] Indexing ${entries.length} ideas...`);

  for (let k = 0; k < entries.length; k++) {
    const e = entries[k];
    process.stdout.write(`\r  ${k + 1}/${entries.length}...`);
    const embedding = await embedText(e.full_text);
    if (!embedding) {
      console.error(`\n[ERROR] Failed to embed: ${e.desc}`);
      continue;
    }
    await client.query(
      `INSERT INTO ideas_vec (date, score, f, angle, focus, "desc", benefit, embedding)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8)`,
      [e.date, e.score, e.f, e.angle, e.focus, e.desc, e.benefit, JSON.stringify(embedding)]
    );
  }

  console.log(`\n[ideas-pgvector] Indexed ${entries.length} ideas → PostgreSQL`);

  // Save config
  writeFileSync(CONFIG_PATH, JSON.stringify({ count: entries.length, indexed_at: new Date().toISOString() }), 'utf8');

  await client.end();
}

// ── Search command ──────────────────────────────────────────────────────────
async function cmdSearch(query) {
  const client = new Client(PG_CONFIG);
  await client.connect();

  const embedding = await embedText(query);
  if (!embedding) {
    console.error('[ERROR] Failed to embed query');
    await client.end();
    return;
  }

  const result = await client.query(`
    SELECT date, score, f, angle, "desc",
           1 - (embedding <=> $1) AS similarity
    FROM ideas_vec
    ORDER BY embedding <=> $1
    LIMIT 10
  `, [JSON.stringify(embedding)]);

  if (result.rows.length === 0) {
    console.log(`\n=== pgvector Search: "${query}" ===\nNo results found.\n`);
    await client.end();
    return;
  }

  console.log(`\n=== pgvector Search: "${query}" ===\n`);
  for (const row of result.rows) {
    console.log(`[${row.date}] ${row.desc} (sim:${Number(row.similarity).toFixed(3)})`);
    console.log(`  angle: ${row.angle} | f: ${row.f}`);
    console.log('');
  }

  await client.end();
}

// ── CLI ──────────────────────────────────────────────────────────────────────
const cmd = process.argv[2];

if (cmd === 'init') {
  cmdInit().catch(e => { console.error(e); process.exit(1); });
} else if (cmd === 'search' && process.argv[3]) {
  cmdSearch(process.argv.slice(3).join(' ')).catch(e => { console.error(e); process.exit(1); });
} else {
  console.log('Usage:');
  console.log('  node shared/ideas-fts.mjs init              # build pgvector index');
  console.log('  node shared/ideas-fts.mjs search "query"    # semantic search');
}
