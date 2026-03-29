# AI 圆桌发言长度控制实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 强制控制每个人格发言在 2 句以内，输出简洁观点而非长篇分析。

**Architecture:** 通过强化 system prompt + 添加 `max_tokens` 上限 + 添加输出格式约束三重保险，确保模型输出简短。

**Tech Stack:** TypeScript, MiniMax API, Prompt Engineering

---

## 背景问题

当前模型输出过长，输出了完整的 Markdown 分析报告而非 2 句短观点。原因：模型倾向于展开论述，"说话要短，2句以内" 的约束不够强。

---

## 文件

- Modify: `src/server.ts` - 所有人格 systemPrompt 及 callMinimax 参数

---

## 任务 1：强化人格 systemPrompt，添加严格格式约束

**Files:**
- Modify: `src/server.ts:17-30`

- [ ] **Step 1: 强化所有 6 个人格的 systemPrompt**

在每个 persona 的 systemPrompt 末尾添加严格的格式要求：

```typescript
const personas = [
  { id: 'optimist', name: '乐观者', icon: '🔥',
    systemPrompt: `你正在一个圆桌讨论现场。轮到你发言，你必须立刻开口说出自己的观点，不能有任何内心独白或思考过程。

格式要求（必须严格遵守）：
- 严格控制在2句话以内
- 每句话不超过25个字
- 禁止使用Markdown格式（不要标题、列表、表格等）
- 禁止使用括号、破折号以外的标点
- 结尾必须有一个你亲眼见过或读过的真实例子

示例格式：
"AI会创造新岗位，就像工业革命纺织机取代人工但创造了检修工一样。身边就有朋友转行做了AI训练师。"` },
  // 其他5个人格类似处理...
];
```

- [ ] **Step 2: 验证构建**

Run: `cd 80-PROJECTS/ai-roundtable-mcp && npm run build`
Expected: 编译成功

---

## 任务 2：限制 API max_tokens 从 800 降到 150

**Files:**
- Modify: `src/server.ts:46`

- [ ] **Step 1: 降低 max_tokens 上限**

150 tokens ≈ 75-100 个中文字符，约 2-3 句话的空间，但不足以输出长篇分析：

```typescript
max_tokens: 150,  // 从 800 降到 150，强制简短回答
```

- [ ] **Step 2: 验证构建**

Run: `npm run build`
Expected: 编译成功

---

## 任务 3：测试验证

**Files:**
- 无（仅测试）

- [ ] **Step 1: 测试 1 轮讨论，验证输出简短**

调用 `roundtable_discuss`，topic="AI是否会取代白领工作"，rounds=1
验证：每条发言应在 50-100 字以内，不再是完整 Markdown 报告

- [ ] **Step 2: 测试 2 轮讨论，验证链条传递**

调用 rounds=2，验证第 2 轮发言能体现对第 1 轮内容的回应

---

## 任务 4：提交

**Files:**
- Modify: `src/server.ts`

- [ ] **Step 1: 提交所有更改**

```bash
git add src/server.ts
git commit -m "fix: 强制发言长度2句以内，添加格式约束和max_tokens限制"
```
