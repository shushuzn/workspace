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
import { getAllOperations } from '../operations/index.mjs';
import { Safety } from '../governance/safety.mjs';

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

    // Meta-cognition: analyze before selecting
    if (this.metaCognizer) {
      const gaps = await this.metaCognizer.analyze();
      if (gaps.length > 0) {
        console.log(`[Agent] 元认知识别 ${gaps.length} 个能力缺口`);
      }
    }

    // Select operation via ToolRouter
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

    const { improved, noOp } = this.evaluateResult(op, result, delta);

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

    console.log(`[Agent] 健康度: ${beforeScore} → ${afterScore} (${delta > 0 ? '+' : ''}${delta}) | ${noOp ? '无操作' : improved ? '✓' : '✗'}`);
    console.log('='.repeat(50));

    return record;
  }

  evaluateResult(op, result, delta) {
    let improved = delta > 0;
    let noOp = false;

    if (!improved && result) {
      if (op.type === 'detection') {
        const found = (result.missing > 0) || (result.changed > 0) ||
                      (result.ideas > 0) || (result.found > 0) ||
                      (result.committed > 0);
        if (!found) noOp = true;
        else improved = true;
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
