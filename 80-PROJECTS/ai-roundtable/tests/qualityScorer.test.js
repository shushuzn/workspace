import { describe, it, mock } from 'node:test';
import assert from 'node:assert';
import { QualityScorer } from '../shared/qualityScorer.js';

describe('QualityScorer', () => {
  it('returns neutral 0.5 fluidity on first round', () => {
    const scorer = new QualityScorer();
    const result = scorer.scoreRound(
      [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]],
      0,
      [0.1, 0.1, 0.1]
    );
    assert.equal(result.fluidity, 0.5);
  });

  it('computes fluidity from per-persona drift on second round', () => {
    const scorer = new QualityScorer();
    scorer.scoreRound([[0.1, 0.2], [0.3, 0.4]], 0, [0.05, 0.05]);
    const r2 = scorer.scoreRound([[0.15, 0.25], [0.35, 0.45]], 0.08, [0.1, 0.1]);
    assert.ok(r2.fluidity > 0);
  });

  it('passes deltaS through as jump unchanged', () => {
    const scorer = new QualityScorer();
    const r = scorer.scoreRound([[0.1, 0.2]], 0.42, [0.1]);
    assert.equal(r.jump, 0.42);
  });

  it('returns quality score in 0-100 range', () => {
    const scorer = new QualityScorer();
    const r = scorer.scoreRound([[0.1, 0.2], [0.3, 0.4]], 0.05, [0.1, 0.1]);
    assert.ok(r.quality >= 0 && r.quality <= 100);
  });

  it('handles zero contributions without division-by-zero', () => {
    const scorer = new QualityScorer();
    const r = scorer.scoreRound([[0.1, 0.2]], 0, [0]);
    assert.ok(!Number.isNaN(r.balance), 'balance should not be NaN');
    assert.ok(r.balance >= 0 && r.balance <= 1);
  });

  it('balance is higher when contributions are more equal', () => {
    const scorer = new QualityScorer();
    const rEqual = scorer.scoreRound([[0.1, 0.2]], 0, [0.1, 0.1, 0.1, 0.1]);
    const rUnequal = scorer.scoreRound([[0.2, 0.3]], 0, [0.5, 0.05, 0.05, 0.05]);
    assert.ok(rEqual.balance > rUnequal.balance, 'equal contributions should score higher balance');
  });

  it('quality formula: fluidity*0.4 + jump*0.3 + balance*0.3', () => {
    const scorer = new QualityScorer();
    scorer.prevPersonaEmbeddings = [[[0.1, 0.2], [0.3, 0.4]]];
    const r = scorer.scoreRound([[0.15, 0.25], [0.35, 0.45]], 0.2, [0.15, 0.15]);
    const expected = r.fluidity * 0.4 + r.jump * 0.3 + r.balance * 0.3;
    assert.ok(Math.abs(r.quality / 100 - expected) < 0.001);
  });
});
