# Workspace API Reference

> Auto-generated on 2026-04-05

## Capability Map

| Project | Description | Key Files |
|---------|-------------|------------|
| [50-ton-hackathon-2026](#50-ton-hackathon-2026) | 项目描述暂无 | `` |
| [a2a-router](#a2a-router) | Agent-to-Agent Communication Router — MCP Server 实现，支持多协议、多能力注册、智能路由。 | `protocols/acp-adapter.js, protocols/acp-gateway.js, protocols/acp-parser.js, protocols/capability-registry.js, protocols/load-balancing/load-balancer.js...` |
| [agent-arena](#agent-arena) | AI Agent 养成竞技游戏。 | `game/agentFactory.js, game/constants.js, game/core.js, game/tournament.js, main.js...` |
| [agent-registry](#agent-registry) | > Service registry and discovery for AI agents — like Eureka/Consul, but built for AI. | `discovery-server.js, index.js, mcp-server.js` |
| [claude-code-main](#claude-code-main) | > The primary `src/` tree in this repository is now dedicated to **Python porting work**. The March 31, 2026 Claude Code source exposure is part of the project's background, but the tracked repository is now centered on Python source rather than the exposed TypeScript snapshot. | `addCommand/__init__.py, addCommand/__main__.py, advisor/__init__.py, assistant/__init__.py, bootstrap/__init__.py...` |
| [code-agent](#code-agent) | Code Intelligence Agent - Semgrep + Tree-sitter 代码分析。 | `agent.js, analyzer/semgrepWrapper.js, server.js` |
| [conceptual-distance-explorer](#conceptual-distance-explorer) | A project for conceptual-distance-explorer | `cli.ts, distance.ts, embed.ts, explorer.ts, main.ts...` |
| [idle-empire](#idle-empire) | (no description) | `aiAdvisor.js, gameAdapter.js, main.js, stores/gameStore.js` |
| [knowledge-bridge](#knowledge-bridge) | 项目描述暂无 | `api-server.mjs, importers/github-issues.ts` |
| [material-price-tracker](#material-price-tracker) | > material-price-tracker | `` |
| [multi-agent-discuss](#multi-agent-discuss) | 项目描述暂无 | `` |
| [multi-agent-hub](#multi-agent-hub) | 多人格 AI 圆桌讨论 CLI，通过动态温度调度探索观点多样性。 | `protocol/oap.ts` |
| [news-workflow-engine](#news-workflow-engine) | (no description) | `news_workflow/analyzer/analyzer.py, news_workflow/analyzer/__init__.py, news_workflow/api/openai_compat.py, news_workflow/api/__init__.py, news_workflow/core/engine.py...` |
| [NewsHub](#newshub) | 新闻聚合与智能推送平台 | `mcp_server.py` |
| [openclaw-dashboard](#openclaw-dashboard) | OpenClaw Workstation Dashboard — A Self-Evolving Workspace Optimizer | `config/default.mjs, core/agent.mjs, core/meta-cognizer.mjs, core/tool-router.mjs, core/working-memory.mjs...` |
| [opencli](#opencli) | (no description) | `analysis.ts, browser/base-page.ts, browser/bridge.ts, browser/cdp.test.ts, browser/cdp.ts...` |
| [openviking-mcp](#openviking-mcp) | Context database MCP server for AI agents, providing cross-project knowledge sharing, session persistence, and context retrieval. | `server.py, tools/context.py, tools/resources.py, tools/session.py, tools/__init__.py...` |
| [pla-degradation-research](#pla-degradation-research) | 项目描述暂无 | `` |
| [public-apis](#public-apis) | (no description) | `` |
| [quadratic-algebra-fibonacci](#quadratic-algebra-fibonacci) | 二次代数与斐波那契数研究 - 验证 Marco Mantovanelli 的论文 arxiv.org/abs/2603.19343v1。 | `` |
| [rl-trading](#rl-trading) | > rl-trading | `` |
| [self-evolving-orchestrator](#self-evolving-orchestrator) | A Go-based task orchestration system that self-evolves its decomposition strategy based on execution outcomes. Uses a strategy pool, scoring feedback loop, and overlap detection to refine task decomposition. | `` |
| [star-forge-web](#star-forge-web) | ![Version](https://img.shields.io/badge/version-1.0.0-blue) | `data/achievements.js, data/buildings.js, data/quests.js, data/seasonConfig.js, data/upgrades.js...` |
| [stock-analysis-agent](#stock-analysis-agent) | ReAct-based AI agent for stock market analysis. Takes natural language queries and produces comprehensive investment analysis reports. | `agent.py, agent_tools.py, api.py, cli.py, debate.py...` |
| [task-orchestrator](#task-orchestrator) | Chain opencli (browser) + CLI-Anything (software) via a rule-based task planner. | `adapters/adapter-sandbox.ts, adapters/cli-anything.ts, adapters/index.ts, adapters/multi-agent-hub.ts, adapters/opencli.ts...` |

---

## 50-ton-hackathon-2026

**项目描述暂无**

```
cd 80-PROJECTS/50-ton-hackathon-2026
```

### README Excerpt

```markdown
# 50-ton-hackathon-2026

项目描述暂无

## 项目信息

- **版本**: 0.0.1
- **路径**: D:\OpenClaw\workspace\80-PROJECTS\50-ton-hackathon-2026

## 快速开始

```bash
# 安装依赖
npm install

# 启动开发
npm run dev
```

## 项目结构

```
50-ton-hackathon-2026/
├── src/          # 源代码
├── README.md     # 本文档
└── package.json  # 项目配置
```

```

---

## a2a-router

**Agent-to-Agent Communication Router — MCP Server 实现，支持多协议、多能力注册、智能路由。**

```
cd 80-PROJECTS/a2a-router
```

### README Excerpt

```markdown
# a2a-router

Agent-to-Agent Communication Router — MCP Server 实现，支持多协议、多能力注册、智能路由。

## 技术栈

- JavaScript/TypeScript (ES Module)
- Node.js
- @modelcontextprotocol/sdk ^1.0.0
- better-sqlite3 ^12.8.0
- vitest (测试)

## 开始使用

```bash
npm install
npm start
```

## 核心能力

### Agent 注册与发现

```javascript
router.registerAgent('agent-id', ['coding', 'reasoning'], { version: '1.0' });
router.discoverAgents({ capabilities: ['coding'] });
```

### Capability 路由

根据 capability 匹配最佳 agent：

```javascript
// Agent 注册时声明 capabilities
router.registerAgent('coding-agent', ['coding', 'review']);

// 路由时查找匹配 agent
const match = router.capabilityRegistry.match('code');
```

### 任务队列

支持 CRITICAL / HIGH / NORMAL / LOW 四级优先级：

```javascript
router.enqueue('agent-id', task, 'HIGH');
```

### LangChain Agent（实验性）


```

### API Sections

**protocols/acp-adapter.js**

```
{Map<string, string>} ACP ID -> Internal ID */
```

**protocols/acp-adapter.js**

```
{Object} acpAgent - ACP agent info; {string} acpAgent.id - ACP agent ID; {string[]} acpAgent.capabilities - Agent capabi
```

**protocols/acp-adapter.js**

```
{string} agentId - Internal agent ID; {string} status - Agent status; {number} load - Current load (0-1); {number} activ
```

**protocols/acp-adapter.js**

```
{string} acpId - ACP agent ID; {string} - Internal agent ID
```

**protocols/acp-gateway.js**

```
{Object} router - A2A Router instance; {Object} options - Gateway options
```

### Source Files

- `protocols/acp-adapter.js`
- `protocols/acp-gateway.js`
- `protocols/acp-parser.js`
- `protocols/capability-registry.js`
- `protocols/load-balancing/load-balancer.js`
- `protocols/mcp/python-mcp-client.js`
- `protocols/mcp/stock-analysis-adapter.js`
- `protocols/monitoring/queue-monitor.js`
- `protocols/orchestration/dify-adapter.js`
- `protocols/orchestration/langchain-adapter.js`

---

## agent-arena

**AI Agent 养成竞技游戏。**

```
cd 80-PROJECTS/agent-arena
```

### README Excerpt

```markdown
# agent-arena

AI Agent 养成竞技游戏。

## 技术栈

- Svelte 5
- Vite 5

## 开始使用

```bash
npm install
npm run dev
```

```

### API Sections

**game/tournament.js**

```
[newRatingA, newRatingB]
```

**shared/identityStore.js**

```
{CrossProjectIdentity[]}
```

**shared/identityStore.js**

```
{CrossProjectIdentity[]}
```

**shared/identityStore.js**

```
{object} agent - Agent object from agent-arena (must have id, name, backstory, rarity, avatar); {CrossProjectIdentity}
```

**shared/identityStore.js**

```
{string} agentId
```

### Source Files

- `game/agentFactory.js`
- `game/constants.js`
- `game/core.js`
- `game/tournament.js`
- `main.js`
- `services/aiOpponentService.js`
- `shared/identityStore.js`
- `stores/arenaStore.js`
- `stores/game.js`
- `stores/gameStore.js`

---

## agent-registry

**> Service registry and discovery for AI agents — like Eureka/Consul, but built for AI.**

```
cd 80-PROJECTS/agent-registry
```

### README Excerpt

```markdown
# Agent Registry

> Service registry and discovery for AI agents — like Eureka/Consul, but built for AI.

## Features

- **Registration**: Agents register with name, capabilities, and tags
- **Discovery**: Find agents by capability (e.g. `text-generation`, `mcp-tools`)
- **Heartbeat**: Keep agents alive with periodic pings
- **Health monitoring**: Auto-expire stale agents
- **REST API**: HTTP server for programmatic access
- **CLI**: Simple commands for humans

## Quick Start

```bash
# Register an agent
node src/index.js register my-agent text-generation openai local

# List all agents
node src/index.js list

# Discover agents by capability
node src/index.js discover text-generation openai

# Send heartbeat (keep alive)
node src/index.js heartbeat <agentId>

# Start REST API server
node s
```

### API Sections

**index.js**

```
{Map<string, AgentEntry>} */
```

**mcp-server.js**

```
{AgentEntry[]} */
```

### Source Files

- `discovery-server.js`
- `index.js`
- `mcp-server.js`

---

## claude-code-main

**> The primary `src/` tree in this repository is now dedicated to **Python porting work**. The March 31, 2026 Claude Code source exposure is part of the project's background, but the tracked repository is now centered on Python source rather than the exposed TypeScript snapshot.**

```
cd 80-PROJECTS/claude-code-main
```

### README Excerpt

```markdown
# Claude Code Python Porting Workspace

> The primary `src/` tree in this repository is now dedicated to **Python porting work**. The March 31, 2026 Claude Code source exposure is part of the project's background, but the tracked repository is now centered on Python source rather than the exposed TypeScript snapshot.

---

## Porting Status

The main source tree is now Python-first.

- `src/` contains the active Python porting workspace
- `tests/` verifies the current Python workspace
- the exposed snapshot is no longer part of the tracked repository state

The current Python workspace is not yet a complete one-to-one replacement for the original system, but the primary implementation surface is now Python.

## Why this rewrite exists

I originally studied the exposed codebase to understan
```

### Source Files

- `addCommand/__init__.py`
- `addCommand/__main__.py`
- `advisor/__init__.py`
- `assistant/__init__.py`
- `bootstrap/__init__.py`
- `bridge/__init__.py`
- `bridge_kick/__init__.py`
- `bridge_kick/__main__.py`
- `brief/__init__.py`
- `brief/__main__.py`

---

## code-agent

**Code Intelligence Agent - Semgrep + Tree-sitter 代码分析。**

```
cd 80-PROJECTS/code-agent
```

### README Excerpt

```markdown
# code-agent

Code Intelligence Agent - Semgrep + Tree-sitter 代码分析。

## 技术栈

- JavaScript/TypeScript
- Node.js
- @modelcontextprotocol/sdk ^1.0.0
- tree-sitter (JavaScript, TypeScript, Python)
- uuid, yaml

## 开始使用

```bash
npm install
npm start
```

```

### Source Files

- `agent.js`
- `analyzer/semgrepWrapper.js`
- `server.js`

---

## conceptual-distance-explorer

**A project for conceptual-distance-explorer**

```
cd 80-PROJECTS/conceptual-distance-explorer
```

### README Excerpt

```markdown
# conceptual-distance-explorer

A project for conceptual-distance-explorer

## Install

```bash
npm install
```

## Usage

```bash
npm run dev
```

## License

MIT

```

### API Sections

**Usage**

```
```bash
npm run dev
```
```

### Source Files

- `cli.ts`
- `distance.ts`
- `embed.ts`
- `explorer.ts`
- `main.ts`
- `types.ts`

---

## idle-empire


```
cd 80-PROJECTS/idle-empire
```

### README Excerpt

```markdown
# 🏰 Idle Empire v2.0 - Evolution Edition

**Premium挂机放置游戏 - 进化版**

---


## 安装

```bash
npm install
```

## ✨ 新功能亮点

| 功能 | 描述 |
|------|------|
| ⌨️ **键盘快捷键** | 1-5切换标签, 空格点击, S保存 |
| 🎯 **进度条** | 实时显示下一个建筑达成进度 |
| 💫 **涟漪效果** | 点击金币时的水波扩散效果 |
| ✨ **粒子爆发** | 点击时喷射出金色小粒子 |
| 🔢 **数字动画** | 数值变化时的弹跳动画 |
| 📊 **Stagger动画** | 卡片入场时的交错动画 |
| 🎬 **徽章动画** | 成就解锁时的脉冲效果 |
| 🌟 **流光效果** | 进度条的流光扫过动画 |
| 🎲 **随机事件** | 随机触发的特殊事件和奖励 |
| 📅 **每日任务** | 每日更新的任务系统 |
| 📦 **收藏品系统** | 收集稀有物品获得永久加成 |
| 🏆 **里程碑系统** | 达成长期目标获得永久奖励 |
| ⚡ **性能优化** | 游戏运行更加流畅 |

---

## 🎮 核心功能

### 建筑系统 (12种)
```
⛏️ 金矿 → 🪓 伐木场 → 🌾 农场 → 🏭 工厂 → 🏦 银行 → 🏰 城堡 → 🛕 神殿 → 🚀 太空站 → ⚛️ 量子实验室 → ☀️ 戴森环 → ⏰ 时间机器 → 🌀 多元宇宙门户
```

### Boss系统 (7个)
```
👺 哥布林 → 🧌 巨魔 → 🐉 巨龙 → 👿 恶魔 → 👽 泰坦 → 🌌 虚空领主 → 🤖
```

### Source Files

- `aiAdvisor.js`
- `gameAdapter.js`
- `main.js`
- `stores/gameStore.js`

---

## knowledge-bridge

**项目描述暂无**

```
cd 80-PROJECTS/knowledge-bridge
```

### README Excerpt

```markdown
# knowledge-bridge

项目描述暂无

## 项目信息

- **版本**: 1.0.0
- **路径**: D:\OpenClaw\workspace\80-PROJECTS\knowledge-bridge

## 快速开始

```bash
# 安装依赖
npm install

# 启动开发
npm run dev
```

## 项目结构

```
knowledge-bridge/
├── src/          # 源代码
├── README.md     # 本文档
└── package.json  # 项目配置
```

```

### Source Files

- `api-server.mjs`
- `importers/github-issues.ts`

---

## material-price-tracker

**> material-price-tracker**

```
cd 80-PROJECTS/material-price-tracker
```

### README Excerpt

```markdown
# 原料期货监控 - PE/PP/PVC期货+采购价实时监控网页

> material-price-tracker

## 简介

暂无。

```

---

## multi-agent-discuss

**项目描述暂无**

```
cd 80-PROJECTS/multi-agent-discuss
```

### README Excerpt

```markdown
# multi-agent-discuss

项目描述暂无

## 项目信息

- **路径**: D:\OpenClaw\workspace\80-PROJECTS\multi-agent-discuss

## 快速开始

```bash
npm install
npm run dev
```

```

---

## multi-agent-hub

**多人格 AI 圆桌讨论 CLI，通过动态温度调度探索观点多样性。**

```
cd 80-PROJECTS/multi-agent-hub
```

### README Excerpt

```markdown
# AI 圆桌讨论 — Cognitive Annealing 版

多人格 AI 圆桌讨论 CLI，通过动态温度调度探索观点多样性。

## 特性

- **6 人格圆桌**：乐观者、怀疑者、分析师、调和者、历史家、务实者
- **自适应温度调度**：模拟退火算法，动态调整 LLM 采样温度
- **概念跳跃测量**：ΔS = cosineDistance( roundMean*t, roundMean*{t-1} )
- **早停机制**：连续 4 轮 ΔS < 0.05 时自动结束
- **Ollama 本地嵌入**：MiniMax 余额不足时自动降级

## 快速开始

```bash
# 安装依赖
npm install

# 运行讨论（交互模式）
node index.js

# 命令行模式
node index.js "AI是否会取代人类工作"
node index.js "气候变化" -r 6 -t 1.0

# 查看帮助
node index.js --help
```

## 命令行选项

| 选项               | 默认值 | 说明                 |
| ------------------ | ------ | -------------------- |
| `-r, --rounds <N>` | 8      | 讨论轮数（最大 10）  |
| `-t, --temp <T>`   | 1.2    | 初始温度（最大 2.0） |
| `-h, --help`       | —      | 显示帮助             |

## 温度调度

- 初始温度：1.2
- 冷却率：0.88（每轮乘以 0.88）
- 最低温度：0.3
- ΔS 峰值检测：超过阈值时进入 plateau（温度不变 2 轮）

```

### Source Files

- `protocol/oap.ts`

---

## news-workflow-engine


```
cd 80-PROJECTS/news-workflow-engine
```

### README Excerpt

```markdown
# News Workflow Engine

**智能新闻工作流引擎** - 整合 NewsHub + agentic-bpm + patrol-agent

## ✨ 特性

| 特性 | 描述 |
|------|------|
| 📰 **自动抓取** | 多源新闻定时抓取 |
| 🧠 **智能分析** | AI 分析重要性、分类、情感 |
| 🔗 **工作流触发** | 基于新闻自动创建任务 |
| 🤖 **自动执行** | patrol-agent 执行任务 |
| 📊 **反馈闭环** | 结果分析优化模型 |
| 📬 **多渠道推送** | 飞书、Telegram、邮件等 |

## 🏗️ 架构

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  NewsHub    │───►│ agentic-bpm │───►│patrol-agent │
│ (信息获取)   │    │ (工作流编排) │    │ (任务执行)  │
└─────────────┘    └─────────────┘    └─────────────┘
         │                  │                  │
         ▼                  ▼                  ▼
┌────────────────────────────────────────────────────┐
│              统一数据库 (SQLite)                    │
└──────────────────────────────────────────
```

### Source Files

- `news_workflow/analyzer/analyzer.py`
- `news_workflow/analyzer/__init__.py`
- `news_workflow/api/openai_compat.py`
- `news_workflow/api/__init__.py`
- `news_workflow/core/engine.py`
- `news_workflow/core/__init__.py`
- `news_workflow/executor/runner.py`
- `news_workflow/executor/__init__.py`
- `news_workflow/feedback/loop.py`
- `news_workflow/feedback/__init__.py`

---

## NewsHub

**新闻聚合与智能推送平台**

```
cd 80-PROJECTS/NewsHub
```

### README Excerpt

```markdown
# NewsHub

新闻聚合与智能推送平台

## 功能特性

- **多源抓取**: 新浪财经、华尔街日报、36氪、虎嗅、TechCrunch 等 7+ 新闻源
- **智能分析**: 自动分类、情感分析、重要性评分
- **多渠道推送**: 飞书、Telegram、微信、Discord、Slack、邮件、QQ
- **热点检测**: 自动识别热门话题
- **AI 增强**: 支持 Ollama 本地模型进行新闻摘要

## 快速开始

```bash
# 抓取新闻
python news_hub.py fetch

# 推送到飞书
python news_hub.py feishu digest

# 查看热点
python news_hub.py hot

# 启动定时任务
start_scheduler.bat
```

## 项目结构

```
NewsHub/
├── core/               # 核心模块
│   ├── async_fetcher.py    # 异步抓取
│   ├── database.py         # 数据库操作
│   ├── shared.py           # 共享工具
│   └── config_manager.py   # 配置管理
├── analyze/            # 分析模块
│   ├── news_processor.py   # 新闻处理
│   ├── hot_topics.py       # 热点检测
│   └── ai_summarizer.py    # AI 摘要
├── push/               # 推送模块
│   ├── news_feishu.py      # 飞书推送
│   ├── news_telegram.py    # T
```

### Source Files

- `mcp_server.py`

---

## openclaw-dashboard

**OpenClaw Workstation Dashboard — A Self-Evolving Workspace Optimizer**

```
cd 80-PROJECTS/openclaw-dashboard
```

### README Excerpt

```markdown
# openclaw-dashboard

OpenClaw Workstation Dashboard — A Self-Evolving Workspace Optimizer

## 概述

本项目包含**两个独立的子系统**，共享同一repo：

### 子系统1：Workspace Dashboard（监控）

读取workspace下所有项目的git状态，生成可视化dashboard。

```
dashboard-server.js        # HTTP服务器（端口8000）
dashboard.html            # Dashboard前端
generate-dashboard-data.js # 扫描workspace所有项目，输出dashboard-data.json
```

- **数据源**: `dashboard-data.json`（由generate-dashboard-data.js生成）
- **监控范围**: 整个workspace下的所有项目

### 子系统2：Self-Evolution Loop（优化）

基于强化学习的自我优化系统，使用ε-greedy算法探索有效操作，通过元认知分析发现能力缺口，governance层约束预算、安全与回滚。

- **入口**: `node self-evolving-loop.mjs [--status|--analyze]`
- **核心**: `src/`下的多模块系统

## 快速开始

```bash
npm install
npm run generate   # 先生成dashboard数据（需在start前运行）
npm run start      # 启动dashboard服务器（端口8000）
npm run test        # 运行单元测试
n
```

### API Sections

**core/meta-cognizer.mjs**

```
{Promise<Array>} List of identified gaps with priority
```

**governance/safety.mjs**

```
{Object} operation - The operation to check; {Object} { approved: boolean, reason: string }
```

**learn/distiller.mjs**

```
{Object} Summary of what was distilled
```

**operations/productive-ops.mjs**

```
{string} projectName
```

**operations/productive-ops.mjs**

```
{string} projectName
```

### Source Files

- `config/default.mjs`
- `core/agent.mjs`
- `core/meta-cognizer.mjs`
- `core/tool-router.mjs`
- `core/working-memory.mjs`
- `evolution/hypothesis.mjs`
- `evolution/population.mjs`
- `evolution/sandbox.mjs`
- `governance/audit.mjs`
- `governance/budget.mjs`

---

## opencli


```
cd 80-PROJECTS/opencli
```

### README Excerpt

```markdown
# OpenCLI

> **Make any website, Electron App, or Local Tool your CLI.**
> Zero risk · Reuse Chrome/Chromium login · AI-powered discovery · Universal CLI Hub

[![中文文档](https://img.shields.io/badge/docs-%E4%B8%AD%E6%96%87-0F766E?style=flat-square)](./README.zh-CN.md)
[![npm](https://img.shields.io/npm/v/@jackwener/opencli?style=flat-square)](https://www.npmjs.com/package/@jackwener/opencli)
[![Node.js Version](https://img.shields.io/node/v/@jackwener/opencli?style=flat-square)](https://nodejs.org)
[![License](https://img.shields.io/npm/l/@jackwener/opencli?style=flat-square)](./LICENSE)

A CLI tool that turns **any website**, **Electron app**, or **local CLI tool** into a command-line interface — Bilibili, Zhihu, 小红书, Twitter/X, Reddit, YouTube, Antigravity, `gh`, `docker`, and [m
```

### API Sections

**clis/douyin/_shared/imagex-upload.ts**

```
imagePath - Local file path to the image (JPEG/PNG/etc.); uploadInfo - Upload URL and store_uri from the apply cover upl
```

**clis/douyin/_shared/tos-upload.ts**

```
— for testing only */
```

**clis/douyin/_shared/transcode.ts**

```
page - Browser page for making credentialed API calls; videoId - The video_id returned from the confirm upload step; tim
```

**clis/ones/task.ts**

```
https://docs.ones.cn/project/open-api-doc/project/task.html
```

**clis/pixiv/utils.ts**

```
page  - Browser page instance; path  - API path, e.g. '/ajax/illust/12345'; opts  - Optional query params; - The parsed 
```

### Source Files

- `analysis.ts`
- `browser/base-page.ts`
- `browser/bridge.ts`
- `browser/cdp.test.ts`
- `browser/cdp.ts`
- `browser/daemon-client.test.ts`
- `browser/daemon-client.ts`
- `browser/discover.ts`
- `browser/dom-helpers.test.ts`
- `browser/dom-helpers.ts`

---

## openviking-mcp

**Context database MCP server for AI agents, providing cross-project knowledge sharing, session persistence, and context retrieval.**

```
cd 80-PROJECTS/openviking-mcp
```

### README Excerpt

```markdown
# OpenViking MCP Server

Context database MCP server for AI agents, providing cross-project knowledge sharing, session persistence, and context retrieval.

## Features

- **Session Management**: Create, persist, and recover conversation sessions
- **Tiered Context**: L0 (abstract), L1 (overview), L2 (full) context loading
- **Semantic Search**: Search across all stored context
- **Resource Tree**: Hierarchical view of knowledge base
- **Relation Links**: Connect related contexts

## Installation

```bash
cd 80-PROJECTS/openviking-mcp
pip install -e .
```

## Configuration

Add to Claude Code settings (`~/.claude/settings.json`):

```json
{
  "mcpServers": {
    "openviking": {
      "command": "py",
      "args": ["D:/OpenClaw/workspace/80-PROJECTS/openviking-mcp/src/server.py"]
    }
  }

```

### Source Files

- `server.py`
- `tools/context.py`
- `tools/resources.py`
- `tools/session.py`
- `tools/__init__.py`
- `__init__.py`

---

## pla-degradation-research

**项目描述暂无**

```
cd 80-PROJECTS/pla-degradation-research
```

### README Excerpt

```markdown
# pla-degradation-research

项目描述暂无

## 项目信息

- **版本**: 1.0.0
- **路径**: D:\OpenClaw\workspace\80-PROJECTS\pla-degradation-research

## 快速开始

```bash
# 安装依赖
npm install

# 启动开发
npm run dev
```

## 项目结构

```
pla-degradation-research/
├── src/          # 源代码
├── README.md     # 本文档
└── package.json  # 项目配置
```

```

---

## public-apis


```
cd 80-PROJECTS/public-apis
```

### README Excerpt

```markdown
# Try Public APIs for free
The Public APIs repository is manually curated by community members like you and folks working at [APILayer](https://apilayer.com/?utm_source=Github&utm_medium=Referral&utm_campaign=Public-apis-repo). It includes an extensive list of public APIs from many domains that you can use for your own products. Consider it a treasure trove of APIs well-managed by the community over the years.

<br >

<p>
    <a href="https://apilayer.com">
        <div>
            <img src=".github/cs1586-APILayerLogoUpdate2022-LJ_v2-HighRes.png" width="100%" alt="APILayer Logo" />
        </div>
    </a>
  </p>

APILayer is the fastest way to integrate APIs into any product. Explore [APILayer APIs](https://apilayer.com/products/?utm_source=Github&utm_medium=Referral&utm_cam
```

### API Sections

**APILayer APIs**

```
| API | Description | Call this API |
|:---|:---|:---|
| [IPstack](https://ipstack.com/?utm_source=Github&utm_medium=Referral&utm_campaign=Public-apis-repo-Best-sellers) | Locate and Identify Websit
```

---

## quadratic-algebra-fibonacci

**二次代数与斐波那契数研究 - 验证 Marco Mantovanelli 的论文 arxiv.org/abs/2603.19343v1。**

```
cd 80-PROJECTS/quadratic-algebra-fibonacci
```

### README Excerpt

```markdown
# quadratic-algebra-fibonacci

二次代数与斐波那契数研究 - 验证 Marco Mantovanelli 的论文 arxiv.org/abs/2603.19343v1。

## 技术栈

- Python 3

## 开始使用

```bash
python verify.py
```

```

---

## rl-trading

**> rl-trading**

```
cd 80-PROJECTS/rl-trading
```

### README Excerpt

```markdown
# rl-trading

> rl-trading


## 安装

```bash
npm install
```

## 简介

暂无。

```

---

## self-evolving-orchestrator

**A Go-based task orchestration system that self-evolves its decomposition strategy based on execution outcomes. Uses a strategy pool, scoring feedback loop, and overlap detection to refine task decomposition.**

```
cd 80-PROJECTS/self-evolving-orchestrator
```

### README Excerpt

```markdown
# Self-Evolving Orchestrator

A Go-based task orchestration system that self-evolves its decomposition strategy based on execution outcomes. Uses a strategy pool, scoring feedback loop, and overlap detection to refine task decomposition.


## 安装

```bash
npm install
```

## Architecture

```
Orchestrator
├── EvolutionLoop       — Self-evolution core; runs iterations with strategy refinement
├── SelfEvolver        — Analyzes results, decides when/how to refine decomposition
├── ResultRanker       — Scores results by quality, latency, success, relevance
└── DecomposerWrapper  — Applies strategy hints to LLM or simple decomposition
```

### Components

**Orchestrator** (`orchestrator.go`) — Entry point. Provides `Process` (with self-evolution) and `ProcessBasic` (single-shot).

**EvolutionLoo
```

---

## star-forge-web

**![Version](https://img.shields.io/badge/version-1.0.0-blue)**

```
cd 80-PROJECTS/star-forge-web
```

### README Excerpt

```markdown
# 🎮 Star Forge Web - 星之熔炉网页版

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![React](https://img.shields.io/badge/React-19.2.4-61dafb)
![Vite](https://img.shields.io/badge/Vite-8.0.1-646cff)

一款类似星露谷的农场建造游戏网页版。使用 React 和 Vite 构建。

## 🚀 一键启动

### 方法一：双击启动脚本（推荐）

1. **交互式菜单** - 双击 `启动菜单.ps1`
   - 提供 5 种启动模式可选
   - 自动检测并安装依赖
   - 包含清理和说明功能

2. **快速开发** - 双击 `启动游戏.bat`
   - 自动打开浏览器
   - 启动开发服务器

3. **生产预览** - 双击 `预览版本.bat`
   - 使用构建后的生产版本
   - 适合测试最终效果

### 方法二：命令行启动

```bash
# 安装依赖
npm install

# 开发模式（推荐）
npm run dev

# 生产预览
npm run preview

# 构建生产版本
npm run build
```

## 🎯 游戏功能

### ⚡ 核心玩法
- **点击收集** - 点击收集能量
- **建筑系统** - 建造各种建筑自动产生能量
- **升级系统** - 购买升级提升效率
- **成就系统** - 解锁各种成就
- **永恒重置** - 重置游戏获得永久加成

### 💾 存档系统
- **自动存档** - 自动保存游戏进度
- **本地存储** - 使用浏览器 localStorage
- **导出导入*
```

### Source Files

- `data/achievements.js`
- `data/buildings.js`
- `data/quests.js`
- `data/seasonConfig.js`
- `data/upgrades.js`
- `hooks/useGameLoop.js`
- `hooks/useLazyLoad.js`
- `hooks/useMemoCache.js`
- `hooks/useOfflineProgress.js`
- `hooks/useSaveLoad.js`

---

## stock-analysis-agent

**ReAct-based AI agent for stock market analysis. Takes natural language queries and produces comprehensive investment analysis reports.**

```
cd 80-PROJECTS/stock-analysis-agent
```

### README Excerpt

```markdown
# Stock Analysis Agent

ReAct-based AI agent for stock market analysis. Takes natural language queries and produces comprehensive investment analysis reports.

## Architecture

```
Query: "分析苹果最近趋势"
         │
         ▼
  ┌─────────────┐
  │  ReAct Agent │  ← select tools → execute → observe → repeat
  └─────────────┘
         │
         ▼
  Tool Executor
    ├── get_quote          (real-time price)
    ├── calc_all           (RSI/MACD/Bollinger/KDJ/ATR)
    ├── get_fundamentals   (P/E, EPS, market cap)
    └── analyze_trend      (MA crossovers)
         │
         ▼
  Report Generator → 📊 Analysis Report
```

## Three Interfaces

| Interface | Command | Best For |
|----------|---------|----------|
| **Web UI** | Open `index.html` in browser | Non-technical users |
| **CLI** | `stock-age
```

### Source Files

- `agent.py`
- `agent_tools.py`
- `api.py`
- `cli.py`
- `debate.py`
- `export_pdf.py`
- `llm.py`
- `macd_events.py`
- `persistence.py`
- `portfolio.py`

---

## task-orchestrator

**Chain opencli (browser) + CLI-Anything (software) via a rule-based task planner.**

```
cd 80-PROJECTS/task-orchestrator
```

### README Excerpt

```markdown
# unified-agent-cli

Chain opencli (browser) + CLI-Anything (software) via a rule-based task planner.

**Zero AI dependencies.** Parses natural language → step sequence → executes sequentially.

## Install

```bash
npm install -g unified-agent-cli
```

Requires: opencli daemon running (`opencli doctor` to verify), CLI-Anything harnesses installed via `pip install git+...#subdirectory=...`.

## Usage

```bash
# Direct natural language
task "帮我截图小红书这篇笔记"

# Dry run (parse only)
task --dry-run "截图然后录视频"

# Check adapter availability
task --check

# List all adapters
task --list

# Continue on recoverable errors
task --continue-on-error "截图然后导视频"

# Verbose logging
task --verbose "打开OBS录制"

# Watch directory for changes
task --watch ./screenshots "process"

# Structured output in YAML
task --o
```

### API Sections

**Usage**

```
```bash
# Direct natural language
task "帮我截图小红书这篇笔记"

# Dry run (parse only)
task --dry-run "截图然后录视频"

# Check adapter availability
task --check

# List all adapters
task --list

# Continue on recover
```

### Source Files

- `adapters/adapter-sandbox.ts`
- `adapters/cli-anything.ts`
- `adapters/index.ts`
- `adapters/multi-agent-hub.ts`
- `adapters/opencli.ts`
- `adapters/registry-loader.ts`
- `adapters/shell.ts`
- `adapters/swarm.ts`
- `capability-explorer.ts`
- `executor.ts`

---
