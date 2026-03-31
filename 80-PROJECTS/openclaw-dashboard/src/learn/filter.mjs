/**
 * Filter (Learn Layer)
 * Filters discovered knowledge for credibility/trustworthiness
 */

export class Filter {
  constructor() {
    this.minCredibilityScore = 0.5;
    this.sourceWeights = {
      user_confirmed: 1.0,
      git_history: 0.8,
      successful_execution: 0.9,
      external_api: 0.7,
      heuristic: 0.4,
      guess: 0.1
    };
  }

  /**
   * Filter discoveries for credibility
   */
  filter(discoveries) {
    return discoveries
      .map(d => this.scoreDiscovery(d))
      .filter(d => d.credibility >= this.minCredibilityScore)
      .sort((a, b) => b.credibility - a.credibility);
  }

  /**
   * Score a discovery based on source reliability
   */
  scoreDiscovery(discovery) {
    const sourceWeight = this.sourceWeights[discovery.source] || 0.5;
    const potentialWeight = this.getPotentialWeight(discovery.potential);
    const recencyWeight = this.getRecencyWeight(discovery);

    const credibility = (
      sourceWeight * 0.5 +
      potentialWeight * 0.3 +
      recencyWeight * 0.2
    );

    return {
      ...discovery,
      credibility,
      sourceWeight,
      potentialWeight,
      recencyWeight
    };
  }

  getPotentialWeight(potential) {
    switch (potential) {
      case 'high': return 1.0;
      case 'medium': return 0.6;
      case 'low': return 0.3;
      default: return 0.5;
    }
  }

  getRecencyWeight(discovery) {
    if (!discovery.discoveredAt) return 0.5;

    const ageHours = (Date.now() - discovery.discoveredAt) / (1000 * 60 * 60);

    if (ageHours < 1) return 1.0;      // Less than 1 hour
    if (ageHours < 24) return 0.8;      // Less than 1 day
    if (ageHours < 168) return 0.5;     // Less than 1 week
    return 0.3;                          // Older
  }

  /**
   * Validate if a discovery should be acted upon
   */
  shouldAct(discovery) {
    return (
      discovery.credibility >= this.minCredibilityScore &&
      discovery.potential !== 'low'
    );
  }

  /**
   * Merge duplicate discoveries
   */
  mergeDuplicates(discoveries) {
    const merged = [];
    const byTarget = {};

    for (const d of discoveries) {
      const key = `${d.type}:${d.target}`;
      if (!byTarget[key]) {
        byTarget[key] = { ...d, count: 1 };
        merged.push(byTarget[key]);
      } else {
        byTarget[key].count++;
        byTarget[key].credibility = Math.max(
          byTarget[key].credibility,
          d.credibility
        );
      }
    }

    return merged.map(m => ({
      ...m,
      count: m.count,
      duplicates: m.count > 1
    }));
  }
}
