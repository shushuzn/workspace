/**
 * Curriculum (Learn Layer)
 * Prioritizes and sequences learning content
 */

export class Curriculum {
  constructor() {
    this.priorityWeights = {
      critical: 1.0,
      high: 0.8,
      medium: 0.5,
      low: 0.2
    };
  }

  /**
   * Prioritize learning items
   */
  prioritize(items) {
    return items
      .map(item => ({
        ...item,
        priorityScore: this.calculatePriority(item)
      }))
      .sort((a, b) => b.priorityScore - a.priorityScore);
  }

  calculatePriority(item) {
    let score = 0;

    // Priority weight
    score += this.priorityWeights[item.priority] || 0.5;

    // Credibility bonus
    if (item.credibility) {
      score += item.credibility * 0.3;
    }

    // Impact potential bonus
    if (item.potential === 'high') {
      score += 0.3;
    }

    // Urgency bonus (if learning has deadline)
    if (item.urgency) {
      const urgencyHours = (item.urgency - Date.now()) / (1000 * 60 * 60);
      if (urgencyHours < 24) {
        score += 0.5;
      } else if (urgencyHours < 168) {
        score += 0.2;
      }
    }

    // Dependency bonus (learn prerequisites first)
    if (item.prerequisites?.length > 0) {
      score -= item.prerequisites.length * 0.1;
    }

    return score;
  }

  /**
   * Create a learning path
   */
  createPath(items, maxItems = 10) {
    const prioritized = this.prioritize(items);
    const path = [];
    const completed = new Set();

    for (const item of prioritized) {
      if (path.length >= maxItems) break;

      // Check prerequisites
      if (item.prerequisites) {
        const prereqsMet = item.prerequisites.every(p => completed.has(p));
        if (!prereqsMet) continue;
      }

      path.push({
        ...item,
        order: path.length + 1,
        estimatedTime: this.estimateTime(item)
      });

      completed.add(item.id || item.name);
    }

    return path;
  }

  estimateTime(item) {
    switch (item.type) {
      case 'capability_gap': return 60;      // 60 minutes
      case 'missing_resource': return 15;       // 15 minutes
      case 'skill_gap': return 120;            // 2 hours
      case 'optimization': return 30;          // 30 minutes
      default: return 30;
    }
  }

  /**
   * Get learning recommendations based on history
   */
  recommendFromHistory(records) {
    const recommendations = [];

    // Recommend learning for underperforming operations
    const failCount = {};
    for (const record of records) {
      if (!record.improved) {
        failCount[record.opId] = (failCount[record.opId] || 0) + 1;
      }
    }

    for (const [opId, fails] of Object.entries(failCount)) {
      if (fails >= 2) {
        recommendations.push({
          type: 'skill_gap',
          target: opId,
          priority: fails >= 3 ? 'high' : 'medium',
          reason: `${opId} 失败 ${fails} 次，需要学习改进`
        });
      }
    }

    return this.prioritize(recommendations);
  }
}
