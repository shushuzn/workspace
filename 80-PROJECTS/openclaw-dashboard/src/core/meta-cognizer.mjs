/**
 * MetaCognizer (Core Layer)
 * Analyzes capability boundaries and identifies knowledge gaps
 * "我哪里不会？我该学什么？"
 */

import fs from 'fs';
import path from 'path';

export class MetaCognizer {
  constructor(workspace, stm, ltm = null) {
    this.workspace = workspace;
    this.stm = stm; // Short-term memory
    this.ltm = ltm; // Long-term memory (optional)
    this.capabilityFile = path.join(workspace, '.omc', 'capabilities.json');
  }

  /**
   * Analyze current capabilities and identify gaps
   * @returns {Promise<Array>} List of identified gaps with priority
   */
  async analyze() {
    const gaps = [];

    // Analyze success rates from STM
    const successRates = this.stm.getSuccessRates();
    const recentRecords = this.stm.getRecentRecords(20);

    // 1. Find underperforming operations
    const underperforming = this.findUnderperformingOps(successRates);
    gaps.push(...underperforming);

    // 2. Find capability gaps (operations never tried or rarely successful)
    const capabilityGaps = this.findCapabilityGaps(successRates);
    gaps.push(...capabilityGaps);

    // 3. Detect recurring failure patterns
    const failurePatterns = this.detectFailurePatterns(recentRecords);
    gaps.push(...failurePatterns);

    // 4. Check for stale knowledge (operations not improving over time)
    const staleKnowledge = this.detectStaleKnowledge(recentRecords);
    gaps.push(...staleKnowledge);

    return this.prioritizeGaps(gaps);
  }

  findUnderperformingOps(successRates) {
    const gaps = [];
    const threshold = 0.3; // 30% success rate

    for (const [opId, stats] of Object.entries(successRates)) {
      if (stats.total >= 3) {
        const rate = stats.success / stats.total;
        if (rate < threshold) {
          gaps.push({
            type: 'underperforming',
            target: opId,
            name: stats.name,
            priority: 'high',
            metric: `成功率仅 ${(rate * 100).toFixed(0)}%`,
            suggestion: `需要优化 ${stats.name} 的执行策略或前置条件`
          });
        }
      }
    }

    return gaps;
  }

findCapabilityGaps(successRates) {    const gaps = [];    for (const [opId, stats] of Object.entries(successRates)) {      if (stats.total >= 3) {        const rate = stats.success / stats.total;        const recent = this.stm.getRecentRecords(5).filter(r => r.opId === opId);        const hasGenuineFailure = recent.some(r => !r.improved && !r.noOp && !r.blocked);        if (rate < 0.3 && hasGenuineFailure) {          gaps.push({            type: 'capability_gap',            target: opId,            name: stats.name,            priority: 'medium',            metric: `成功率仅 $((rate * 100).toFixed(0))% ($stats.success/$stats.total)`,            suggestion: `需要优化 ${stats.name} 的执行策略或前置条件`          });        }      }    }    return gaps;  }

  detectFailurePatterns(records) {
    const gaps = [];
    if (records.length < 5) return gaps;

    // Check for consecutive failures (must be genuine failures, not "workspace already clean" no-ops)
    let consecutiveFails = 0;
    let failOps = [];
    let failOpIds = [];

    for (const record of records.slice().reverse()) {
      // noOp = workspace already clean, NOT a failure
      if (!record.improved && !record.noOp) {
        consecutiveFails++;
        failOps.push(record.opName);
        failOpIds.push(record.opId);
      } else {
        // noOp or improved = break the fail streak
        break;
      }
    }

    if (consecutiveFails >= 3) {
      gaps.push({
        type: 'failure_pattern',
        target: failOpIds[0],  // Use opId for matching
        name: failOps.slice(0, 3).join(', '),
        priority: 'high',
        metric: `连续失败 ${consecutiveFails} 次`,
        suggestion: '检测到连续失败模式，需要暂停并重新评估策略'
      });
    }

    return gaps;
  }

  detectStaleKnowledge(records) {
    const gaps = [];
    if (records.length < 10) return gaps;

    // Group by operation and check if any are consistently not improving
    const opGroups = {};
    for (const record of records) {
      if (!opGroups[record.opId]) {
        opGroups[record.opId] = [];
      }
      opGroups[record.opId].push(record);
    }

    for (const [opId, opRecords] of Object.entries(opGroups)) {
      if (opRecords.length >= 5) {
        const recent = opRecords.slice(-5);
        const hasImprovement = recent.some(r => r.delta > 0);
        const avgDelta = recent.reduce((sum, r) => sum + r.delta, 0) / recent.length;

        // Only flag as stale if genuinely underperforming, not at ceiling
        const recentScores = recent.map(r => r.afterScore);
        const atCeiling = recentScores.every(s => s >= 100);
        if (!hasImprovement && avgDelta <= 0 && !atCeiling) {
          gaps.push({
            type: 'stale_knowledge',
            target: opId,
            name: opRecords[0].opName,
            priority: 'medium',
            metric: '最近5次执行无改善',
            suggestion: `${opRecords[0].opName} 可能已达到局部最优，需要新策略`
          });
        }
      }
    }

    return gaps;
  }

  prioritizeGaps(gaps) {
    // Sort by priority: high > medium > low
    const priorityOrder = { high: 0, medium: 1, low: 2 };
    return gaps.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);
  }

  /**
   * Get estimated capability boundary
   */
  getCapabilityBoundary() {
    const successRates = this.stm.getSuccessRates();
    const boundary = {
      strong: [],    // > 70% success
      moderate: [],  // 30-70% success
      weak: []       // < 30% success
    };

    for (const [opId, stats] of Object.entries(successRates)) {
      if (stats.total >= 2) {
        const rate = stats.success / stats.total;
        const entry = { id: opId, name: stats.name, rate, total: stats.total };

        if (rate > 0.7) boundary.strong.push(entry);
        else if (rate >= 0.3) boundary.moderate.push(entry);
        else boundary.weak.push(entry);
      }
    }

    return boundary;
  }
}
