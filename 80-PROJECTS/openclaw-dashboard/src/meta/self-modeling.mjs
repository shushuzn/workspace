/**
 * SelfModeling (MetaLoop Layer)
 * Estimates own capability boundaries
 */

import path from 'path';
import { MetaCognizer } from '../core/meta-cognizer.mjs';

export class SelfModeling {
  constructor(workspace, stm, ltm) {
    this.workspace = workspace;
    this.stm = stm;
    this.ltm = ltm;
    this.metaCognizer = new MetaCognizer(workspace, stm, ltm);
    this.modelFile = path.join(workspace, '.omc', 'self-model.json');
  }

  /**
   * Build a model of own capabilities
   */
  async buildModel() {
    const boundary = this.metaCognizer.getCapabilityBoundary();
    const gaps = await this.metaCognizer.analyze();

    const model = {
      version: '1.0.0',
      builtAt: Date.now(),
      capabilities: {
        strong: boundary.strong,
        moderate: boundary.moderate,
        weak: boundary.weak
      },
      gaps: gaps.map(g => ({
        type: g.type,
        target: g.target,
        priority: g.priority
      })),
      confidence: this.calculateConfidence(boundary, gaps),
      recommendations: this.generateRecommendations(boundary, gaps)
    };

    return model;
  }

  calculateConfidence(boundary, gaps) {
    let confidence = 0.5;

    // More data = higher confidence
    const totalOps = boundary.strong.length + boundary.moderate.length + boundary.weak.length;
    if (totalOps >= 5) confidence += 0.2;
    else if (totalOps >= 3) confidence += 0.1;

    // Fewer high-priority gaps = higher confidence
    const highPriorityGaps = gaps.filter(g => g.priority === 'high').length;
    if (highPriorityGaps === 0) confidence += 0.2;
    else if (highPriorityGaps <= 2) confidence += 0.1;

    return Math.min(confidence, 0.95);
  }

  generateRecommendations(boundary, gaps) {
    const recommendations = [];
    const totalOps = boundary.strong.length + boundary.moderate.length + boundary.weak.length;

    // If too many weak capabilities
    if (boundary.weak.length > 3) {
      recommendations.push({
        type: 'learning_focus',
        priority: 'high',
        recommendation: '当前有较多薄弱能力，建议优先提升中等能力达到强项'
      });
    }

    // If high-priority gaps exist
    const highGaps = gaps.filter(g => g.priority === 'high');
    if (highGaps.length > 0) {
      recommendations.push({
        type: 'gap_remediation',
        priority: 'critical',
        recommendation: `优先解决 ${highGaps.length} 个高优先级能力缺口`
      });
    }

    // If no strong capabilities
    if (boundary.strong.length === 0 && totalOps >= 3) {
      recommendations.push({
        type: 'quick_win',
        priority: 'high',
        recommendation: '建议选择一个操作专注提升，快速建立强项'
      });
    }

    return recommendations;
  }

  /**
   * Get capability estimate for a specific task type
   */
  estimateCapability(taskType) {
    const boundary = this.metaCognizer.getCapabilityBoundary();

    const capabilityMap = {
      'detection': boundary.strong.filter(s => s.name.includes('Check')),
      'creation': boundary.strong.filter(s => s.name.includes('Create')),
      'cleanup': boundary.strong.filter(s => s.name.includes('Clean')),
      'sync': boundary.strong.filter(s => s.name.includes('Sync'))
    };

    const relevant = capabilityMap[taskType] || [];

    if (relevant.length > 0) {
      return {
        capable: true,
        confidence: 'high',
        relevantSkills: relevant
      };
    }

    return {
      capable: boundary.moderate.length > 0,
      confidence: 'medium',
      relevantSkills: []
    };
  }

  /**
   * Check if a task is within current capabilities
   */
  canHandle(task) {
    const estimate = this.estimateCapability(task.type || 'general');

    return {
      canHandle: estimate.capable,
      confidence: estimate.confidence,
      suggestion: estimate.capable
        ? 'Proceed with current capabilities'
        : 'Consider learning phase before attempting'
    };
  }
}
