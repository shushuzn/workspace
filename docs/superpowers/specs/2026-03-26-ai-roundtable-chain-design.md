# AI 圆桌讨论 - 链条式上下文传递设计

## 概述

重新设计 `ai-roundtable-mcp` MCP tool，实现真正的"圆桌讨论"——每个人格按顺序发言，后发言者能看到前面所有人的具体内容，形成观点碰撞和回应。

## 问题

当前 MCP 实现中，6 个人格在同一轮内并行调用，互相不知道对方说了什么，只是把回答拼接在一起。这不是真正的讨论，而是"广播"。

## 核心设计

### 发言链条（Chain）

维护一个发言序列 `chain`，每个人格的发言按时间顺序排列：

```
chain = [A1, S1, P1, H1, Hi1, Pr1, A2, S2, P2, H2, Hi2, Pr2, A3, S3, ...]
```

每个人格发言时，看到的是：
1. 原始话题
2. `chain` 中排在**当前人格之前**的所有发言

### 发言顺序

每轮内按固定顺序：乐观者 → 怀疑者 → 分析师 → 调和者 → 历史家 → 务实者

### 发言人格模板

```typescript
const personas = [
  { id: 'optimist',   name: '乐观者', icon: '🔥', systemPrompt: '...' },
  { id: 'skeptic',    name: '怀疑者', icon: '🧊', systemPrompt: '...' },
  { id: 'analyst',    name: '分析师', icon: '🔬', systemPrompt: '...' },
  { id: 'harmonizer', name: '调和者', icon: '🌱', systemPrompt: '...' },
  { id: 'historian',  name: '历史家', icon: '📜', systemPrompt: '...' },
  { id: 'pragmatist', name: '务实者', icon: '⚙️', systemPrompt: '...' },
];
```

### 单次发言的 prompt 构建

人格 X 第 N 轮发言时，prompt =：

```
{persona.systemPrompt}

重要：直接输出你的观点，不要使用括号、不要输出思考过程、不要输出引号、不要解释。只输出纯文本。

话题：{topic}

以下是之前的发言（按时间顺序）：
{chain 中所有在人格 X 之前的发言，格式为 "人格名：内容"}

现在轮到 {persona.name} 发言：
```

### MiniMax API 调用

- Endpoint: `https://api.minimaxi.com/v1/text/chatcompletion_v2`
- Header: `Authorization: Bearer {API_KEY}`
- Body: `model: MiniMax-M2.7-highspeed`, `max_tokens: 800`, `temperature: 0.2`
- response: 从 `choices[0].message.content` 提取，fallback 到 `reasoning_content`

### API 响应字段

```typescript
{
  topic: string,           // 讨论话题
  rounds: number,          // 轮数（默认3）
}
```

### 流程

```
roundtable_discuss(topic, rounds):
  chain = []
  history = [{ role: 'user', content: `话题：${topic}` }]

  for round in 1..rounds:
    for persona in [乐观者, 怀疑者, 分析师, 调和者, 历史家, 务实者]:
      # 构建发言上下文
      priorStatements = chain.map(e => `${e.persona.name}：${e.text}`).join('\n')
      systemPrompt = 构建prompt(persona, topic, priorStatements)

      # 调用 MiniMax
      response = await callMinimax(systemPrompt, history)

      # 加入链条和历史
      chain.push({ persona, text: response })
      history.push({ role: 'assistant', content: response })

  # 输出结果
  return formatOutput(topic, rounds, chain)
```

### 输出格式

```
🔥 AI 圆桌讨论
话题：{topic}
轮数：{rounds}
──────────────────────────────────────────────────

📍 第 1 / 3 轮

  🔥 乐观者：{A1}
  🧊 怀疑者：{S1}
  🔬 分析师：{P1}
  🌱 调和者：{H1}
  📜 历史家：{Hi1}
  ⚙️ 务实者：{Pr1}

📍 第 2 / 3 轮

  🔥 乐观者：{A2}（基于 S1/P1/H1/Hi1/Pr1 的具体内容）
  🧊 怀疑者：{S2}（基于 A2/P1/H1/Hi1/Pr1）
  ...

──────────────────────────────────────────────────
✅ 讨论结束
```

### 工具接口

```
name: roundtable_discuss
inputSchema: {
  type: 'object',
  properties: {
    topic: { type: 'string', description: '讨论话题' },
    rounds: { type: 'number', description: '轮数', default: 3, minimum: 1, maximum: 10 }
  },
  required: ['topic']
}
```

### 停止机制

`roundtable_stop` 中断当前的发言链条，抛出 AbortError。

### 错误处理

- MiniMax 返回错误 → 该人格输出 `⚠ {错误信息}`，继续下一个
- 中止信号 → 停止并返回已收集的内容

## 性能

串行执行，每轮 6 人 × N 轮 = 6N 次 MiniMax 调用。
- 每次调用约 3-6 秒
- 3 轮约 54-108 秒
- 受 MiniMax 模型响应速度限制

## 文件

- `src/server.ts` - MCP server 实现
