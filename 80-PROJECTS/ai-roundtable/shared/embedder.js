// shared/embedder.js
import 'dotenv/config';

const EMBED_API_URL = process.env.EMBEDDER_API_URL || 'https://api.minimaxi.com/v1/embeddings';
const EMBED_MODEL = process.env.EMBEDDER_MODEL || 'embedding-2';
const EMBED_API_KEY = process.env.MINIMAX_API_KEY;  // 复用已有 key

export class MiniMaxEmbedder {
  /** 单文本嵌入 */
  async embed(text) {
    const res = await fetch(EMBED_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${EMBED_API_KEY}`,
      },
      body: JSON.stringify({ model: EMBED_MODEL, input: text }),
    });
    if (!res.ok) throw new Error(`Embedding API error: ${res.status}`);
    const data = await res.json();
    return data.data?.[0]?.embedding ?? [];
  }

  /** 批量嵌入（单次 API 调用） */
  async embedBatch(texts) {
    const res = await fetch(EMBED_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${EMBED_API_KEY}`,
      },
      body: JSON.stringify({ model: EMBED_MODEL, input: texts }),
    });
    if (!res.ok) throw new Error(`Embedding API error: ${res.status}`);
    const data = await res.json();
    return (data.data ?? []).map(item => item.embedding ?? []);
  }
}
