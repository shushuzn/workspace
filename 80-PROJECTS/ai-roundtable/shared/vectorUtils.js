// shared/vectorUtils.js
/**
 * cosineDistance — 余弦距离，1 - cosine_similarity
 * @param {number[]} a
 * @param {number[]} b
 * @returns {number}
 */
export function cosineDistance(a, b) {
  const dot = a.reduce((s, ai, i) => s + ai * b[i], 0);
  const normA = Math.sqrt(a.reduce((s, ai) => s + ai * ai, 0));
  const normB = Math.sqrt(b.reduce((s, bi) => s + bi * bi, 0));
  if (normA === 0 || normB === 0) return 1.0;
  return 1 - dot / (normA * normB);
}
