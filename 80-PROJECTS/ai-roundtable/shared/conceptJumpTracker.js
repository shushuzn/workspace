// shared/conceptJumpTracker.js
import { cosineDistance } from './vectorUtils.js';

export class ConceptJumpTracker {
  constructor(embedder) {
    this.embedder = embedder;
    this.roundEmbeddings = [];
    this.roundDeltaSHistory = [];
  }

  /**
   * 处理一轮发言：批量嵌入 → 计算 ΔS
   * @param {string[]} utterances - 当前轮所有发言文本
   * @returns {Promise<number>} ΔS 值
   */
  async processRound(utterances) {
    if (utterances.length === 0) return 0;

    let vectors;
    try {
      vectors = await this.embedder.embedBatch(utterances);
    } catch (err) {
      // Embedder API 失败时，优雅降级：跳过 ΔS 测量，记录 0
      console.warn(`  ⚠ 嵌入 API 失败：${err.message}，跳过 ΔS 测量`);
      return 0;
    }
    const dim = vectors?.[0]?.length ?? 0;
    if (dim === 0) return 0;

    // 计算该轮平均嵌入
    const roundMean = vectors.reduce(
      (acc, v) => acc.map((a, i) => a + v[i]),
      Array(dim).fill(0)
    ).map(x => x / vectors.length);

    // 计算 ΔS
    const deltaS = this.roundEmbeddings.length > 0
      ? cosineDistance(roundMean, this.roundEmbeddings[this.roundEmbeddings.length - 1])
      : 0;

    this.roundEmbeddings.push(roundMean);
    this.roundDeltaSHistory.push(deltaS);
    return deltaS;
  }

  getHistory() {
    return this.roundDeltaSHistory;
  }
}
