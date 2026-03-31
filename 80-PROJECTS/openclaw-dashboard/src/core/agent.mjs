/**
 * Agent (Core Layer)
 * Main orchestration for the self-evolving optimization loop
 * Refactored from: loop-engine.mjs
 */

import path from 'path';
import { CONFIG } from '../config/default.mjs';
import { WorkingMemory } from './working-memory.mjs';
import { ToolRouter } from './tool-router.mjs';
import { STM } from '../memory/stm.mjs';
import { LTM } from '../memory/ltm.mjs';
import { getAllOperations } from '../operations/index.mjs';
import { Safety } from '../governance/safety.mjs';
import { CandidatePool } from '../learn/candidate-pool.mjs';
import { Discoverer } from '../learn/discoverer.mjs';
import { Distiller } from '../learn/distiller.mjs';
import { Curriculum } from '../learn/curriculum.mjs';
import { SkillLibrary } from '../memory/skill-library.mjs';
import { Hypothesis } from '../evolution/hypothesis.mjs';
import { Sandbox } from '../evolution/sandbox.mjs';

export class Agent {
  constructor(workspace) {
    this.workspace = workspace;
    this.historyFile = path.join(workspace, '.omc', 'loop-history.json');

    // Core components
    this.stm = new STM(this.historyFile);
    this.workingMemory = new WorkingMemory(workspace);
    this.operations = getAllOperations(workspace);
    this.toolRouter = new ToolRouter(workspace, this.operations, this.stm.history);
    this.safety = new Safety(workspace);

    // Learn components - connected to MetaCognizer loop
    this.candidatePool = new CandidatePool(workspace);
    this.curriculum = new Curriculum();

    // Memory and Evolution components
    this.ltm = new LTM(workspace);
    this.hypothesis = new Hypothesis(workspace, this.stm, this.ltm);
    this.sandbox = new Sandbox(workspace);

    // Wire candidate pool into tool router
    this.toolRouter.setCandidatePool(this.candidatePool);

    // Discoverer for finding new knowledge
    this.discoverer = new Discoverer(workspace, this.ltm, this.skillLibrary);

    // Learn components - SkillLibrary + Distiller pipeline
    this.skillLibrary = new SkillLibrary(workspace);
    this.distiller = new Distiller(workspace, this.stm, this.ltm, this.skillLibrary);

    // Meta-cognizer will be injected
    this.metaCognizer = null;
  }

  setMetaCognizer(metaCognizer) {
    this.metaCognizer = metaCognizer;
  }

  async runIteration() {
    const beforeScore = this.workingMemory.calculate();

    console.log('\n' + '='.repeat(50));
    console.log(`[Agent] 迭代开始 | 健康度: ${beforeScore} | ε: ${(this.stm.history.epsilon * 100).toFixed(0)}%`);

    // Meta-cognition: analyze and update ToolRouter with gaps
    let gaps = [];
    let hypotheses = [];
    if (this.metaCognizer) {
      gaps = await this.metaCognizer.analyze();
      if (gaps.length > 0) {
        console.log(`[Agent] 元认知识别 ${gaps.length} 个能力缺口`);
        // Feed gaps to ToolRouter to bias operation selection
        this.toolRouter.setGaps(gaps);
        // Add gaps to candidate pool for learning
        this.learnFromGaps(gaps);
        // Generate hypotheses from gaps
        hypotheses = await this.hypothesis.generate();
        if (hypotheses.length > 0) {
          console.log(`[Agent] 生成 ${hypotheses.length} 个改进假设`);
        }
      }
    }

    // Query LTM for relevant knowledge to bias decisions
    const ltmKnowledge = await this.queryLTM();
    if (ltmKnowledge && ltmKnowledge.successfulOps) {
      this.toolRouter.setLTMKnowledge(ltmKnowledge.successfulOps);
    }

    // Discover new knowledge and feed to candidate pool
    const discoveries = await this.discoverer.discover();
    if (discoveries.length > 0) {
      this.learnFromDiscoveries(discoveries);
    }

    // Select operation via ToolRouter (now gap-informed)
    const { op, mode } = this.toolRouter.select();

    // Safety check before execution
    const safetyResult = await this.safety.check(op);
    if (!safetyResult.approved) {
      console.log(`[Agent] 操作被安全策略阻止: ${safetyResult.reason}`);
      const record = {
        opId: op.id,
        opName: op.name,
        mode: 'blocked',
        beforeScore,
        afterScore: beforeScore,
        delta: 0,
        improved: false,
        blocked: true,
        blockReason: safetyResult.reason,
        timestamp: Date.now()
      };
      this.stm.addRecord(record);
      this.stm.save();
      return record;
    }

    let result;
    try {
      result = await op.execute();
      console.log(`[Result]`, result);
    } catch (e) {
      console.error(`[Error] 操作失败: ${e.message}`);
      result = { error: e.message };
    }

    const afterScore = this.workingMemory.calculate();
    const delta = afterScore - beforeScore;

    const { improved, noOp } = this.evaluateResult(op, result, delta, beforeScore);

    const record = {
      opId: op.id,
      opName: op.name,
      mode,
      beforeScore,
      afterScore,
      delta,
      improved,
      noOp,
      timestamp: Date.now()
    };

    this.stm.addRecord(record);
    this.toolRouter.updateEpsilon(improved);
    this.stm.save();

    // Update candidate pool - mark matching candidate as evaluated
    this.candidatePool.getByType('capability_gap').forEach(c => {
      if (c.target === op.id || (c.name && op.name && op.name.includes(c.name.substring(0, 6)))) {
        if (improved && !noOp) {
          this.candidatePool.approve(c.id, { delta, afterScore });
        } else if (!improved && !noOp && record.attempts >= 2) {
          this.candidatePool.reject(c.id, `连续失败，已尝试 ${record.attempts} 次`);
        }
      }
    });

    // Distill experience into rules, skills, and insights via full Distiller pipeline
    const distResult = await this.distiller.distill({ records: this.stm.getRecentRecords(50) });
    if (distResult.rules.length > 0 || distResult.skills.length > 0 || distResult.insights.length > 0) {
      console.log(`[Agent] 蒸馏: ${distResult.rules.length} 条规则, ${distResult.skills.length} 个技能, ${distResult.insights.length} 条洞察`);
    }

    console.log(`[Agent] 健康度: ${beforeScore} → ${afterScore} (${delta > 0 ? '+' : ''}${delta}) | ${noOp ? '无操作' : improved ? '✓' : '✗'}`);
    console.log('='.repeat(50));

    return record;
  }

  evaluateResult(op, result, delta, beforeScore) {
    // Delta must be positive (or at ceiling with real output) AND health above minimum threshold
    const atCeiling = beforeScore >= 100;
    let improved = (delta > 0 || atCeiling) && beforeScore >= 50;
    let noOp = false;

    if (!improved && result) {
      if (op.type === 'detection') {
        const found = (result.missing > 0) || (result.changed > 0) ||
                      (result.found > 0) || (result.checked > 0) ||
                      (result.sizeKB > 0) || (result.lines > 0) ||
                      (result.total > 0) || (result.fixed > 0) ||
                      (result.updated > 0) || (result.created > 0) ||
                      (result.cleaned > 0);
        if (!found) {
          noOp = true;
        } else {
          improved = beforeScore >= 50;
        }
      } else {
        const hasOutput = (result.created > 0) || (result.cleaned > 0) ||
                          (result.deleted > 0) || (result.committed > 0) ||
                          (result.fixed > 0) || (result.updated > 0) ||
                          (result.synced > 0);
        if (!hasOutput) {
          noOp = true;
        } else {
          improved = beforeScore >= 50;
        }
      }
    }

    return { improved, noOp };
  }

  /**
   * Add gaps from MetaCognizer to CandidatePool for learning
   */
  learnFromGaps(gaps) {
    for (const gap of gaps) {
      // Check if already in pool
      const existing = this.candidatePool.getByType('capability_gap')
        .find(c => c.target === gap.target && c.status !== 'rejected');

      if (!existing) {
        this.candidatePool.add({
          type: 'capability_gap',
          source: 'meta_cognizer',
          target: gap.target,
          name: gap.name,
          priority: gap.priority,
          reason: gap.suggestion || `Gap: ${gap.metric}`,
          estimatedImpact: gap.priority === 'high' ? 30 : gap.priority === 'medium' ? 20 : 10
        });
      }
    }

    // Log pool stats
    const stats = this.candidatePool.getStats();
    if (stats.pending > 0) {
      console.log(`[Agent] 候选池: ${stats.pending} 个待学习项`);
    }
  }

  /**
   * Add discoveries from Discoverer to CandidatePool
   */
  learnFromDiscoveries(discoveries) {
    let added = 0;
    for (const d of discoveries) {
      // Avoid duplicates by checking existing pool
      const existing = this.candidatePool.getByType(d.type)
        .find(c => c.target === d.target && c.status !== 'rejected');
      if (existing) continue;

      const priority = d.potential === 'high' ? 'high' : d.potential === 'medium' ? 'medium' : 'low';
      this.candidatePool.add({
        type: d.type,
        source: 'discoverer',
        target: d.target,
        name: d.finding || d.finding,
        priority,
        reason: d.finding,
        estimatedImpact: priority === 'high' ? 25 : priority === 'medium' ? 15 : 5
      });
      added++;
    }
    if (added > 0) {
      console.log(`[Agent] 发现 ${added} 个新知识加入候选池`);
    }
  }

  /**
   * Distill successful operation result to LTM for future reference
   */
  async distillToLTM(op, result, record) {
    const knowledge = {
      opId: op.id,
      opName: op.name,
      type: op.type,
      delta: record.delta,
      mode: record.mode,
      timestamp: record.timestamp
    };

    try {
      await this.ltm.store('operation', op.id, knowledge, {
        success: record.improved,
        delta: record.delta
      });
    } catch (e) {
      // LTM storage failure is non-fatal
      console.log(`[LTM] 存储失败: ${e.message}`);
    }
  }

  /**
   * Query LTM for relevant knowledge to bias decisions
   */
  async queryLTM() {
    const stats = this.ltm.getStats();
    if (stats.totalEntries === 0) {
      return null; // No knowledge yet
    }

    // Search for recent successful operations
    try {
      const recent = await this.ltm.searchByDomain('operation');
      if (recent.length > 0) {
        // Return top successful operations for bias
        const successful = recent
          .filter(e => e.metadata?.success === true)
          .sort((a, b) => (b.metadata?.delta || 0) - (a.metadata?.delta || 0))
          .slice(0, 5);
        return { successfulOps: successful };
      }
    } catch (e) {
      // LTM query failure is non-fatal
    }
    return null;
  }

  getStatus() {
    const score = this.workingMemory.calculate();
    const rates = this.stm.getSuccessRates();

    const sorted = Object.values(rates)
      .filter(r => r.total >= 1)
      .sort((a, b) => (b.success / b.total) - (a.success / b.total))
      .slice(0, 5);

    return {
      score,
      epsilon: this.stm.history.epsilon,
      records: this.stm.history.records.length,
      streak: this.stm.history.streak,
      topOperations: sorted
    };
  }
}
