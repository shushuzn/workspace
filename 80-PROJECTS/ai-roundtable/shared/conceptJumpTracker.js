// shared/conceptJumpTracker.js
import { cosineDistance } from './vectorUtils.js';

export class ConceptJumpTracker {
  constructor(embedder) {
    this.embedder = embedder;
    this.roundEmbeddings = [];      // 每轮平均嵌入
    this.personaEmbeddings = [];    // 每轮每个人的嵌入 [round][personaIdx]
    this.roundDeltaSHistory = [];
  }

  /**
   * 处理一轮发言：批量嵌入 → 计算 ΔS + per-persona 贡献度
   * @param {string[]} utterances - 当前轮所有发言文本（按 persona 顺序）
   * @returns {Promise<{deltaS: number, contributions: number[]}>} ΔS + 每人贡献度
   */
  async processRound(utterances) {
    if (utterances.length === 0) return { deltaS: 0, contributions: [] };

    let vectors;
    try {
      vectors = await this.embedder.embedBatch(utterances);
    } catch (err) {
      console.warn(`  ⚠ 嵌入 API 失败：${err.message}，跳过 ΔS 测量`);
      return { deltaS: 0, contributions: [] };
    }
    const dim = vectors?.[0]?.length ?? 0;
    if (dim === 0) return { deltaS: 0, contributions: [] };

    // 计算该轮平均嵌入
    const roundMean = vectors.reduce(
      (acc, v) => acc.map((a, i) => a + v[i]),
      Array(dim).fill(0)
    ).map(x => x / vectors.length);

    // 计算 ΔS
    let deltaS = 0;
    let contributions = [];
    if (this.roundEmbeddings.length > 0) {
      const prevMean = this.roundEmbeddings[this.roundEmbeddings.length - 1];
      deltaS = cosineDistance(roundMean, prevMean);

      // 每人贡献度：与上一轮均值的距离（越高说明此人推动了概念跳跃）
      contributions = vectors.map(v => cosineDistance(v, prevMean));
    }

    this.roundEmbeddings.push(roundMean);
    this.personaEmbeddings.push(vectors);
    this.roundDeltaSHistory.push(deltaS);
    return { deltaS, contributions };
  }

  /** 全局 ΔS 历史 */
  getHistory() {
    return this.roundDeltaSHistory;
  }
}
