/**
 * Loop Engine
 * Main orchestration for the self-evolving optimization loop
 */

import path from 'path';
import { CONFIG } from '../config/default.mjs';
import { HealthScorer } from './health-scorer.mjs';
import { EpsilonGreedy } from './epsilon-greedy.mjs';
import { HistoryManager } from '../history/history-manager.mjs';
import { getAllOperations } from '../operations/index.mjs';

export class LoopEngine {
  constructor(workspace) {
    this.workspace = workspace;
    this.historyFile = path.join(workspace, '.omc', 'loop-history.json');
    this.historyManager = new HistoryManager(this.historyFile);
    this.healthScorer = new HealthScorer(workspace);
    this.operations = getAllOperations(workspace);
    this.selector = new EpsilonGreedy(workspace, this.operations, this.historyManager.history);
  }

  async runIteration() {
    const beforeScore = this.healthScorer.calculate();

    console.log('\n' + '='.repeat(50));
    console.log(`[Loop] 迭代开始 | 健康度: ${beforeScore} | ε: ${(this.historyManager.history.epsilon * 100).toFixed(0)}%`);

    const { op, mode } = this.selector.select();

    let result;
    try {
      result = await op.execute();
      console.log(`[Result]`, result);
    } catch (e) {
      console.error(`[Error] 操作失败: ${e.message}`);
      result = { error: e.message };
    }

    const afterScore = this.healthScorer.calculate();
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

    this.historyManager.addRecord(record);
    this.selector.updateEpsilon(improved);
    this.historyManager.save();

    console.log(`[Loop] 健康度: ${beforeScore} → ${afterScore} (${delta > 0 ? '+' : ''}${delta}) | ${noOp ? '无操作' : improved ? '✓' : '✗'}`);
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
    const score = this.healthScorer.calculate();
    const rates = this.historyManager.getSuccessRates();

    const sorted = Object.values(rates)
      .filter(r => r.total >= 1)
      .sort((a, b) => (b.success / b.total) - (a.success / a.total))
      .slice(0, 5);

    return {
      score,
      epsilon: this.historyManager.history.epsilon,
      records: this.historyManager.history.records.length,
      streak: this.historyManager.history.streak,
      topOperations: sorted
    };
  }
}
