# Discussion Quality Scorer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a 0-100 quality score to each discussion round, computed from fluidity + concept-jump + participation-balance.

**Architecture:** New `QualityScorer` class in `shared/qualityScorer.js` — stateless scorer called each round-end from `index.js`. No changes to `conceptJumpTracker.js`. Results added to existing `roundStats`.

**Tech Stack:** Pure JS, no new dependencies. Uses existing `cosineDistance` from `shared/vectorUtils.js`.

---

## Task 1: Create `shared/qualityScorer.js`

**Files:**

- Create: `80-PROJECTS/ai-roundtable/shared/qualityScorer.js`
- Modify: — (no changes to existing files yet)
- Test: `80-PROJECTS/ai-roundtable/tests/qualityScorer.test.js`

### Steps

- [ ] **Step 1: Write failing test**

```js
// tests/qualityScorer.test.js
import { describe, it, mock } from 'node:test';
import assert from 'node:assert';
import { QualityScorer } from '../shared/qualityScorer.js';

describe('QualityScorer', () => {
  it('returns neutral 0.5 fluidity on first round', () => {
    const scorer = new QualityScorer();
    const result = scorer.scoreRound(
      [
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6],
        [0.7, 0.8, 0.9],
      ], // personaEmbeddings for 3 personas
      0,
      [0.1, 0.1, 0.1]
    );
    assert.equal(result.fluidity, 0.5);
  });

  it('computes fluidity from per-persona drift on second round', () => {
    const scorer = new QualityScorer();
    // Round 1
    scorer.scoreRound(
      [
        [0.1, 0.2],
        [0.3, 0.4],
      ],
      0,
      [0.05, 0.05]
    );
    // Round 2 — each persona shifted by 0.1 in cosine distance terms
    const r2 = scorer.scoreRound(
      [
        [0.15, 0.25],
        [0.35, 0.45],
      ],
      0.08,
      [0.1, 0.1]
    );
    assert.ok(r2.fluidity > 0);
  });

  it('passes deltaS through as jump unchanged', () => {
    const scorer = new QualityScorer();
    const r = scorer.scoreRound([[0.1, 0.2]], 0.42, [0.1]);
    assert.equal(r.jump, 0.42);
  });

  it('returns quality score in 0-100 range', () => {
    const scorer = new QualityScorer();
    const r = scorer.scoreRound(
      [
        [0.1, 0.2],
        [0.3, 0.4],
      ],
      0.05,
      [0.1, 0.1]
    );
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
    scorer.scoreRound([[0.1, 0.2]], 0, [0.1, 0.1, 0.1, 0.1]); // equal
    const rUnequal = scorer.scoreRound(
      [[0.2, 0.3]],
      0,
      [0.5, 0.05, 0.05, 0.05]
    ); // unequal
    assert.ok(
      rUnequal.balance < 1,
      'unequal contributions should reduce balance'
    );
  });

  it('quality formula: fluidity*0.4 + jump*0.3 + balance*0.3', () => {
    const scorer = new QualityScorer();
    // Override prev embeddings so fluidity is deterministic
    scorer.prevPersonaEmbeddings = [
      [
        [0.1, 0.2],
        [0.3, 0.4],
      ],
    ];
    const r = scorer.scoreRound(
      [
        [0.15, 0.25],
        [0.35, 0.45],
      ],
      0.2,
      [0.15, 0.15]
    );
    const expected = r.fluidity * 0.4 + r.jump * 0.3 + r.balance * 0.3;
    assert.ok(
      Math.abs(r.quality / 100 - expected) < 0.001,
      `expected ${expected}, got ${r.quality / 100}`
    );
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd 80-PROJECTS/ai-roundtable && node --test tests/qualityScorer.test.js`
Expected: FAIL with "ERR_MODULE_NOT_FOUND" or "Cannot find module"

- [ ] **Step 3: Write minimal implementation**

```js
// shared/qualityScorer.js
import { cosineDistance } from './vectorUtils.js';

export class QualityScorer {
  constructor() {
    this.prevPersonaEmbeddings = [];
  }

  /**
   * @param {number[][]} personaEmbeddings - [personaCount][dim]
   * @param {number} deltaS - deltaS from ConceptJumpTracker
   * @param {number[]} contributions - contributions from ConceptJumpTracker
   * @returns {{ quality: number, fluidity: number, jump: number, balance: number }}
   */
  scoreRound(personaEmbeddings, deltaS, contributions) {
    const ε = 0.001;

    // 人均观点变化 (fluidity)
    let fluidity = 0.5;
    if (this.prevPersonaEmbeddings.length > 0) {
      const prev =
        this.prevPersonaEmbeddings[this.prevPersonaEmbeddings.length - 1];
      fluidity =
        personaEmbeddings.reduce(
          (sum, emb, i) => sum + cosineDistance(emb, prev[i]),
          0
        ) / personaEmbeddings.length;
    }

    // 概念跳跃 (jump)
    const jump = deltaS;

    // 活跃均衡度 (balance)
    const mean =
      contributions.reduce((a, b) => a + b, 0) / contributions.length;
    const std = Math.sqrt(
      contributions.reduce((s, v) => s + (v - mean) ** 2, 0) /
        contributions.length
    );
    const balance = 1 - std / (mean + ε);

    const quality = fluidity * 0.4 + jump * 0.3 + balance * 0.3;

    this.prevPersonaEmbeddings.push(personaEmbeddings);
    return {
      quality: Math.min(100, quality * 100),
      fluidity,
      jump,
      balance,
    };
  }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd 80-PROJECTS/ai-roundtable && node --test tests/qualityScorer.test.js`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd 80-PROJECTS/ai-roundtable
git add shared/qualityScorer.js tests/qualityScorer.test.js
git commit -m "feat: add QualityScorer class for discussion quality scoring"
```

---

## Task 2: Wire QualityScorer into `index.js`

**Files:**

- Modify: `80-PROJECTS/ai-roundtable/index.js:1-20` (imports), `index.js:330-460` (main loop + report)

### Steps

- [ ] **Step 1: Add import and construct scorer**

After line 4 (embedder import), add:

```js
import { QualityScorer } from './shared/qualityScorer.js';
```

After `const tracker = new ConceptJumpTracker(embedder);` (line 368), add:

```js
const scorer = new QualityScorer();
```

- [ ] **Step 2: Call scorer each round-end, store quality in roundStats**

After line 410 (`scheduler.recordDeltaS(deltaS);`), add:

```js
const { quality, fluidity, jump, balance } = scorer.scoreRound(
  tracker.personaEmbeddings[tracker.personaEmbeddings.length - 1],
  deltaS,
  contributions
);
roundStats[round].quality = quality;
```

- [ ] **Step 3: Update printAnnealingReport to show quality column**

In `printAnnealingReport()`, find the table header:

```
'  轮次 | 温度  | ΔS   | 状态'
```

Change to:

```
'  轮次 | 温度  | ΔS   | 质量分 | 状态'
```

In the format string for each row, add quality:

```js
`    ${String(s.round).padStart(2)}  | ${s.temp.toFixed(2)}  | ${s.deltaS.toFixed(2)} | ${(s.quality ?? '—').toString().padStart(4)} | ${s.status} ${bar}`;
```

Add per-score breakdown at the end of the report (before final divider):

```js
// 综合评分
const avgQuality =
  roundStats.reduce((sum, s) => sum + (s.quality ?? 0), 0) / roundStats.length;
console.log(`  本轮讨论综合评分：${avgQuality.toFixed(0)} / 100`);
```

- [ ] **Step 4: Run full discussion test to verify integration**

Run: `cd 80-PROJECTS/ai-roundtable && node index.js "测试质量评分" -r 3`
Expected: Output table shows quality score column, final report shows 综合评分

- [ ] **Step 5: Commit**

```bash
git add index.js
git commit -m "feat: integrate QualityScorer into main loop and report"
```

---

## Verification

After all tasks, run:

```bash
cd 80-PROJECTS/ai-roundtable
node index.js "AI是否会取代人类工作" -r 4
```

Verify:

1. Table shows quality score per round
2. No crashes
3. 综合评分 appears at end
4. All 6 personas still respond
