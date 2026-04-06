/**
 * Embedding abstraction layer for Semantic Task Router.
 * Supports Ollama (nomic-embed-text) and OpenAI-compatible backends.
 */
import { readFileSync, existsSync } from 'fs';
import { join } from 'path';
import { homedir } from 'os';

function loadConfig() {
  const configPath = join(homedir(), '.unified-agent-cli', 'embed.config.json');
  if (existsSync(configPath)) {
    try { return JSON.parse(readFileSync(configPath, 'utf-8')); } catch {}
  }
  return {
    provider: 'ollama',
    baseUrl: process.env.OLLAMA_BASE ?? 'http://127.0.0.1:11434',
    model: 'nomic-embed-text',
  };
}

export async function embed(text) {
  const config = loadConfig();
  if (config.provider === 'ollama') {
    const res = await fetch(`${config.baseUrl}/api/embeddings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: config.model ?? 'nomic-embed-text', prompt: text }),
    });
    if (!res.ok) throw new Error(`Ollama embed failed: ${res.status}`);
    const data = await res.json();
    return { embedding: data.embedding, model: config.model ?? 'nomic-embed-text' };
  }
  const apiKey = process.env.OPENAI_API_KEY ?? process.env.API_KEY;
  const res = await fetch(`${config.baseUrl}/embeddings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${apiKey}` },
    body: JSON.stringify({ model: config.model ?? 'text-embedding-3-small', input: text }),
  });
  if (!res.ok) throw new Error(`OpenAI embed failed: ${res.status}`);
  const data = await res.json();
  return { embedding: data.data[0].embedding, model: config.model ?? 'text-embedding-3-small' };
}

export function cosineSimilarity(a, b) {
  let dot = 0, normA = 0, normB = 0;
  for (let i = 0; i < a.length; i++) {
    dot += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }
  return dot / (Math.sqrt(normA) * Math.sqrt(normB));
}
