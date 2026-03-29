# AI 圆桌多工具拆分实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将单个 `roundtable_discuss` 拆分为 `roundtable_start` / `roundtable_next` / `roundtable_stop` 三个独立工具，每次调用立即返回并显示发言内容，实现真正的实时输出。

**Architecture:** 链条状态持久化到文件，每次 `roundtable_next` 读取历史、追加新发言、返回新发言内容。Claude Code 会话中每次工具调用独立显示结果。

**Tech Stack:** TypeScript, MCP SDK, 文件持久化

---

## 文件

- Modify: `src/server.ts` - 重构为三个工具

---

## 任务 1：添加文件持久化辅助函数

**Files:**
- Modify: `src/server.ts`

- [ ] **Step 1: 添加 chain 文件路径和读写函数**

在 `callMinimax` 函数之前添加：

```typescript
// ─── chain 持久化 ───────────────────────────────────────
const CHAIN_FILE = path.join(os.tmpdir(), 'ai-roundtable-chain.json');

interface ChainEntry {
  persona: { id: string; name: string; icon: string };
  text: string;
  round: number;
  order: number;
}

interface ChainState {
  topic: string;
  totalRounds: number;
  chain: ChainEntry[];
  currentRound: number;
  currentOrder: number; // 在当前轮内的顺序（0-5）
}

function readChain(): ChainState | null {
  try {
    if (!fs.existsSync(CHAIN_FILE)) return null;
    return JSON.parse(fs.readFileSync(CHAIN_FILE, 'utf8'));
  } catch { return null; }
}

function writeChain(state: ChainState): void {
  fs.writeFileSync(CHAIN_FILE, JSON.stringify(state, null, 2), 'utf8');
}
```

需要添加导入：
```typescript
import fs from 'fs';
import os from 'os';
import path from 'path';
```

---

## 任务 2：改造 roundtable_start 工具

**Files:**
- Modify: `src/server.ts` - 修改 ListToolsRequestSchema 和 CallToolRequestSchema

- [ ] **Step 1: 更新工具列表为 3 个**

```typescript
tools: [
  {
    name: 'roundtable_start',
    description: '开始圆桌讨论。传入话题和轮数，初始化链条并返回第一个人格的发言。',
    inputSchema: {
      type: 'object',
      properties: {
        topic: { type: 'string', description: '讨论话题' },
        rounds: { type: 'number', description: '轮数', default: 3, minimum: 1, maximum: 10 },
      },
      required: ['topic'],
    },
  },
  {
    name: 'roundtable_next',
    description: '获取下一个发言。如果还有未完成的发言，返回下一人格的内容；否则返回"讨论已结束"。',
    inputSchema: { type: 'object', properties: {} },
  },
  {
    name: 'roundtable_stop',
    description: '强制停止当前讨论',
    inputSchema: { type: 'object', properties: {} },
  },
]
```

- [ ] **Step 2: 实现 roundtable_start 逻辑**

```typescript
if (name === 'roundtable_start') {
  const topic = (args as { topic?: string })?.topic;
  const rounds = Math.min(Math.max((args as { rounds?: number })?.rounds || 3, 1), 10);

  if (!topic?.trim()) return { content: [{ type: 'text', text: '请提供讨论话题。' }], isError: true };
  if (!API_KEY) return { content: [{ type: 'text', text: '错误：未设置 MINIMAX_API_KEY' }], isError: true };

  globalAbort.abort();
  globalAbort = new AbortController();

  const chain: ChainEntry[] = [];
  const state: ChainState = { topic, totalRounds: rounds, chain, currentRound: 0, currentOrder: 0 };
  writeChain(state);

  // 执行第一轮第一个人格（乐观者）
  const firstPersona = personas[0];
  const systemFull = `${firstPersona.systemPrompt}\n\n重要：直接输出你的观点，不要使用括号、不要输出思考过程、不要输出引号、不要解释。只输出纯文本。严格控制在2句话以内。`;
  const content = `话题：${topic}\n\n以下是之前的发言（按时间顺序）：\n（暂无）\n\n现在轮到 ${firstPersona.name} 发言：`;

  let answer: string;
  try {
    answer = await callMinimax(systemFull, content, globalAbort.signal);
  } catch (err) {
    answer = `⚠ ${err instanceof Error ? err.message : String(err)}`;
  }

  chain.push({ persona: { id: firstPersona.id, name: firstPersona.name, icon: firstPersona.icon }, text: answer, round: 0, order: 0 });
  state.currentOrder = 1; // 下一个是 order=1（怀疑者）
  writeChain(state);

  return {
    content: [{ type: 'text', text: `🔥 AI 圆桌讨论\n话题：${topic}\n轮数：${rounds}\n${'─'.repeat(50)}\n\n📍 第 1 / ${rounds} 轮\n\n  ${firstPersona.icon} ${firstPersona.name}：${answer}` }]
  };
}
```

---

## 任务 3：实现 roundtable_next 工具

**Files:**
- Modify: `src/server.ts`

- [ ] **Step 1: 实现 roundtable_next 逻辑**

```typescript
if (name === 'roundtable_next') {
  const state = readChain();
  if (!state) return { content: [{ type: 'text', text: '无进行中的讨论，请先调用 roundtable_start。' }], isError: true };

  const { topic, totalRounds, chain, currentRound, currentOrder } = state;

  // 判断是否还有下一条发言
  const nextRound = currentRound;
  const nextOrder = currentOrder;

  // 如果当前轮已结束，进入下一轮
  if (nextOrder >= personas.length) {
    const newRound = nextRound + 1;
    if (newRound >= totalRounds) {
      fs.unlinkSync(CHAIN_FILE);
      return { content: [{ type: 'text', text: `${'─'.repeat(50)}\n✅ 讨论结束（共 ${totalRounds} 轮，共 ${chain.length} 条发言）` }] };
    }
    // 下一轮
    state.currentRound = newRound;
    state.currentOrder = 0;
    writeChain(state);
    // 重新读取
    return { content: [{ type: 'text', text: `📍 第 ${newRound + 1} / ${totalRounds} 轮` }] };
  }

  // 获取下一人格
  const nextPersona = personas[nextOrder];
  const priorStatements = chain.map(e => `${e.persona.name}：${e.text}`).join('\n');

  const systemFull = `${nextPersona.systemPrompt}\n\n重要：直接输出你的观点，不要使用括号、不要输出思考过程、不要输出引号、不要解释。只输出纯文本。严格控制在2句话以内。`;
  const content = `话题：${topic}\n\n以下是之前的发言（按时间顺序）：\n${priorStatements}\n\n现在轮到 ${nextPersona.name} 发言：`;

  let answer: string;
  try {
    answer = await callMinimax(systemFull, content, globalAbort.signal);
  } catch (err) {
    answer = `⚠ ${err instanceof Error ? err.message : String(err)}`;
  }

  chain.push({ persona: { id: nextPersona.id, name: nextPersona.name, icon: nextPersona.icon }, text: answer, round: state.currentRound, order: state.currentOrder });
  state.currentOrder++;
  writeChain(state);

  return {
    content: [{ type: 'text', text: `  ${nextPersona.icon} ${nextPersona.name}：${answer}` }]
  };
}
```

---

## 任务 4：更新 roundtable_stop 并清理

**Files:**
- Modify: `src/server.ts`

- [ ] **Step 1: 更新 roundtable_stop 清理 chain 文件**

```typescript
if (name === 'roundtable_stop') {
  globalAbort.abort();
  globalAbort = new AbortController();
  try { fs.unlinkSync(CHAIN_FILE); } catch {}
  return { content: [{ type: 'text', text: '讨论已停止。' }] };
}
```

- [ ] **Step 2: 验证构建**

Run: `npm run build`
Expected: 编译成功

---

## 任务 5：测试完整流程

**Files:**
- 无

- [ ] **Step 1: 测试 roundtable_start**

调用 `roundtable_start`，topic="AI是否会取代白领工作"，rounds=2
Expected: 返回乐观者的发言

- [ ] **Step 2: 多次调用 roundtable_next**

连续调用 11 次 `roundtable_next`（6+6-1=11 次完整发言，加上轮次切换和结束提示）
Expected: 每次调用返回一条发言，立即显示在会话中

---

## 任务 6：提交

- [ ] **Step 1: 提交所有更改**

```bash
git add src/server.ts
git commit -m "refactor: 拆分为三个工具实现实时发言显示"
```
