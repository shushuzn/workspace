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

  findCapabilityGaps(successRates) {
    const gaps = [];
    const allOps = this.stm.history.records.length > 0
      ? [...new Set(this.stm.history.records.map(r => r.opId))]
      : [];

    // If an operation type has never been tried, it's a capability gap
    // This would be enhanced with LTM integration
    for (const opId of allOps) {
      const stats = successRates[opId];
      if (stats && stats.total === 1 && stats.success === 0) {
        gaps.push({
          type: 'capability_gap',
          target: opId,
          name: stats.name,
          priority: 'medium',
          metric: '仅尝试过1次且失败',
          suggestion: `需要学习/练习 ${stats.name} 操作`
        });
      }
    }

    return gaps;
  }

  detectFailurePatterns(records) {
    const gaps = [];
    if (records.length < 5) return gaps;

    // Check for consecutive failures
    let consecutiveFails = 0;
    let failOps = [];

    for (const record of records.slice().reverse()) {
      if (!record.improved) {
        consecutiveFails++;
        failOps.push(record.opName);
      } else {
        break;
      }
    }

    if (consecutiveFails >= 3) {
      gaps.push({
        type: 'failure_pattern',
        target: failOps[0],
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

        if (!hasImprovement && avgDelta <= 0) {
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
