/**
 * Hypothesis (Evolution Layer)
 * Generates improvement hypotheses based on meta-cognition analysis
 */

import { MetaCognizer } from '../core/meta-cognizer.mjs';

export class Hypothesis {
  constructor(workspace, stm, ltm) {
    this.workspace = workspace;
    this.stm = stm;
    this.ltm = ltm;
    this.metaCognizer = new MetaCognizer(workspace, stm, ltm);
  }

  /**
   * Generate hypotheses based on capability gaps
   * Gracefully degrades: if analyze() fails, returns empty array
   */
  async generate() {
    let gaps = [];
    try {
      gaps = await this.metaCognizer.analyze();
    } catch (e) {
      console.log(`[Hypothesis] 元认知分析失败，跳过假设生成: ${e.message}`);
      return [];
    }

    const hypotheses = [];

    for (const gap of gaps) {
      const hypothesis = this.createHypothesis(gap);
      if (hypothesis) {
        hypotheses.push(hypothesis);
      }
    }

    // Add general improvement hypotheses
    hypotheses.push(...this.generateGeneralHypotheses());

    // Sort by expected impact and feasibility
    hypotheses.sort((a, b) => (b.expectedImpact * b.feasibility) - (a.expectedImpact * a.feasibility));

    return hypotheses;
  }

  /**
   * Create a hypothesis from a capability gap
   */
  createHypothesis(gap) {
    switch (gap.type) {
      case 'underperforming':
        return {
          id: this.generateId(),
          type: 'optimization',
          target: gap.target,
          targetName: gap.name,
          problem: gap.metric,
          hypothesis: `如果改进 ${gap.name} 的前置条件或执行策略，成功率应提高`,
          expectedImpact: 0.3,
          feasibility: 0.7,
          experiments: this.designExperiments(gap)
        };

      case 'capability_gap':
        return {
          id: this.generateId(),
          type: 'learning',
          target: gap.target,
          targetName: gap.name,
          problem: '从未成功过',
          hypothesis: `通过练习和优化执行流程，${gap.name} 可以达到可用状态`,
          expectedImpact: 0.5,
          feasibility: 0.5,
          experiments: this.designExperiments(gap)
        };

      case 'failure_pattern':
        return {
          id: this.generateId(),
          type: 'strategy_change',
          target: gap.target,
          targetName: gap.name,
          problem: gap.metric,
          hypothesis: `连续失败表明当前策略不适用，需要改变执行上下文或前置条件`,
          expectedImpact: 0.4,
          feasibility: 0.6,
          experiments: this.designExperiments(gap)
        };

      case 'stale_knowledge':
        return {
          id: this.generateId(),
          type: 'reinvention',
          target: gap.target,
          targetName: gap.name,
          problem: gap.metric,
          hypothesis: `${gap.name} 可能已达到局部最优，需要突破性改变而非渐进优化`,
          expectedImpact: 0.6,
          feasibility: 0.4,
          experiments: this.designExperiments(gap)
        };

      default:
        return null;
    }
  }

  /**
   * Design experiments to test a hypothesis
   */
  designExperiments(gap) {
    const experiments = [];

    // Experiment 1: Change execution order
    experiments.push({
      id: this.generateId(),
      name: `改变执行顺序`,
      description: '在其他操作之后执行，增加成功概率',
      predictedOutcome: '成功率提升 10-20%'
    });

    // Experiment 2: Add preconditions
    experiments.push({
      id: this.generateId(),
      name: `增加前置检查`,
      description: '在执行前检查必要的环境条件',
      predictedOutcome: '避免无效执行'
    });

    // Experiment 3: Modify parameters
    experiments.push({
      id: this.generateId(),
      name: `调整参数`,
      description: '修改操作的默认参数或阈值',
      predictedOutcome: '可能找到更优配置'
    });

    return experiments;
  }

  /**
   * Generate general improvement hypotheses
   */
  generateGeneralHypotheses() {
    const hypotheses = [];
    const recentRecords = this.stm.getRecentRecords(20);

    // Hypothesis: Diversity helps
    const uniqueOps = new Set(recentRecords.map(r => r.opId));
    if (uniqueOps.size < 5) {
      hypotheses.push({
        id: this.generateId(),
        type: 'diversity',
        problem: '操作多样性不足',
        hypothesis: '增加探索率，尝试更多不同操作可以发现新的优化机会',
        expectedImpact: 0.3,
        feasibility: 0.8,
        experiments: []
      });
    }

    // Hypothesis: Health affects success
    const healthTrend = this.calculateHealthTrend(recentRecords);
    if (healthTrend < 0) {
      hypotheses.push({
        id: this.generateId(),
        type: 'health_recovery',
        problem: '健康度呈下降趋势',
        hypothesis: '优先执行恢复性操作（如清理、整理）可以改善整体表现',
        expectedImpact: 0.4,
        feasibility: 0.7,
        experiments: []
      });
    }

    return hypotheses;
  }

  calculateHealthTrend(records) {
    if (records.length < 5) return 0;

    const deltas = records.map(r => r.delta);
    const recent = deltas.slice(-5);
    const older = deltas.slice(-10, -5);

    const recentAvg = recent.reduce((a, b) => a + b, 0) / recent.length;
    const olderAvg = older.length > 0 ? older.reduce((a, b) => a + b, 0) / older.length : recentAvg;

    return recentAvg - olderAvg;
  }

  generateId() {
    return `hyp_${Date.now().toString(36)}_${Math.random().toString(36).substring(2, 6)}`;
  }
}
