// shared/embedder.js
import 'dotenv/config';

const MINIMAX_API_URL = process.env.EMBEDDER_API_URL || 'https://api.minimaxi.com/v1/embeddings';
const MINIMAX_MODEL = process.env.EMBEDDER_MODEL || 'embedding-2';
const MINIMAX_API_KEY = process.env.MINIMAX_API_KEY;
const OLLAMA_URL = process.env.OLLAMA_URL || 'http://localhost:11434';
const OLLAMA_MODEL = process.env.OLLAMA_MODEL || 'llama3.2:1b';

/** MiniMax 嵌入（主用，余额不足时自动降级到 Ollama） */
export class MiniMaxEmbedder {
  /** 单文本嵌入 */
  async embed(text) {
    // 尝试 MiniMax
    const mmVec = await this._embedMinimax(text);
    if (mmVec.length > 0) return mmVec;
    // 降级到 Ollama
    return this._embedOllama(text);
  }

  /** 批量嵌入（单次 API 调用） */
  async embedBatch(texts) {
    // 尝试 MiniMax
    const mmVecs = await this._embedBatchMinimax(texts);
    if (mmVecs.length > 0 && mmVecs[0].length > 0) return mmVecs;
    // 降级到 Ollama
    return this._embedBatchOllama(texts);
  }

  async _embedMinimax(text) {
    try {
      const res = await fetch(MINIMAX_API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${MINIMAX_API_KEY}`,
        },
        body: JSON.stringify({ model: MINIMAX_MODEL, input: text }),
      });
      if (!res.ok) return [];
      const data = await res.json();
      // MiniMax 返回 { data: [{ embedding: [...] }] } 或 { vectors: [...] }
      if (data.data?.[0]?.embedding?.length > 0) {
        return data.data[0].embedding;
      }
      if (data.vectors?.[0]?.length > 0) {
        return data.vectors[0];
      }
      return [];
    } catch {
      return [];
    }
  }

  async _embedOllama(text) {
    const res = await fetch(`${OLLAMA_URL}/api/embed`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: OLLAMA_MODEL, input: text }),
    });
    if (!res.ok) return [];
    const data = await res.json();
    return data.embeddings?.[0] ?? [];
  }

  async _embedBatchMinimax(texts) {
    try {
      const res = await fetch(MINIMAX_API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${MINIMAX_API_KEY}`,
        },
        body: JSON.stringify({ model: MINIMAX_MODEL, input: texts }),
      });
      if (!res.ok) return [];
      const data = await res.json();
      if (data.data?.length > 0) {
        return data.data.map(item => item.embedding ?? []);
      }
      if (data.vectors?.[0]?.length > 0) {
        return data.vectors;
      }
      return [];
    } catch {
      return [];
    }
  }

  async _embedBatchOllama(texts) {
    // Ollama /api/embed 支持批量 input: string[]
    const res = await fetch(`${OLLAMA_URL}/api/embed`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: OLLAMA_MODEL, input: texts }),
    });
    if (!res.ok) return [];
    const data = await res.json();
    return data.embeddings ?? [];
  }
}
