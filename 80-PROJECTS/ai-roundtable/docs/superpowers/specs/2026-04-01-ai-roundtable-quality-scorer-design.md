# AI Roundtable — 讨论质量评分设计

> **Goal:** 给每轮讨论打一个 0-100 的质量分，用于复盘判断"这轮讨论好不好"。

## 评分维度

| 维度 | 权重 | 计算方式 | 解释 |
|------|------|----------|------|
| 人均观点变化 | 0.4 | mean_i(cosineDistance(personaEmbedding_i_t, personaEmbedding_i_{t-1})) | 每个人格相比上轮自己有多大变化，取均值。衡量个体视角的流动性 |
| 概念跳跃 | 0.3 | ΔS（取原始值，不 clamp） | 整体讨论方向的突变幅度（与人均变化不同：前者是个体变化，后者是群体重心漂移） |
| 活跃均衡度 | 0.3 | 1 - (std(contributions) / (mean(contributions) + ε)) | 加 ε=0.001 防除零。越接近1=全员参与，越接近0=某人格主导 |

**质量分 = 人均观点变化×0.4 + 概念跳跃×0.3 + 活跃均衡度×0.3 → 0-100**

> 注意：Round 1 无法计算人均观点变化（没有上轮数据），该维度记为 0.5（中性值）。

## 数据来源

`ConceptJumpTracker.processRound()` 已经返回：
- `deltaS` — 本轮 ΔS
- `contributions[]` — 每人格与上轮均值的距离

`index.js` 已有 `roundEmbeddings` 历史，可计算 cosineSimilarity。

## 新增文件

```
shared/
  qualityScorer.js   ← 新增
```

## 架构

```js
// shared/qualityScorer.js
import { cosineDistance } from './vectorUtils.js';

export class QualityScorer {
  constructor() {
    this.prevPersonaEmbeddings = []; // [[round0_per_persona], [round1_per_persona], ...]
  }

  /**
   * @param {number[][]} personaEmbeddings - 当前轮每个人的嵌入 [personaCount][dim]
   * @param {number} deltaS - ConceptJumpTracker.processRound() 返回的 deltaS
   * @param {number[]} contributions - ConceptJumpTracker.processRound() 返回的 contributions[]
   * @returns {{ quality: number, fluidity: number, jump: number, balance: number }}
   */
  scoreRound(personaEmbeddings, deltaS, contributions) {
    const ε = 0.001;

    // 人均观点变化
    let fluidity = 0.5; // Round 1 默认中性值
    if (this.prevPersonaEmbeddings.length > 0) {
      const prev = this.prevPersonaEmbeddings[this.prevPersonaEmbeddings.length - 1];
      fluidity = personaEmbeddings.reduce((sum, emb, i) =>
        sum + cosineDistance(emb, prev[i]), 0) / personaEmbeddings.length;
    }

    // 概念跳跃（直接用原始 ΔS，不 clamp）
    const jump = deltaS;

    // 活跃均衡度（防除零）
    const mean = contributions.reduce((a, b) => a + b, 0) / contributions.length;
    const std = Math.sqrt(contributions.reduce((s, v) => s + (v - mean) ** 2, 0) / contributions.length);
    const balance = 1 - (std / (mean + ε));

    const quality = fluidity * 0.4 + jump * 0.3 + balance * 0.3;

    this.prevPersonaEmbeddings.push(personaEmbeddings);
    return { quality: Math.min(100, quality * 100), fluidity, jump, balance };
  }
}
```

## 改动点

### `index.js`
- 构造 `QualityScorer` 实例
- `ConceptJumpTracker` 已有 `personaEmbeddings` 数组，可通过 `tracker.personaEmbeddings` 访问
- 每轮结束时调用 `scorer.scoreRound(tracker.personaEmbeddings[round], deltaS, contributions)`
- 记录到 `roundStats`（每轮 `{ round, temp, deltaS, contributions, status, quality }`）
- `printAnnealingReport()` 加质量分列和本轮综合评分

### `shared/conceptJumpTracker.js`
- **不改** — `processRound()` 已返回所需数据，`personaEmbeddings` 数组可直接访问

## 输出示例（退火报告增强）

```
  轮次 | 温度  | ΔS   | 质量分 | 状态
  -----|-------|------|-------|------
     1 | 1.20  | 0.00 |  58   | 🔥 高温探索
     2 | 1.06  | 0.08 |  63   | 🔥 高温探索
     ...

  本轮讨论综合评分：67 / 100（论点密度0.72 + 概念跳跃0.24 + 均衡度0.71）
```

## 风险

- 权重分配是经验值： fluidity×0.4 + jump×0.3 + balance×0.3 后续可根据实际评分结果校准
- Round 1 fluidity=0.5 为硬编码中性值：第一轮没有人均变化数据，这是合理妥协
- balance 分子为 0 时（所有人格贡献完全均等）= 1.0，符合预期
