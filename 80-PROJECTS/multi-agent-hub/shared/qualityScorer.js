import { cosineDistance } from './vectorUtils.js';

export class QualityScorer {
  constructor() {
    this.prevPersonaEmbeddings = [];
  }

  reset() {
    this.prevPersonaEmbeddings = [];
  }

  /**
   * @param {number[][]} personaEmbeddings - [personaCount][dim]
   * @param {number} deltaS - deltaS from ConceptJumpTracker
   * @param {number[]} contributions - contributions from ConceptJumpTracker
   * @returns {{ quality: number, fluidity: number, jump: number, balance: number }}
   */
  scoreRound(personaEmbeddings, deltaS, contributions) {
    const ε = 0.001;

    let fluidity = 0.5;
    if (this.prevPersonaEmbeddings.length > 0) {
      const prev =
        this.prevPersonaEmbeddings[this.prevPersonaEmbeddings.length - 1];
      if (prev.length !== personaEmbeddings.length) {
        fluidity = 0.5;
      } else {
        fluidity =
          personaEmbeddings.reduce(
            (sum, emb, i) => sum + cosineDistance(emb, prev[i]),
            0
          ) / personaEmbeddings.length;
      }
    }

    const jump = deltaS;

    // contributions 为空时（嵌入失败）降级为中性分
    const mean =
      contributions.length > 0
        ? contributions.reduce((a, b) => a + b, 0) / contributions.length
        : 0;
    const std =
      contributions.length > 0
        ? Math.sqrt(
            contributions.reduce((s, v) => s + (v - mean) ** 2, 0) /
              contributions.length
          )
        : 0;
    const balance = Math.max(0, Math.min(1, 1 - std / (mean + ε)));

    const quality = fluidity * 0.4 + jump * 0.3 + balance * 0.3;

    this.prevPersonaEmbeddings.push(personaEmbeddings);
    return {
      quality: Math.min(100, quality * 100),
      fluidity,
      jump,
      balance,
    };
  }
}
