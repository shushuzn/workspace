# 自适应温度探索：多 Agent 讨论系统的动态调度

## 概述

在 AI 多人格讨论中，LLM 的 `temperature` 参数控制采样的随机性——高温产生更多创意跳跃，低温产生更确定性收敛。本系统通过**自适应温度调度**，在不同话题上动态探索最优温度区间，并测量"概念跳跃幅度 ΔS"作为讨论质量的代理指标。

**注意**：本设计不再声称与物理退火有严格的理论对应，而是作为**实证探索框架**——我们还不知道温度调度是否有效，所以设计重点是**可测量、可对比、可复现**。

## 设计目标

1. 在单次讨论运行中，按温度曲线动态调整 LLM 采样温度
2. 测量每轮的概念跳跃幅度 ΔS（基于嵌入向量）
3. 比较不同温度下的 ΔS 曲线，找到温度-涌现的规律
4. 输出可读的实验报告和温度曲线

## 核心指标：概念跳跃 ΔS

### 定义

每轮所有发言的平均嵌入向量记为 `E_round`。定义：

```
ΔS[round] = 1 - cosine_similarity(E_current, E_previous)
```

即当前轮与前一轮的平均嵌入向量之间的余弦距离。ΔS 越大，表示讨论方向发生了越大偏移。

### 限制说明

- ΔS 衡量的是**讨论方向漂移**，不是"涌现质量"
- 漂移可能是：话题的自然演化、观点的真正融合、或者只是跳到了无关方向
- 这是一个**代理指标**，需要实验验证其与人类判断的相关性

## 架构

### 1. 温度调度器（TemperatureScheduler）

温度调度器控制每轮发言的温度，遵循指数衰减曲线 + 峰值 plateau 机制：

**温度曲线**：
- round 0: T₀ = 1.2
- 每轮：`T = T₀ × α^round`，其中 α = 0.88
- 当检测到 ΔS 峰值后，进入 plateau（温度不变 2 轮）
- 到达 minTemp = 0.3 后不再下降

**关键方法**：
- `getTemperature()` — 获取当前轮温度
- `recordDeltaS(deltaS)` — 记录 ΔS，用于峰值检测
- `shouldEnterPlateau()` — 检测是否触发 plateau
- `nextRound()` — 进入下一轮
- `getRoundsSinceLastSignificantDelta()` — 获取早停计数

完整实现见 **Section 5**。

### 2. 嵌入器接口（EmbedderInterface）

```typescript
interface Embedder {
  embed(text: string): Promise<number[]>;   // 单文本嵌入
  embedBatch(texts: string[]): Promise<number[][]>;  // 批量嵌入
}

class MiniMaxEmbedder implements Embedder {
  // 配置：API key、endpoint、model name
  async embed(text: string): Promise<number[]> {
    // POST to MiniMax embedding endpoint
    // 返回归一化向量
  }
  async embedBatch(texts: string[]): Promise<number[][]> {
    // 单次 API 调用处理所有文本（降低 API 次数）
  }
}
```

**配置参数**（在 `.env` 或命令行）：
```
EMBEDDER_PROVIDER=minimax   # or "openai", "local"
EMBEDDER_MODEL=embedding-2  # MiniMax embedding 模型名（待确认）
EMBEDDER_API_KEY=          # 复用现有 MINIMAX_API_KEY
EMBEDDER_API_URL=          # 可选，默认 https://api.minimaxi.com/v1/embeddings
```

### 3. 概念跳跃追踪器（ConceptJumpTracker）

```typescript
class ConceptJumpTracker {
  private embedder: Embedder;
  private roundEmbeddings: number[][] = [];  // 每轮平均嵌入
  private roundDeltaSHistory: number[] = []; // 每轮 ΔS 历史（用于报告）

  constructor(embedder: Embedder) { this.embedder = embedder; }

  async processRound(utterances: string[]): Promise<number> {
    // 批量嵌入该轮所有发言（1次 API 调用）
    const vectors = await this.embedder.embedBatch(utterances);
    // 计算该轮平均嵌入
    const dim = vectors[0].length;
    const roundMean = vectors.reduce(
      (acc, v) => acc.map((a, i) => a + v[i]),
      Array(dim).fill(0)
    ).map(x => x / vectors.length);
    // 计算 ΔS
    const deltaS = this.roundEmbeddings.length > 0
      ? cosineDistance(roundMean, this.roundEmbeddings[this.roundEmbeddings.length - 1])
      : 0;
    this.roundEmbeddings.push(roundMean);
    this.roundDeltaSHistory.push(deltaS);
    return deltaS;
  }

  getHistory(): number[] { return this.roundDeltaSHistory; }
}

// ─── 向量工具函数 ───────────────────────────────────────────
function cosineDistance(a: number[], b: number[]): number {
  const dot = a.reduce((s, ai, i) => s + ai * b[i], 0);
  const normA = Math.sqrt(a.reduce((s, ai) => s + ai * ai, 0));
  const normB = Math.sqrt(b.reduce((s, bi) => s + bi * bi, 0));
  return 1 - dot / (normA * normB);
}
```

### 4. 轮边界数据流

每轮发言存储在 `roundResponses[]`（当前轮结束后再处理整轮）：

```typescript
// 主循环
const roundResponses: { persona: Persona, text: string, temp: number }[][] = [];

for (let round = 0; round < rounds; round++) {
  const T = scheduler.getTemperature();
  const roundUtterances: string[] = [];
  roundResponses[round] = [];  // ⚠ 初始化当前轮数组

  for (const persona of personas) {
    const text = await askPersona(history, persona, T);  // 传入温度
    roundResponses[round].push({ persona, text, temp: T });
    roundUtterances.push(text);
    history.push({ role: 'assistant', content: text });
  }

  // 轮结束：计算 ΔS
  const deltaS = await tracker.processRound(roundUtterances);
  scheduler.recordDeltaS(deltaS);  // 用于 plateau 检测

  // 检查是否进入 plateau
  if (scheduler.shouldEnterPlateau()) {
    scheduler.enterPlateau();
  }

  scheduler.nextRound();

  if (round < rounds - 1) {
    history.push({ role: 'user', content: `第 ${round + 2} 轮：请继续讨论，从另一角度深入。` });
  }
}
```

### 5. 峰值检测算法

```typescript
class TemperatureScheduler {
  private config: {
    initialTemp: number;
    coolingRate: number;
    minTemp: number;
    plateauRounds: number;
    earlyStopDeltaS: number;
  };
  private currentTemp: number;  // ⚠ 已初始化
  private deltaSHistory: number[] = [];
  private roundsSinceSignificantDelta: number = 0;  // ⚠ 新增
  private criticalDetected: boolean = false;
  private plateauRemaining: number = 0;
  private plateauTemperature: number | null = null;  // ⚠ 捕获峰值温度

  constructor(config = {}) {
    this.config = {
      initialTemp: 1.2,
      coolingRate: 0.88,
      minTemp: 0.3,
      plateauRounds: 2,
      earlyStopDeltaS: 0.05,
      ...config
    };
    this.currentTemp = this.config.initialTemp;  // ⚠ 修复：初始化
  }

  recordDeltaS(deltaS: number): void {
    this.deltaSHistory.push(deltaS);
    if (deltaS < this.config.earlyStopDeltaS) {
      this.roundsSinceSignificantDelta++;
    } else {
      this.roundsSinceSignificantDelta = 0;
    }
  }

  shouldEnterPlateau(): boolean {
    if (this.deltaSHistory.length < 3) return false;
    if (this.criticalDetected) return false;

    const n = this.deltaSHistory.length;
    const prev = this.deltaSHistory[n - 2];
    const curr = this.deltaSHistory[n - 1];

    // 局部峰值：当前 > 前一个 AND 当前 > 阈值
    if (curr > prev && curr > 0.35) {
      return true;
    }
    return false;
  }

  enterPlateau(): void {
    this.criticalDetected = true;
    this.plateauRemaining = this.config.plateauRounds;
    this.plateauTemperature = this.currentTemp;  // ⚠ 捕获临界温度
  }

  getTemperature(): number {
    if (this.plateauRemaining > 0) {
      return this.plateauTemperature ?? this.currentTemp;  // ⚠ 使用 plateau 温度
    }
    // 指数衰减，到达 minTemp 后不再下降
    return Math.min(this.currentTemp, this.config.minTemp);  // ⚠ 修复：max→min
  }

  nextRound(): void {
    if (this.plateauRemaining > 0) {
      this.plateauRemaining--;
      if (this.plateauRemaining === 0) {
        // plateau 结束，恢复从 plateau 温度继续衰减
        this.currentTemp = this.plateauTemperature ?? this.currentTemp;
      }
    } else {
      this.currentTemp *= this.config.coolingRate;
    }
  }

  // ⚠ 新增方法
  getRoundsSinceLastSignificantDelta(): number {
    return this.roundsSinceSignificantDelta;
  }

  getStats(): { tempHistory: number[], deltaSHistory: number[], criticalTemp: number | null } {
    return {
      tempHistory: [],  // 温度历史由主循环填充
      deltaSHistory: this.deltaSHistory,
      criticalTemp: this.plateauTemperature,
    };
  }
}
```

### 6. 早停机制（Early Stopping）

```typescript
// 每轮结束后检查（⚠ 需至少跑满 4 轮才允许触发早停）
if (round >= 4 && scheduler.getRoundsSinceLastSignificantDelta() > 3) {
  // ΔS 连续 3 轮 < 0.05，讨论趋于稳定，可以提前结束
  console.log(color('⚠ 讨论已收敛，提前结束', 33));
  break;
}
```

### 7. 修改后的 askPersona

```typescript
async function askPersona(messages, persona, temperature, abortSignal) {
  // ... 现有 controller/signal 逻辑 ...
  const res = await fetch(API_URL, {
    method: 'POST',
    headers: { /* ... */ },
    body: JSON.stringify({
      model: MODEL,
      messages: allMessages,
      max_tokens: 1500,
      temperature: temperature,  // 动态温度，不再硬编码 0.2
      stream: false,
    }),
    signal,
  });
  // ...
}
```

## 参数配置

| 参数 | 默认值 | 说明 |
|------|--------|------|
| initialTemp | 1.2 | 探索起点（保守，避免高温崩质量） |
| coolingRate | 0.88 | 每轮乘以此系数 |
| minTemp | 0.3 | 温度下限 |
| rounds | **8** | 默认轮次（修订：原 3 轮不够） |
| plateauRounds | 2 | 峰值后温度不变的轮数 |
| deltaSThreshold | 0.35 | ΔS 峰值检测阈值 |
| earlyStopDeltaS | 0.05 | 连续低于此值则早停 |
| earlyStopRounds | 3 | 连续多少轮触发早停 |

## 改动文件清单

| 文件 | 变更 |
|------|------|
| `index.js` | 新增 `TemperatureScheduler`、`ConceptJumpTracker` 类；修改 `askPersona` 支持动态温度；修改主循环增加 ΔS 测量和 plateau 检测 |
| `.env` | 新增 `EMBEDDER_*` 相关配置（可选，默认用 MiniMax） |
| `package.json` | 无变更 |

## 输出报告格式

```
══════════════════════════════════════════════
  自适应温度探索报告
══════════════════════════════════════════════
话题：{topic}
轮次：{rounds}
耗时：{duration}

温度调度参数
  初始温度：{T0}
  冷却速率：{α}
  临界 plateau：{plateauRounds} 轮

概念跳跃曲线（ΔS）
  ΔS 越高 = 讨论方向偏移越大

轮次 | 温度  | ΔS   | 状态
-----|-------|------|------
  1  | 1.20  | 0.18 | 🔥 高温探索
  2  | 1.06  | 0.24 |
  3  | 0.93  | 0.22 |
  4  | 0.82  | 0.41 | ⭐ ΔS 峰值（触发 plateau）
  5  | 0.82  | 0.19 | 🐢 plateau
  6  | 0.72  | 0.15 | 🐢 plateau
  7  | 0.63  | 0.11 |
  8  | 0.56  | 0.08 |

峰值信息
  临界轮次：第 4 轮
  临界温度：0.82
  临界 ΔS：0.41

结论：ΔS 在 T≈0.82 附近出现峰值，
      之后的 plateau 使系统在临界温度
      附近多停留了 2 轮。
══════════════════════════════════════════════
```

## 实验设计（验证计划）

### 实验 1：温度曲线对比
```
话题集：10 个不同话题
每话题跑 3 次：
  A. 固定温度 T=0.2（baseline）
  B. 固定温度 T=0.8（探索）
  C. 退火调度 T₀=1.2, α=0.88

比较：ΔS 曲线形状、各轮观点多样性（待定义）、人工评估质量
```

### 实验 2：临界温度复现性
```
同一话题 × 5 次退火
检验：临界温度是否稳定？
预期：如果临界温度稳定，说明存在话题相关的最优探索温度
```

### 实验 3：ΔS 与人工判断相关性
```
人工标注：同一组讨论中哪些发言有"创意/涌现感"
统计：这些发言的 ΔS 是否显著高于普通发言？
```

## 风险与限制

1. **嵌入 API 成本**：每轮批量调用 Embedder（6 personas × N rounds）
   - 缓解：使用 `embedBatch` 一次处理整轮，round 只算 1 次 API 调用
2. **MiniMax 嵌入接口**：尚未验证 `embedding-2` 的存在和参数
   - 缓解：接口设计为可插拔，先用 OpenAI 嵌入或本地模型替代测试
3. **ΔS ≠ 涌现**：代理指标，需人工验证
   - 缓解：设计实验 3 检验相关性
4. **温度上限未验证**：MiniMax 聊天模型在 T>1.0 时可能质量下降
   - 缓解：T₀ 从 1.2 开始（而非更激进的 1.5），可根据实验结果上调
5. **轮次不足**：少于 6 轮无法充分观察退火过程
   - 缓解：默认轮次改为 8

## 待确认事项（实现前必须验证）

- [ ] MiniMax Embedding API 端点和模型名（`embedding-2` 是否存在？）
- [ ] MiniMax 模型 temperature 有效范围（能否接受 1.0 以上？）
- [ ] OpenAI Embedding 作为 fallback 的 API key 配置

## 参考文献（作为灵感，非严格理论对应）

- Kirkpatrick et al., "Optimization by Simulated Annealing" (1983) — 灵感来源
- Wei et al., "Emergent Abilities of Large Language Models" (2022) — 涌现现象观察
- Schaeffer et al., "Are Emergent Abilities of Large Language Models a Mirage?" (2023) — 对涌现指标可靠性的质疑
