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
  }

  getEpsilon() {
    return this.history.epsilon;
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
    let bestRate = -1;

    for (const op of candidates) {
      const rate = successRates[op.id];
      const noveltyBonus = this.isNewOp(op.id) ? 0.1 : 0;

      if (rate && rate.total >= 1) {
        const r = rate.success / rate.total + noveltyBonus;
        if (r > bestRate) {
          bestRate = r;
          bestOp = op;
        }
      } else if (this.isNewOp(op.id)) {
        const r = 0.1 + noveltyBonus;
        if (r > bestRate) {
          bestRate = r;
          bestOp = op;
        }
      }
    }

    if (!bestOp || bestRate <= 0) {
      return this.fallbackSelection();
    }

    if (!this.canImprove(bestOp)) {
      return this.findAlternativeBest(successRates);
    }

    console.log(`[ToolRouter] 利用模式: ${bestOp.name} (成功率: ${(bestRate * 100).toFixed(0)}%)`);
    return { op: bestOp, mode: 'exploit' };
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
