// shared/bridgeDiscovery.js
import { cosineDistance } from './vectorUtils.js';

const OLLAMA_URL = process.env.OLLAMA_URL || 'http://localhost:11434';
const OLLAMA_MODEL = process.env.OLLAMA_MODEL || 'llama3.2:1b';

/**
 * 发现桥接概念 — 当讨论趋于同温层时，注入第三方概念打破共识
 *
 * @param {Object} params
 * @param {string[]} params.positiveUtterances — 正方发言（deltaS 最高的发言）
 * @param {string[]} params.negativeUtterances — 反方发言（deltaS 最低的发言）
 * @param {string[]} params.bridgePool — 候选桥接概念池
 * @param {number} [params.topK=3] — 返回前几个桥接概念
 * @param {Object} [options] — 可选：{ ollamaUrl, model }
 * @returns {Promise<string[]>} 桥接概念名称数组
 */
export async function discoverBridgeConcepts(
  { positiveUtterances, negativeUtterances, bridgePool, topK = 3 },
  options = {}
) {
  const ollamaUrl = options.ollamaUrl || OLLAMA_URL;
  const model = options.model || OLLAMA_MODEL;

  // bridgePool 上限 50 个，避免延迟
  const pool = bridgePool.slice(0, 50);

  if (
    pool.length === 0 ||
    (positiveUtterances.length === 0 && negativeUtterances.length === 0)
  ) {
    return [];
  }

  try {
    // 1. 批量获取 positive / negative / pool 的 embedding
    const allTexts = [...positiveUtterances, ...negativeUtterances, ...pool];
    const embeddings = await _embedOllama(allTexts, ollamaUrl, model);
    if (!embeddings || embeddings.length === 0) return [];

    const posEmbeds = embeddings.slice(0, positiveUtterances.length);
    const negEmbeds = embeddings.slice(
      positiveUtterances.length,
      positiveUtterances.length + negativeUtterances.length
    );
    const poolEmbeds = embeddings.slice(
      positiveUtterances.length + negativeUtterances.length
    );

    // 2. 合并 positive / negative 为单一向量（取平均）
    const posVec = _meanVector(posEmbeds);
    const negVec = _meanVector(negEmbeds);

    // 3. 对每个候选概念计算 distance(pos, c) + distance(c, neg)
    const scored = poolEmbeds.map((cEmbed, i) => {
      const dPos = cosineDistance(posVec, cEmbed);
      const dNeg = cosineDistance(cEmbed, negVec);
      return { index: i, sum: dPos + dNeg };
    });

    // 4. 取 sum 最小的 topK
    scored.sort((a, b) => a.sum - b.sum);
    return scored.slice(0, topK).map(s => pool[s.index]);
  } catch {
    // Ollama 不可用时返回空数组，不抛出异常
    return [];
  }
}

/**
 * 简单名词短语提取 — 从发言文本中提取高频概念词
 * 简化实现：按空格分词，取 2-4 字词组合，过滤停用词
 * @param {string[]} utterances
 * @returns {string[]}
 */
export function extractBridgePool(utterances) {
  const stopWords = new Set([
    '的',
    '了',
    '是',
    '在',
    '和',
    '有',
    '我',
    '你',
    '他',
    '她',
    '它',
    '这',
    '那',
    '就',
    '也',
    '都',
    '会',
    '能',
    '要',
    '可以',
    '一个',
    '什么',
    '怎么',
    '为什么',
    '如果',
    '因为',
    '所以',
    '但是',
    '而且',
    '其实',
    '可能',
    '应该',
    '认为',
    '觉得',
    '问题',
    '时候',
    '情况',
    '对方',
    '我们',
    '他们',
    '自己',
    '这个',
    '那个',
    '一些',
    '可能',
  ]);

  const wordCount = new Map();
  for (const utt of utterances) {
    // 移除链式思维前缀（英文指令如 "1. 2句以内。2. 结尾必须..."）
    // 以及编号列表、数字前缀等干扰
    const cleaned = utt
      .replace(
        /^[A-Za-z][\s\S]*?(?:我需要|让我|Let me|The user|用户).*?[。？！\n]/g,
        ''
      ) // 移除英文链式思维
      .replace(/^\d+[.、.\s]+/gm, '') // 移除行首编号 "1. 2. "
      .replace(/^[A-Za-z][：:]/gm, '') // 移除行首英文前缀 "X:"
      .replace(/[""''""'']/g, '') // 移除引号
      .replace(/[()（）【】[\]]/g, '') // 移除括号
      .trim();

    // 提取 2-4 字的中文词/词组
    const words = cleaned.match(/[\u4e00-\u9fa5]{2,4}/g) || [];
    for (const w of words) {
      if (!stopWords.has(w) && !/^\d+$/.test(w)) {
        wordCount.set(w, (wordCount.get(w) || 0) + 1);
      }
    }
    // 同时提取英文词（仅从含中文的句子中提取，避免纯英文链式思维干扰）
    if (/[\u4e00-\u9fa5]/.test(cleaned)) {
      const enWords = cleaned.match(/[a-zA-Z]{3,}/g) || [];
      for (const w of enWords) {
        const lower = w.toLowerCase();
        if (!stopWords.has(lower)) {
          wordCount.set(w, (wordCount.get(w) || 0) + 1);
        }
      }
    }
  }

  // 按频次降序，取前 50 个
  return Array.from(wordCount.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, 50)
    .map(([word]) => word);
}

// ─── 内部工具函数 ──────────────────────────────────────

async function _embedOllama(texts, ollamaUrl, model) {
  const url = `${ollamaUrl}/api/embed`;
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model, input: texts }),
  });
  if (!res.ok) return [];
  const data = await res.json();
  return data.embeddings ?? [];
}

function _meanVector(vectors) {
  if (vectors.length === 0) return [];
  const dim = vectors[0].length;
  const out = new Array(dim).fill(0);
  for (const v of vectors) {
    for (let i = 0; i < dim; i++) {
      out[i] += v[i];
    }
  }
  const n = vectors.length;
  for (let i = 0; i < dim; i++) {
    out[i] /= n;
  }
  return out;
}
