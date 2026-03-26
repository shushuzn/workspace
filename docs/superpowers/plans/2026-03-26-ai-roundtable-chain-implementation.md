# AI 圆桌链条式上下文传递实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 重构 `ai-roundtable-mcp` MCP server，将并行发言改为链条式顺序发言，使后发言者能看到前面所有人的具体内容，实现真正的讨论。

**Architecture:** 保持单文件 MCP server 结构，改造 `roundtable_discuss` 工具，将 `Promise.all` 并行调用改为嵌套 for 循环顺序调用，每次调用前构建包含完整链条历史的 prompt。

**Tech Stack:** TypeScript, MCP SDK, undici fetch, MiniMax API

---

## 文件

- Modify: `src/server.ts` - 重构 roundtable_discuss 工具逻辑

---

## 任务 1：改造 callMinimax，移除 history 依赖

**Files:**
- Modify: `src/server.ts:33-74`

- [ ] **Step 1: 改造 callMinimax 函数签名**

将 `messages` 参数从 `history` 数组改为简单的消息内容字符串，移除 API 调用中不必要的 history 构建：

```typescript
async function callMinimax(
  systemPrompt: string,
  content: string,
  signal?: AbortSignal
): Promise<string> {
  const dispatcher = proxyUrl ? new ProxyAgent(proxyUrl) : undefined;

  const res = await fetch(API_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${API_KEY}`,
    },
    body: JSON.stringify({
      model: MODEL,
      max_tokens: 800,
      temperature: 0.2,
      system: systemPrompt,
      messages: [{ role: 'user', content }],
    }),
    signal,
    dispatcher,
  });

  if (!res.ok) {
    const err = (await res.json().catch(() => ({}))) as { base_resp?: { status_msg?: string } };
    throw new Error(err.base_resp?.status_msg || `HTTP ${res.status}`);
  }

  const data = (await res.json()) as {
    choices?: { message?: { content?: string; reasoning_content?: string } }[];
  };

  const msg = data.choices?.[0]?.message;
  const text = (msg?.content?.trim() || msg?.reasoning_content?.trim() || '').trim();
  if (!text) return '(无有效回答)';
  return text;
}
```

- [ ] **Step 2: 验证构建**

Run: `cd 80-PROJECTS/ai-roundtable-mcp && npm run build`
Expected: 编译成功，无错误

---

## 任务 2：重构 roundtable_discuss 实现链条式发言

**Files:**
- Modify: `src/server.ts:107-186`

- [ ] **Step 1: 重写 roundtable_discuss 工具核心逻辑**

将 Promise.all 并行调用改为嵌套 for 循环顺序调用，每次构建包含完整链条历史的 prompt：

```typescript
if (name === 'roundtable_discuss') {
  const topic = args?.topic as string;
  const rounds = Math.min(Math.max((args?.rounds as number) || 3, 1), 10);

  if (!topic?.trim()) {
    return { content: [{ type: 'text', text: '请提供讨论话题。' }], isError: true };
  }
  if (!API_KEY) {
    return { content: [{ type: 'text', text: '错误：未设置 MINIMAX_API_KEY' }], isError: true };
  }

  globalAbort.abort();
  globalAbort = new AbortController();
  const abortSignal = globalAbort.signal;

  // 发言链条：按时间顺序记录所有发言
  const chain: { persona: typeof personas[0]; text: string }[] = [];

  let output = `🔥 AI 圆桌讨论\n话题：${topic}\n轮数：${rounds}\n${'─'.repeat(50)}\n\n`;

  try {
    for (let round = 0; round < rounds; round++) {
      if (abortSignal.aborted) {
        return { content: [{ type: 'text', text: '讨论已中止。' }] };
      }

      output += `📍 第 ${round + 1} / ${rounds} 轮\n`;

      // 按顺序遍历每轮中的 6 个人格
      for (const persona of personas) {
        if (abortSignal.aborted) {
          return { content: [{ type: 'text', text: '讨论已中止。' }] };
        }

        // 构建之前所有发言的文本（链条历史）
        const priorStatements = chain.length > 0
          ? chain.map(e => `${e.persona.name}：${e.text}`).join('\n')
          : '（暂无）';

        // 完整的 system prompt
        const systemFull = `${persona.systemPrompt}\n\n重要：直接输出你的观点，不要使用括号、不要输出思考过程、不要输出引号、不要解释。只输出纯文本。`;

        // 用户消息 = 话题 + 链条历史
        const content = `话题：${topic}\n\n以下是之前的发言（按时间顺序）：\n${priorStatements}\n\n现在轮到 ${persona.name} 发言：`        try {
          const answer = await callMinimax(systemFull, content, abortSignal);
          chain.push({ persona, text: answer });
          output += `  ${persona.icon} ${persona.name}：${answer}\n`;
        } catch (err) {
          if (err instanceof Error && err.name === 'AbortError') {
            return { content: [{ type: 'text', text: '讨论已中止。' }] };
          }
          const errMsg = err instanceof Error ? err.message : String(err);
          chain.push({ persona, text: `⚠ ${errMsg}` });
          output += `  ${persona.icon} ${persona.name}：⚠ ${errMsg}\n`;
        }
      }

      output += '\n';
    }

    output += `${'─'.repeat(50)}\n✅ 讨论结束（共 ${rounds} 轮，共 ${chain.length} 条发言）`;
    return { content: [{ type: 'text', text: output }] };
  } catch (err) {
    return {
      content: [{
        type: 'text',
        text: `讨论出错：${err instanceof Error ? err.message : String(err)}`,
      }],
      isError: true,
    };
  }
}
```

- [ ] **Step 2: 验证构建**

Run: `cd 80-PROJECTS/ai-roundtable-mcp && npm run build`
Expected: 编译成功，无错误

- [ ] **Step 3: 测试运行**

Run: `cd 80-PROJECTS/ai-roundtable-mcp && node dist/server.js &`（后台运行）
然后用 MCP 客户端调用 `roundtable_discuss`，话题 "AI是否会取代白领工作"，rounds=1
Expected: 输出按链条顺序显示 6 个人格的发言，每条发言都能看到之前所有人的内容

---

## 任务 3：验证链条传递效果（可选，2轮测试）

**Files:**
- Modify: 无（仅测试）

- [ ] **Step 1: 测试 2 轮链条传递**

调用 `roundtable_discuss`，rounds=2
Expected:
- 第 2 轮每个人格的发言中能体现出对第 1 轮具体内容的回应
- 例如乐观者第 2 轮会回应怀疑者/分析师/历史家等第 1 轮的具体观点

---

## 任务 4：更新工具描述

**Files:**
- Modify: `src/server.ts:86-98`

- [ ] **Step 1: 更新 roundtable_discuss 描述**

将 `description` 字段从 `6种人格并行发言` 改为准确描述链条式发言：

```typescript
name: 'roundtable_discuss',
description: '开始 AI 圆桌讨论。6种人格按顺序发言，后发言者能看到前面所有人的具体内容，形成真正的讨论。',
```

- [ ] **Step 2: 验证构建并提交**

Run: `npm run build && git add src/server.ts && git commit -m "feat: 改并行发言为链条式顺序发言，实现真正讨论"`
