/**
 * Tool Router (Core Layer)
 * Balances exploration vs exploitation for operation selection
 * Refactored from: epsilon-greedy.mjs
 */

import { CONFIG } from '../config/default.mjs';
import { WorkingMemory } from './working-memory.mjs';

export class ToolRouter {
  constructor(workspace, operations, history) {
    this.workspace = workspace;
    this.operations = operations;
    this.history = history;
    this.workingMemory = new WorkingMemory(workspace);
    this.gaps = []; // MetaCognizer gaps - injected via setGaps()
    this.ltmKnowledge = []; // LTM successful operations
    this.candidatePool = null; // Learn layer candidate pool
  }

  setGaps(gaps) {
    this.gaps = gaps;
  }

  setLTMKnowledge(knowledge) {
    this.ltmKnowledge = knowledge;
  }

  setCandidatePool(pool) {
    this.candidatePool = pool;
  }

  getEpsilon() {
    const base = this.history.epsilon;
    // Health-based adjustment: low health forces more exploration
    const score = this.workingMemory.calculate();
    if (score < 40) {
      return Math.min(CONFIG.epsilon.max, base + 0.2); // +20% when critical
    } else if (score < 60) {
      return Math.min(CONFIG.epsilon.max, base + 0.1); // +10% when low
    }
    return base;
  }

  getEpsilonMin() {
    const score = this.workingMemory.calculate();
    return score > 90 ? CONFIG.epsilon.minHighScore : CONFIG.epsilon.min;
  }

  isDetectionOp(opId) {
    return CONFIG.cooldown.detectionOps.includes(opId);
  }

  getCooldown(opId) {
    return this.isDetectionOp(opId) ? CONFIG.cooldown.detection : CONFIG.cooldown.productive;
  }

  isNewOp(opId) {
    return !this.history.records.some(r => r.opId === opId);
  }

  select() {
    const epsilon = this.getEpsilon();

    if (Math.random() < epsilon) {
      return this.explore();
    }
    return this.exploit();
  }

  explore() {
    const candidates = this.getViableCandidates();
    if (candidates.length === 0) {
      // Fallback to productive op
      const productive = this.operations.filter(op => !this.isDetectionOp(op.id));
      const op = productive[Math.floor(Math.random() * productive.length)] || this.operations[0];
      console.log(`[ToolRouter] 探索模式: ${op.name} [兜底选productive]`);
      return { op, mode: 'explore' };
    }

    // Prefer new operations
    const newCandidates = candidates.filter(op => this.isNewOp(op.id));
    const pickFrom = newCandidates.length > 0 ? newCandidates : candidates;
    const op = pickFrom[Math.floor(Math.random() * pickFrom.length)];

    if (newCandidates.length > 0) {
      console.log(`[ToolRouter] 探索模式: ${op.name} [新操作优先]`);
    } else {
      console.log(`[ToolRouter] 探索模式: ${op.name}`);
    }
    return { op, mode: 'explore' };
  }

  exploit() {
    const successRates = this.calculateSuccessRates();
    const candidates = this.getViableCandidates()
      .filter(op => !this.isDetectionOp(op.id));

    let bestOp = null;
    let bestScore = -1;

    for (const op of candidates) {
      const rate = successRates[op.id];
      let baseScore = 0;

      if (rate && rate.total >= 1) {
        baseScore = rate.success / rate.total;
      } else if (this.isNewOp(op.id)) {
        baseScore = 0.1; // New ops get minimum score
      }

      // Gap priority bonus: high-priority gaps boost related ops
      const gapBonus = this.getGapBonus(op);

      // LTM knowledge bonus: operations with successful history in LTM
      const ltmBonus = this.getLTMBonus(op);

      // Novelty bonus for unexplored operations
      const noveltyBonus = this.isNewOp(op.id) ? 0.05 : 0;

      // CandidatePool bonus: pending high-priority candidates get boosted
      const poolBonus = this.getPoolBonus(op);

      // Rule bonus: operations that tend to succeed after the previous successful operation
      const ruleBonus = this.getRuleBonus(op);

      const totalScore = baseScore + gapBonus + ltmBonus + noveltyBonus + poolBonus + ruleBonus;

      if (totalScore > bestScore) {
        bestScore = totalScore;
        bestOp = op;
      }
    }

    if (!bestOp || bestScore <= 0) {
      return this.fallbackSelection();
    }

    if (!this.canImprove(bestOp)) {
      return this.findAlternativeBest(successRates);
    }

    const gapNote = this.getGapBonus(bestOp) > 0 ? ' [gap优先级]' : '';
    console.log(`[ToolRouter] 利用模式: ${bestOp.name} (得分: ${(bestScore * 100).toFixed(0)}%)${gapNote}`);
    return { op: bestOp, mode: 'exploit' };
  }

  getGapBonus(op) {
    if (!this.gaps || this.gaps.length === 0) return 0;

    // Match operation to gap via opId or name similarity
    const opGaps = this.gaps.filter(g => {
      // Direct match by target (opId)
      if (g.target === op.id) return true;
      // Name contains match (fuzzy)
      if (g.name && op.name && (
        op.name.includes(g.name.substring(0, 8)) ||
        g.name.includes(op.name.substring(0, 8))
      )) return true;
      return false;
    });

    if (opGaps.length === 0) return 0;

    // Highest priority gap determines bonus
    const priorityBonus = { high: 0.3, medium: 0.15, low: 0.05 };
    const highestPriority = opGaps.reduce((best, g) => {
      const order = { high: 0, medium: 1, low: 2 };
      return order[g.priority] < order[best.priority] ? g : best;
    }, opGaps[0]);

    return priorityBonus[highestPriority.priority] || 0;
  }

  getLTMBonus(op) {
    if (!this.ltmKnowledge || this.ltmKnowledge.length === 0) return 0;

    // Find if this operation has successful LTM history
    const ltmEntry = this.ltmKnowledge.find(e => e.entity === op.id);
    if (!ltmEntry) return 0;

    // Bonus based on delta magnitude (higher improvement = higher bonus)
    const delta = ltmEntry.metadata?.delta || 0;
    if (delta > 10) return 0.2;
    if (delta > 5) return 0.15;
    if (delta > 0) return 0.1;
    return 0;
  }

  getPoolBonus(op) {
    if (!this.candidatePool) return 0;

    const top = this.candidatePool.getTop(3);
    if (top.length === 0) return 0;

    // Match op to a pending candidate
    const match = top.find(c =>
      c.target === op.id ||
      (c.name && op.name && (
        op.name.includes(c.name.substring(0, 6)) ||
        c.name.includes(op.name.substring(0, 6))
      ))
    );

    if (!match) return 0;

    // Bonus based on priority
    const bonus = { high: 0.25, medium: 0.15, low: 0.05 };
    return bonus[match.priority] || 0.1;
  }

  /**
   * Rule bonus: operations that historically followed a successful operation
   * (chain pattern from Distiller sequences)
   */
  getRuleBonus(op) {
    if (!this.history.records || this.history.records.length < 3) return 0;

    // Find last successful operation
    let lastSuccessful = null;
    for (let i = this.history.records.length - 1; i >= 0; i--) {
      const r = this.history.records[i];
      if (r.improved) { lastSuccessful = r.opId; break; }
    }
    if (!lastSuccessful) return 0;

    // Count: how many times does this op follow the lastSuccessful op and result in improvement?
    let chainCount = 0;
    let chainImproved = 0;
    for (let i = 0; i < this.history.records.length - 1; i++) {
      const curr = this.history.records[i];
      const next = this.history.records[i + 1];
      if (curr.opId === lastSuccessful && next.opId === op.id) {
        chainCount++;
        if (next.improved) chainImproved++;
      }
    }
    if (chainCount === 0) return 0;
    // Bonus proportional to chain success rate
    const chainRate = chainImproved / chainCount;
    return chainRate > 0.5 ? 0.15 * chainRate : 0;
  }

  calculateSuccessRates() {
    const rates = {};
    for (const record of this.history.records) {
      if (!rates[record.opId]) {
        rates[record.opId] = { success: 0, total: 0 };
      }
      rates[record.opId].total++;
      if (record.improved) {
        rates[record.opId].success++;
      }
    }
    return rates;
  }

  getViableCandidates() {
    return this.operations.filter(op => {
      const cd = this.getCooldown(op.id);
      const recent = this.history.records.slice(-cd).map(r => r.opId);
      return !recent.includes(op.id);
    });
  }

  canImprove(op) {
    // Implementation of canImprove logic for each operation type
    return true; // Default
  }

  fallbackSelection() {
    const candidates = this.getViableCandidates().filter(op => this.canImprove(op));
    if (candidates.length === 0) {
      const productive = this.operations.filter(op => !this.isDetectionOp(op.id));
      const op = productive[Math.floor(Math.random() * productive.length)] || this.operations[0];
      console.log(`[ToolRouter] 无历史/全失败，强制探索: ${op.name}`);
      return { op, mode: 'explore' };
    }
    const op = candidates[Math.floor(Math.random() * candidates.length)];
    console.log(`[ToolRouter] 无历史/全失败，强制探索: ${op.name}`);
    return { op, mode: 'explore' };
  }

  findAlternativeBest(successRates) {
    const improvable = this.getViableCandidates()
      .filter(op => {
        if (this.isDetectionOp(op.id)) return false;
        const rate = successRates[op.id];
        return rate && (rate.success / rate.total) > 0 && this.canImprove(op);
      })
      .sort((a, b) => {
        const rateA = successRates[a.id].success / successRates[a.id].total;
        const rateB = successRates[b.id].success / successRates[b.id].total;
        return rateB - rateA;
      });

    if (improvable.length > 0) {
      const nextBest = improvable[0];
      const rate = successRates[nextBest.id].success / successRates[nextBest.id].total;
      console.log(`[ToolRouter] 利用模式: ${nextBest.name} (成功率: ${(rate * 100).toFixed(0)}%) [最佳操作无可改善空间，降级]`);
      return { op: nextBest, mode: 'exploit' };
    }

    const candidates = this.getViableCandidates();
    if (candidates.length === 0) {
      candidates.push(this.operations[Math.floor(Math.random() * this.operations.length)]);
    }
    const op = candidates[Math.floor(Math.random() * candidates.length)];
    console.log(`[ToolRouter] 全部操作无可改善，强制探索: ${op.name}`);
    return { op, mode: 'explore' };
  }

  updateEpsilon(improved) {
    if (improved) {
      this.history.streak.success++;
      this.history.streak.fail = 0;
      if (this.history.streak.success >= CONFIG.streak.successThreshold) {
        this.history.epsilon = Math.max(
          this.getEpsilonMin(),
          this.history.epsilon - CONFIG.epsilon.decayStep
        );
        this.history.streak.success = 0;
        console.log(`[ToolRouter] 连续成功，ε 降低到 ${(this.history.epsilon * 100).toFixed(0)}%`);
      }
    } else {
      this.history.streak.fail++;
      this.history.streak.success = 0;
      if (this.history.streak.fail >= CONFIG.streak.failThreshold) {
        this.history.epsilon = Math.min(
          CONFIG.epsilon.max,
          this.history.epsilon + CONFIG.epsilon.growthStep
        );
        this.history.streak.fail = 0;
        console.log(`[ToolRouter] 连续失败，ε 升高到 ${(this.history.epsilon * 100).toFixed(0)}%`);
      }
    }
  }
}
