import { cosineDistance } from './vectorUtils.js';

export class QualityScorer {
  constructor() {
    this.prevPersonaEmbeddings = [];
  }

  scoreRound(personaEmbeddings, deltaS, contributions) {
    const ε = 0.001;

    let fluidity = 0.5;
    if (this.prevPersonaEmbeddings.length > 0) {
      const prev = this.prevPersonaEmbeddings[this.prevPersonaEmbeddings.length - 1];
      fluidity = personaEmbeddings.reduce((sum, emb, i) =>
        sum + cosineDistance(emb, prev[i]), 0) / personaEmbeddings.length;
    }

    const jump = deltaS;

    const mean = contributions.reduce((a, b) => a + b, 0) / contributions.length;
    const std = Math.sqrt(
      contributions.reduce((s, v) => s + (v - mean) ** 2, 0) / contributions.length
    );
    const balance = 1 - (std / (mean + ε));

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
