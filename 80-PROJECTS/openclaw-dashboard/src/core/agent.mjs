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
import { Curriculum } from '../learn/curriculum.mjs';
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
      timestamp: Date.now()
    };

    this.stm.addRecord(record);
    this.toolRouter.updateEpsilon(improved);
    this.stm.save();

    // Distill successful experience to LTM
    if (improved || result.success) {
      await this.distillToLTM(op, result, record);
    }

    console.log(`[Agent] 健康度: ${beforeScore} → ${afterScore} (${delta > 0 ? '+' : ''}${delta}) | ${noOp ? '无操作' : improved ? '✓' : '✗'}`);
    console.log('='.repeat(50));

    return record;
  }

  evaluateResult(op, result, delta, beforeScore) {
    // Delta must be positive AND absolute health must not be critically low
    let improved = delta > 0 && beforeScore >= 50;
    let noOp = false;

    if (!improved && result) {
      if (op.type === 'detection') {
        const found = (result.missing > 0) || (result.changed > 0) ||
                      (result.ideas > 0) || (result.found > 0) ||
                      (result.committed > 0);
        if (!found) noOp = true;
        else improved = beforeScore >= 50; // Detection only improves if health OK
      } else {
        if ((result.created === 0 && result.message) ||
            (result.cleaned === 0 && result.total > 0)) {
          noOp = true;
        } else {
          improved = (result.created > 0) || (result.cleaned > 0) ||
                     (result.deleted > 0) || (result.found > 0) ||
                     (result.success === true) || (result.committed > 0);
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
