/**
 * Distiller (Learn Layer)
 * Converts experience into rules, skills, and strategies
 */

import path from 'path';

export class Distiller {
  constructor(workspace, stm, ltm, skillLibrary) {
    this.workspace = workspace;
    this.stm = stm;           // Short-term memory
    this.ltm = ltm;           // Long-term memory
    this.skillLibrary = skillLibrary; // Skill library
  }

  /**
   * Distill recent experience into knowledge
   * @returns {Object} Summary of what was distilled
   */
  async distill(experience) {
    const results = {
      rules: [],
      skills: [],
      insights: []
    };

    // 1. Analyze patterns from experience
    const patterns = this.extractPatterns(experience);

    // 2. Generate rules from successful patterns
    const rules = this.generateRules(patterns);
    results.rules.push(...rules);

    // 3. Extract skills from repeated successful actions
    const skills = this.extractSkills(patterns);
    results.skills.push(...skills);

    // 4. Generate insights from failures
    const insights = this.generateInsights(patterns);
    results.insights.push(...insights);

    // 5. Store in appropriate memory systems
    await this.storeKnowledge(results);

    return results;
  }

  /**
   * Extract patterns from experience
   */
  extractPatterns(experience) {
    const patterns = {
      successful: [],
      failed: [],
      sequences: []
    };

    const records = experience.records || this.stm.getRecentRecords(50);

    // Analyze success patterns
    for (const record of records) {
      if (record.improved) {
        patterns.successful.push({
          opId: record.opId,
          opName: record.opName,
          delta: record.delta,
          mode: record.mode
        });
      } else {
        patterns.failed.push({
          opId: record.opId,
          opName: record.opName,
          delta: record.delta
        });
      }
    }

    // Find common sequences
    if (records.length > 1) {
      for (let i = 0; i < records.length - 1; i++) {
        patterns.sequences.push({
          from: records[i].opId,
          to: records[i + 1].opId,
          improved: records[i + 1].improved
        });
      }
    }

    return patterns;
  }

  /**
   * Generate rules from patterns
   */
  generateRules(patterns) {
    const rules = [];

    // Rule: If X succeeds, follow with Y (sequence rule)
    const sequenceWins = {};
    for (const seq of patterns.sequences) {
      const key = `${seq.from}->${seq.to}`;
      if (!sequenceWins[key]) {
        sequenceWins[key] = { total: 0, improved: 0 };
      }
      sequenceWins[key].total++;
      if (seq.improved) sequenceWins[key].improved++;
    }

    for (const [key, stats] of Object.entries(sequenceWins)) {
      if (stats.total >= 2 && stats.improved / stats.total > 0.6) {
        const [from, to] = key.split('->');
        rules.push({
          type: 'sequence',
          condition: `after(${from})`,
          action: to,
          confidence: stats.improved / stats.total,
          support: stats.total
        });
      }
    }

    // Rule: Context-dependent success
    for (const success of patterns.successful) {
      if (success.mode === 'exploit' && success.delta > 5) {
        rules.push({
          type: 'context',
          condition: `highHealthAndExploitMode`,
          action: success.opId,
          confidence: 0.8,
          insight: `在利用模式下执行 ${success.opName} 效果显著`
        });
      }
    }

    return rules;
  }

  /**
   * Extract skills from repeated patterns
   */
  extractSkills(patterns) {
    const skills = [];

    // Count operation frequency
    const opCount = {};
    for (const success of patterns.successful) {
      opCount[success.opId] = (opCount[success.opId] || 0) + 1;
    }

    // Operations that succeed frequently become skills
    for (const [opId, count] of Object.entries(opCount)) {
      if (count >= 3) {
        const avgDelta = patterns.successful
          .filter(s => s.opId === opId)
          .reduce((sum, s) => sum + s.delta, 0) / count;

        skills.push({
          type: 'skill',
          name: opId,
          category: 'operation',
          description: `熟练掌握 ${opId} 操作`,
          proficiency: Math.min(count / 10, 1), // 0-1 scale
          avgDelta,
          successCount: count,
          prerequisites: this.inferPrerequisites(opId)
        });
      }
    }

    return skills;
  }

  /**
   * Infer prerequisites for an operation
   */
  inferPrerequisites(opId) {
    // Simple heuristic-based prerequisite inference
    const prereqs = {
      'GenDashboardData': ['cleanWorkspace'],
      'CreateMissingReadme': ['findReadmeIssues'],
      'CleanRecordedIssues': ['FindWorkspaceIssues']
    };
    return prereqs[opId] || [];
  }

  /**
   * Generate insights from failures
   */
  generateInsights(patterns) {
    const insights = [];

    // Analyze failure patterns
    const failCount = {};
    for (const fail of patterns.failed) {
      failCount[fail.opId] = (failCount[fail.opId] || 0) + 1;
    }

    for (const [opId, count] of Object.entries(failCount)) {
      if (count >= 2) {
        insights.push({
          type: 'caution',
          target: opId,
          insight: `${opId} 连续失败 ${count} 次，需要在执行前满足更多前置条件`,
          severity: count >= 3 ? 'high' : 'medium'
        });
      }
    }

    // Detect mode-related failures
    const modeFailures = {};
    for (const fail of patterns.failed) {
      const key = `${fail.opId}_${fail.mode}`;
      modeFailures[key] = (modeFailures[key] || 0) + 1;
    }

    for (const [key, count] of Object.entries(modeFailures)) {
      const [opId, mode] = key.split('_');
      if (count >= 2) {
        insights.push({
          type: 'mode_adaptation',
          target: opId,
          insight: `${opId} 在 ${mode === 'explore' ? '探索' : '利用'} 模式下失败率较高`,
          suggestion: `考虑调整 ${opId} 在 ${mode} 模式下的执行策略`
        });
      }
    }

    return insights;
  }

  /**
   * Store distilled knowledge in appropriate systems
   */
  async storeKnowledge(results) {
    // Store rules in LTM
    for (const rule of results.rules) {
      await this.ltm.store('rules', rule.type, rule, {
        confidence: rule.confidence,
        support: rule.support
      });
    }

    // Register skills in Skill Library
    for (const skill of results.skills) {
      const existing = this.skillLibrary.getAll().find(
        s => s.name === skill.name && s.category === skill.category
      );
      if (!existing) {
        this.skillLibrary.register(skill);
      } else {
        // Update existing skill
        this.skillLibrary.update(existing.id, {
          proficiency: Math.max(existing.proficiency || 0, skill.proficiency),
          successCount: (existing.successCount || 0) + skill.successCount
        });
      }
    }

    // Store insights in LTM
    for (const insight of results.insights) {
      await this.ltm.store('insights', insight.type, insight, {
        severity: insight.severity
      });
    }
  }

  /**
   * Generate summary report of distilled knowledge
   */
  generateReport() {
    return {
      timestamp: Date.now(),
      rulesCount: this.stm.history.records.length,
      skillsCount: this.skillLibrary.getStats().totalSkills,
      topSkills: this.skillLibrary.getMostUsed(5).map(s => ({
        name: s.name,
        usageCount: s.usageCount,
        proficiency: s.proficiency
      })),
      memoryStats: this.ltm.getStats()
    };
  }
}
