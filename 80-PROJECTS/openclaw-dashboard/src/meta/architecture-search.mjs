/**
 * ArchitectureSearch (MetaLoop Layer)
 * Suggests module connection adjustments
 */

import path from 'path';

export class ArchitectureSearch {
  constructor(workspace) {
    this.workspace = workspace;
    this.historyFile = path.join(workspace, '.omc', 'architecture-suggestions.json');
  }

  /**
   * Analyze current architecture and suggest improvements
   */
  analyze(agent, operations) {
    const suggestions = [];

    // 1. Analyze feedback loops
    suggestions.push(...this.analyzeFeedbackLoops(agent));

    // 2. Analyze operation distribution
    suggestions.push(...this.analyzeOperationDistribution(agent, operations));

    // 3. Analyze memory efficiency
    suggestions.push(...this.analyzeMemoryEfficiency(agent));

    return suggestions.sort((a, b) => {
      const priorityOrder = { high: 0, medium: 1, low: 2 };
      return priorityOrder[a.priority] - priorityOrder[b.priority];
    });
  }

  analyzeFeedbackLoops(agent) {
    const suggestions = [];
    const history = agent.stm.history;

    // Check for long feedback cycles
    if (history.records.length >= 10) {
      const recent = history.records.slice(-10);
      const improvements = recent.filter(r => r.improved).length;

      if (improvements < 3) {
        suggestions.push({
          id: 'feedback_slow',
          type: 'loop_optimization',
          priority: 'high',
          problem: '最近10次迭代中只有3次改善，反馈循环效率低',
          suggestion: '考虑增加探索率或调整操作选择策略',
          expectedImpact: '可能提升20-30%改善率'
        });
      }
    }

    // Check for stuck states
    if (history.streak.fail >= 5) {
      suggestions.push({
        id: 'feedback_stuck',
        type: 'loop_optimization',
        priority: 'critical',
        problem: '连续失败5次以上，可能陷入局部最优',
        suggestion: '建议大幅增加探索率(ε)或重置历史',
        expectedImpact: '可能打破当前僵局'
      });
    }

    return suggestions;
  }

  analyzeOperationDistribution(agent, operations) {
    const suggestions = [];
    const history = agent.stm.history;

    // Analyze operation usage distribution
    const opUsage = {};
    for (const record of history.records) {
      opUsage[record.opId] = (opUsage[record.opId] || 0) + 1;
    }

    const usageValues = Object.values(opUsage);
    if (usageValues.length > 0) {
      const maxUsage = Math.max(...usageValues);
      const minUsage = Math.min(...usageValues);

      // If one operation dominates
      if (maxUsage > usageValues.reduce((a, b) => a + b, 0) * 0.5) {
        const dominantOp = Object.entries(opUsage).find(([, count]) => count === maxUsage)?.[0];
        suggestions.push({
          id: 'operation_dominance',
          type: 'redistribution',
          priority: 'medium',
          problem: `操作 ${dominantOp} 被过度使用 (${maxUsage} 次)`,
          suggestion: '考虑增加探索多样性，减少单一操作依赖',
          expectedImpact: '可能发现新的优化机会'
        });
      }

      // If some operations never used
      const usedOps = new Set(history.records.map(r => r.opId));
      const unusedOps = operations.filter(op => !usedOps.has(op.id));

      if (unusedOps.length > 0 && unusedOps.length <= 3) {
        suggestions.push({
          id: 'unused_operations',
          type: 'capability_underexplored',
          priority: 'low',
          problem: `${unusedOps.length} 个操作从未被尝试`,
          suggestion: `未使用的操作: ${unusedOps.map(o => o.name).join(', ')}`,
          expectedImpact: '未知，可能发现隐藏的有效操作'
        });
      }
    }

    return suggestions;
  }

  analyzeMemoryEfficiency(agent) {
    const suggestions = [];

    // Check if LTM is being utilized
    if (agent.ltm) {
      const ltmStats = agent.ltm.getStats();
      if (ltmStats.totalEntries === 0) {
        suggestions.push({
          id: 'ltm_unused',
          type: 'memory_optimization',
          priority: 'low',
          problem: '长期记忆未被使用',
          suggestion: '建议在 distill 阶段将学习成果存入 LTM',
          expectedImpact: '可能提升知识保留'
        });
      }
    }

    // Check STM efficiency
    if (agent.stm) {
      const records = agent.stm.history.records;
      if (records.length > 100) {
        // Analyze if old records are still useful
        const recentRecords = records.slice(-50);
        const oldRecords = records.slice(0, -50);

        const recentSuccessRate = recentRecords.filter(r => r.improved).length / recentRecords.length;
        const oldSuccessRate = oldRecords.filter(r => r.improved).length / oldRecords.length;

        if (recentSuccessRate > oldSuccessRate + 0.2) {
          suggestions.push({
            id: 'history_weighting',
            type: 'memory_optimization',
            priority: 'medium',
            problem: '近期记录改善率显著高于历史',
            suggestion: '考虑给近期记录更高权重，或减少历史窗口大小',
            expectedImpact: '可能提升选择准确性'
          });
        }
      }
    }

    return suggestions;
  }

  /**
   * Generate architecture change proposal
   */
  generateProposal(suggestions) {
    const topSuggestion = suggestions[0];

    if (!topSuggestion) {
      return {
        ready: false,
        reason: 'No significant architecture issues found'
      };
    }

    return {
      ready: true,
      topSuggestion,
      allSuggestions: suggestions,
      confidence: suggestions.length > 3 ? 'high' : 'medium'
    };
  }
}
