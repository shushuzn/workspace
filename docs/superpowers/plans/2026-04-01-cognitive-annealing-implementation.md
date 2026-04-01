# Cognitive Annealing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add adaptive temperature scheduling and concept-jump measurement to ai-roundtable CLI, replacing the fixed temperature=0.2 with a dynamic cooling schedule that detects ΔS peaks.

**Architecture:** Three new classes (TemperatureScheduler, ConceptJumpTracker, MiniMaxEmbedder) plug into the existing main loop. Minimal changes to existing askPersona and persona definitions.

**Tech Stack:** Node.js ES modules, MiniMax Chat API + Embedding API, no new npm dependencies.

---

## File Map

| 文件 | 职责 |
|------|------|
| `80-PROJECTS/ai-roundtable/index.js` | 主循环改造：动态温度、ΔS 测量、退火报告 |
| `80-PROJECTS/ai-roundtable/shared/embedder.js` | 新增：嵌入接口（MiniMaxEmbedder） |
| `80-PROJECTS/ai-roundtable/shared/vectorUtils.js` | 新增：向量工具（cosineDistance） |
| `80-PROJECTS/ai-roundtable/.env` | 新增 EMBEDDER_* 配置 |

---

## Task 1: 向量工具函数

**Files:**
- Create: `80-PROJECTS/ai-roundtable/shared/vectorUtils.js`

- [ ] **Step 1: 创建 vectorUtils.js**

```javascript
// shared/vectorUtils.js
/**
 * cosineDistance — 余弦距离，1 - cosine_similarity
 * @param {number[]} a
 * @param {number[]} b
 * @returns {number}
 */
export function cosineDistance(a, b) {
  const dot = a.reduce((s, ai, i) => s + ai * b[i], 0);
  const normA = Math.sqrt(a.reduce((s, ai) => s + ai * ai, 0));
  const normB = Math.sqrt(b.reduce((s, bi) => s + bi * bi, 0));
  if (normA === 0 || normB === 0) return 1.0;
  return 1 - dot / (normA * normB);
}
```

- [ ] **Step 2: 提交**

```bash
git add 80-PROJECTS/ai-roundtable/shared/vectorUtils.js
git commit -m "feat(ai-roundtable): add cosineDistance utility"
```

---

## Task 2: Embedder 接口与 MiniMax 实现

**Files:**
- Create: `80-PROJECTS/ai-roundtable/shared/embedder.js`

- [ ] **Step 1: 创建 embedder.js**

```javascript
// shared/embedder.js
import 'dotenv/config';

const EMBED_API_URL = process.env.EMBEDDER_API_URL || 'https://api.minimaxi.com/v1/embeddings';
const EMBED_MODEL = process.env.EMBEDDER_MODEL || 'embedding-2';
const EMBED_API_KEY = process.env.MINIMAX_API_KEY;  // 复用已有 key

export class MiniMaxEmbedder {
  /** 单文本嵌入 */
  async embed(text) {
    const res = await fetch(EMBED_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${EMBED_API_KEY}`,
      },
      body: JSON.stringify({ model: EMBED_MODEL, input: text }),
    });
    if (!res.ok) throw new Error(`Embedding API error: ${res.status}`);
    const data = await res.json();
    return data.data?.[0]?.embedding ?? [];
  }

  /** 批量嵌入（单次 API 调用） */
  async embedBatch(texts) {
    const res = await fetch(EMBED_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${EMBED_API_KEY}`,
      },
      body: JSON.stringify({ model: EMBED_MODEL, input: texts }),
    });
    if (!res.ok) throw new Error(`Embedding API error: ${res.status}`);
    const data = await res.json();
    return (data.data ?? []).map(item => item.embedding ?? []);
  }
}
```

- [ ] **Step 2: 提交**

```bash
git add 80-PROJECTS/ai-roundtable/shared/embedder.js
git commit -m "feat(ai-roundtable): add MiniMaxEmbedder with batch support"
```

---

## Task 3: TemperatureScheduler

**Files:**
- Create: `80-PROJECTS/ai-roundtable/shared/temperatureScheduler.js`

- [ ] **Step 1: 创建 temperatureScheduler.js**

```javascript
// shared/temperatureScheduler.js

export class TemperatureScheduler {
  constructor(config = {}) {
    this.config = {
      initialTemp: config.initialTemp ?? 1.2,
      coolingRate: config.coolingRate ?? 0.88,
      minTemp: config.minTemp ?? 0.3,
      plateauRounds: config.plateauRounds ?? 2,
      earlyStopDeltaS: config.earlyStopDeltaS ?? 0.05,
      deltaSThreshold: config.deltaSThreshold ?? 0.35,
      minRoundsBeforeEarlyStop: config.minRoundsBeforeEarlyStop ?? 4,
      ...config,
    };
    this.currentTemp = this.config.initialTemp;
    this.deltaSHistory = [];
    this.roundsSinceSignificantDelta = 0;
    this.criticalDetected = false;
    this.plateauRemaining = 0;
    this.plateauTemperature = null;
    this.tempHistory = [];  // 记录每轮温度
  }

  /** 获取当前轮温度（不在此处 push tempHistory，由调用方管理） */
  getTemperature() {
    if (this.plateauRemaining > 0) {
      return this.plateauTemperature ?? this.currentTemp;
    }
    return Math.min(this.currentTemp, this.config.minTemp);
  }

  /** 记录本轮温度（由主循环调用，每轮只 push 一次） */
  pushTempHistory(t) {
    this.tempHistory.push(t);
  }

  /** 记录本轮 ΔS */
  recordDeltaS(deltaS) {
    this.deltaSHistory.push(deltaS);
    if (deltaS < this.config.earlyStopDeltaS) {
      this.roundsSinceSignificantDelta++;
    } else {
      this.roundsSinceSignificantDelta = 0;
    }
  }

  /** 检测是否应进入 plateau */
  shouldEnterPlateau() {
    if (this.deltaSHistory.length < 3) return false;
    if (this.criticalDetected) return false;
    const n = this.deltaSHistory.length;
    const prev = this.deltaSHistory[n - 2];
    const curr = this.deltaSHistory[n - 1];
    return curr > prev && curr > this.config.deltaSThreshold;
  }

  /** 进入 plateau */
  enterPlateau() {
    this.criticalDetected = true;
    this.plateauRemaining = this.config.plateauRounds;
    this.plateauTemperature = this.currentTemp;
  }

  /** 进入下一轮 */
  nextRound() {
    if (this.plateauRemaining > 0) {
      this.plateauRemaining--;
      if (this.plateauRemaining === 0) {
        // plateau 结束，恢复从峰值温度继续衰减
        this.currentTemp = this.plateauTemperature ?? this.currentTemp;
      }
    } else {
      this.currentTemp *= this.config.coolingRate;
    }
  }

  /** 连续几轮无显著 ΔS */
  getRoundsSinceLastSignificantDelta() {
    return this.roundsSinceSignificantDelta;
  }

  /** 获取所有统计信息（供报告使用） */
  getStats() {
    return {
      tempHistory: this.tempHistory,
      deltaSHistory: this.deltaSHistory,
      criticalTemp: this.plateauTemperature,
      criticalDetected: this.criticalDetected,
    };
  }
}
```

- [ ] **Step 2: 提交**

```bash
git add 80-PROJECTS/ai-roundtable/shared/temperatureScheduler.js
git commit -m "feat(ai-roundtable): add TemperatureScheduler with plateau detection"
```

---

## Task 4: ConceptJumpTracker

**Files:**
- Create: `80-PROJECTS/ai-roundtable/shared/conceptJumpTracker.js`

- [ ] **Step 1: 创建 conceptJumpTracker.js**

```javascript
// shared/conceptJumpTracker.js
import { cosineDistance } from './vectorUtils.js';

export class ConceptJumpTracker {
  constructor(embedder) {
    this.embedder = embedder;
    this.roundEmbeddings = [];
    this.roundDeltaSHistory = [];
  }

  /**
   * 处理一轮发言：批量嵌入 → 计算 ΔS
   * @param {string[]} utterances - 当前轮所有发言文本
   * @returns {Promise<number>} ΔS 值
   */
  async processRound(utterances) {
    if (utterances.length === 0) return 0;

    let vectors;
    try {
      vectors = await this.embedder.embedBatch(utterances);
    } catch (err) {
      // Embedder API 失败时，优雅降级：跳过 ΔS 测量，记录 0
      console.warn(`  ⚠ 嵌入 API 失败：${err.message}，跳过 ΔS 测量`);
      return 0;
    }
    const dim = vectors?.[0]?.length ?? 0;
    if (dim === 0) return 0;

    // 计算该轮平均嵌入
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

  getHistory() {
    return this.roundDeltaSHistory;
  }
}
```

- [ ] **Step 2: 提交**

```bash
git add 80-PROJECTS/ai-roundtable/shared/conceptJumpTracker.js
git commit -m "feat(ai-roundtable): add ConceptJumpTracker with batch embedding"
```

---

## Task 5: 修改 askPersona 支持动态温度

**Files:**
- Modify: `80-PROJECTS/ai-roundtable/index.js:94-140`

原始函数签名：`async function askPersona(messages, persona, topic, abortSignal)`（4 个参数）
新签名：`async function askPersona(messages, persona, topic, temperature, abortSignal)`（5 个参数，topic 保留）

- [ ] **Step 1: 修改函数签名**

在 `index.js` 第 94 行，将：
```javascript
async function askPersona(messages, persona, topic, abortSignal) {
```
改为：
```javascript
async function askPersona(messages, persona, topic, temperature, abortSignal) {
```

- [ ] **Step 2: 将 `temperature: 0.2` 替换为参数**

在 `index.js` 第 119 行附近，将：
```javascript
temperature: 0.2,
```
改为：
```javascript
temperature: temperature,
```

- [ ] **Step 3: 更新所有调用处**

找到所有 `askPersona(history, persona, ...)` 调用，更新为传入 `topic` 和 `temperature`：

原调用（index.js:260）：
```javascript
fullText = await askPersona(history, persona, topic, abortController.signal);
```
改为（保留 topic，追加 temperature 参数 T）：
```javascript
fullText = await askPersona(history, persona, topic, T, abortController.signal);
```

- [ ] **Step 4: 提交**

```bash
git add 80-PROJECTS/ai-roundtable/index.js
git commit -m "feat(ai-roundtable): make askPersona accept dynamic temperature"
```

---

## Task 6: 主循环改造 + 退火报告输出

**Files:**
- Modify: `80-PROJECTS/ai-roundtable/index.js`

改造主循环（around lines 246-296），改造 `parseArgs`（支持 `--temp` 和 `--rounds` 参数），新增报告输出函数。

- [ ] **Step 1: 在文件顶部 import 新增的类**

```javascript
import { TemperatureScheduler } from './shared/temperatureScheduler.js';
import { ConceptJumpTracker } from './shared/conceptJumpTracker.js';
import { MiniMaxEmbedder } from './shared/embedder.js';
```

- [ ] **Step 2: 修改 DEFAULT_ROUNDS**

原始：`const DEFAULT_ROUNDS = 3;`
改为：`const DEFAULT_ROUNDS = 8;`

- [ ] **Step 3: 修改 parseArgs 支持新参数**

原始 `parseArgs` 只支持 `-r`。在函数开头添加变量声明，在循环末尾、topic 赋值之前增加：
```javascript
let customInitialTemp = null;  // 新增：初始温度覆盖

// ... existing -r/--rounds handling ...

if ((args[i] === '--temp' || args[i] === '-t') && args[i + 1] && !args[i + 1].startsWith('-')) {
  const t = parseFloat(args[i + 1]);
  if (!isNaN(t) && t > 0) customInitialTemp = Math.min(t, 2.0);  // 上限 2.0
  i++;
}
```

同时在 `parseArgs` 返回语句中添加 `customInitialTemp`：
```javascript
return { topic, rounds, customInitialTemp };
```

- [ ] **Step 4: 替换主循环**

将原主循环（约 lines 246-296）替换为：

```javascript
// ─── 退火模式主循环 ───────────────────────────────────────
const { topic, rounds, customInitialTemp } = parseArgs(process.argv);
const scheduler = new TemperatureScheduler(
  customInitialTemp ? { initialTemp: customInitialTemp } : {}
);
const embedder = new MiniMaxEmbedder();
const tracker = new ConceptJumpTracker(embedder);
const roundResponses = [];

// 记录 { round, temp, deltaS, status } 用于报告
const roundStats = [];

try {
  for (let round = 0; round < rounds; round++) {
    const T = scheduler.getTemperature();
    scheduler.pushTempHistory(T);  // 每轮只 push 一次
    const roundUtterances = [];
    roundResponses[round] = [];

    console.log(color(`📍 第 ${round + 1} / ${rounds} 轮  [T=${T.toFixed(3)}]`, 90) + '\n');

    for (const persona of personas) {
      const pName = color(`${persona.icon} ${persona.name}`, persona.color);
      process.stdout.write(`  ${pName} 思考中...`);

      const dotTimer = setInterval(() => process.stdout.write(color('.', persona.color)), 150);

      let fullText = '';
      try {
        fullText = await askPersona(history, persona, topic, T, abortController.signal);
      } catch (err) {
        if (err.name === 'AbortError') {
          clearInterval(dotTimer);
          console.log('\n\n已停止。');
          return;
        }
        fullText = color(`⚠ ${err.message}`, 31);
      }

      clearInterval(dotTimer);
      process.stdout.write('\r' + '\x1b[K');
      console.log(`  ${pName}：${fullText}`);

      roundResponses[round].push({ persona, text: fullText, temp: T });
      roundUtterances.push(fullText);
      history.push({ role: 'assistant', content: fullText });
    }

    // ─── 轮结束：计算 ΔS ──────────────────────────────
    const deltaS = await tracker.processRound(roundUtterances);
    scheduler.recordDeltaS(deltaS);

    // 记录本轮统计
    let status = '';
    if (scheduler.shouldEnterPlateau()) {
      scheduler.enterPlateau();
      status = '⭐ ΔS 峰值（触发 plateau）';
    } else if (scheduler.plateauRemaining > 0) {
      status = '🐢 plateau';
    } else if (T <= scheduler.config.minTemp) {
      status = '❄️ 最低温度';
    } else {
      status = '🔥 高温探索';
    }
    roundStats.push({ round: round + 1, temp: T, deltaS, status });

    // ─── 早停检查 ───────────────────────────────────
    if (round >= scheduler.config.minRoundsBeforeEarlyStop - 1 &&
        scheduler.getRoundsSinceLastSignificantDelta() > 3) {
      console.log(color('\n⚠ 讨论已收敛，提前结束', 33));
      break;
    }

    scheduler.nextRound();

    if (round < rounds - 1) {
      history.push({
        role: 'user',
        content: `第 ${round + 2} 轮：请继续讨论，从另一角度深入。`,
      });
    }
  }

  printDivider();
  console.log(color('\n✅ 讨论结束\n', 32));

  // ─── 输出退火报告 ───────────────────────────────────
  const stats = scheduler.getStats();
  printAnnealingReport(topic, rounds, stats, roundStats);

  const filename = saveResult(topic, rounds, roundResponses.flat());
  console.log(color(`💾 讨论记录已保存：${filename}`, 32));

} catch (err) {
  console.error(color(`\n错误：${err.message}`, 31));
  process.exit(1);
}
```

- [ ] **Step 5: 添加报告输出函数**

在 `printDivider` 函数之后添加：

```javascript
// ─── 退火报告 ───────────────────────────────────────────
function printAnnealingReport(topic, totalRounds, stats, roundStats) {
  const { tempHistory, deltaSHistory, criticalTemp, criticalDetected } = stats;

  console.log(color('══════════════════════════════════════════════', 1));
  console.log(color('  自适应温度探索报告', 1));
  console.log(color('══════════════════════════════════════════════', 1));
  console.log(`  话题：${topic}`);
  console.log(`  轮次：${roundStats.length}`);
  console.log('');
  console.log('  温度调度参数');
  console.log(`    初始温度：${tempHistory[0]?.toFixed(2) ?? 'N/A'}`);
  console.log(`    冷却速率：0.88`);
  console.log(`    临界 plateau：2 轮`);
  console.log('');
  console.log('  概念跳跃曲线（ΔS）');
  console.log('    ΔS 越高 = 讨论方向偏移越大');
  console.log('');
  console.log('  轮次 | 温度  | ΔS   | 状态');
  console.log('  -----|-------|------|------');

  for (const s of roundStats) {
    const bar = s.deltaS > 0.35 ? '★'.repeat(Math.round(s.deltaS * 5)) : '';
    console.log(
      `    ${String(s.round).padStart(2)}  | ${s.temp.toFixed(2)}  | ${s.deltaS.toFixed(2)} | ${s.status} ${bar}`
    );
  }

  console.log('');
  if (criticalDetected && criticalTemp !== null) {
    console.log(`  临界温度：${criticalTemp.toFixed(2)}（ΔS 峰值）`);
  } else {
    console.log('  临界温度：未检测到显著峰值');
  }
  console.log(color('══════════════════════════════════════════════\n', 1));
}
```

- [ ] **Step 6: 提交**

```bash
git add 80-PROJECTS/ai-roundtable/index.js
git commit -m "feat(ai-roundtable): implement annealing main loop with ΔS tracking"
```

---

## Task 7: .env 配置说明

**Files:**
- Modify: `80-PROJECTS/ai-roundtable/.env`

在 `.env` 文件末尾添加（如果已有 EMBEDDER_* 配置则跳过）：

```
# 嵌入器配置（用于 ΔS 测量）
EMBEDDER_MODEL=embedding-2
# EMBEDDER_API_URL=https://api.minimaxi.com/v1/embeddings  # 可选，使用默认值可不配置
```

---

## Task 8: 冒烟测试（手动验证）

- [ ] **Step 1: 检查 .env 中是否有 MINIMAX_API_KEY**

如果无，添加一个测试 key（或确认已有 key 可用）。

- [ ] **Step 2: 运行一个简短发散测试**

```bash
cd 80-PROJECTS/ai-roundtable
node index.js "AI 的未来是通用智能吗" -r 4
```

预期：
- 每轮显示当前温度 `[T=1.200]` 等
- 讨论结束后显示退火报告表格
- 有 `📍 第 N / 4 轮 [T=...]` 输出

- [ ] **Step 3: 确认 ΔS 有数值输出**

检查报告中 ΔS 列是否有 0.00 ~ 0.60 范围的数字（无 NaN）。

---

## 执行顺序

1. Task 1 → Task 2 → Task 3 → Task 4（都是新增 shared/ 文件）
2. Task 5 → Task 6（修改 index.js）
3. Task 7（.env）
4. Task 8（冒烟测试）

每个 Task 完成即提交，共 6 个 commit（Tasks 1-4 各 1 个 + Tasks 5、6 各 1 个）。
