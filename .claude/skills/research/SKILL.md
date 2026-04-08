---
name: "research"
description: "Monitor AI/Agent tech news and generate inspiration. Use when user says 研究/继续研究."
---

# Research

触发自动研究循环，监测 AI/Agent/LLM/MCP 科技热点，生成灵感。

## When To Use

- User says: "研究", "继续研究"

## 执行

```bash
node "D:/OpenClaw/workspace/80-PROJECTS/auto-research-loop.js"
```

可选 — 头脑风暴模式（每30分钟）：

```bash
node "D:/OpenClaw/workspace/80-PROJECTS/auto-brainstorm-loop.js"
```

## 停止

```
Ctrl+C
```

## 说明

- 监测 36kr 科技频道关键词：AI, Agent, Claude, GPT, 模型, OpenAI, Anthropic, 语音
- 结果保存在 `D:\OpenClaw\workspace\logs\auto-research\`
