# workspace

[![Tests](https://github.com/shushuzn/workspace/actions/workflows/Tests/badge.svg)](https://github.com/shushuzn/workspace/actions/workflows/Tests)

> OpenClaw AI Workstation — 全能力自进化智能体工作站

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              OpenClaw Workstation                                     │
│                                                                                     │
│  ┌─────────────┐    ┌──────────────────────────────────────────────────────────┐  │
│  │  oh-my-     │    │                     80-PROJECTS                            │  │
│  │  claudecode │    │                                                              │  │
│  │  (OMC)      │    │  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐  │  │
│  │             │    │  │ opencli     │  │ task-       │  │ multi-agent-hub   │  │  │
│  │  • CLAUDE.md│    │  │  browser    │  │ orchestrator│  │                  │  │  │
│  │  • skills/  │    │  │  automation │  │  task chain │  │  • Cognitive     │  │  │
│  │  • hooks/   │    │  │  79 adapters│  │  + MCP reg │  │    Annealing     │  │  │
│  │  • agents/  │    │  └──────┬──────┘  └──────┬──────┘  │  • Debate       │  │  │
│  └──────┬──────┘    │         │                │         │  • News Analyze │  │  │
│         │           │         ▼                ▼         │  • Code Analyze │  │  │
│         │           │  ┌─────────────────────────────┐  └────────┬─────────┘  │
│         ▼           │  │      openclaw-cli (router)   │             │           │
│  ┌─────────────┐    │  │  routes → opencli / task-orch / hub / CLI-Anything  │  │
│  │ shared/    │    │  └────────────────────┬──────────┘             │           │
│  │ shared-types│◄──┼────────────────────────┼────────────────────────┼─────────►│
│  │ shared-test │    │                        │                        │           │
│  │ -fixtures/  │    │         ┌──────────────▼──────────┐              │           │
│  └─────────────┘    │         │   CLI-Anything          │   ┌──────────▼───────┐  │
│                     │         │   auto-generates CLIs  │   │ openviking-mcp   │  │
│  ┌─────────────┐    │         │   for any software     │   │  context DB       │  │
│  │ docs/       │    │         │   1839 tests passing    │   │  session mgmt     │  │
│  │  • specs/   │    │         └──────────┬────────────┘   └──────────────────┘  │
│  │  • plans/   │    │                    │                                       │
│  │  • *.html   │    │  ┌────────────────▼────────────────┐                       │
│  └─────────────┘    │  │        AI-ROUNDTABLE              │                       │
│                    │  │   multi-agent structured debate  │                       │
│  ┌─────────────┐    │  └────────────────────────────────┘                       │
│  │ scripts/    │    │                                                              │
│  │ 80+ check- │    │  ┌───────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ ers & tools│    │  │ star-forge-   │  │ idle-empire   │  │ agent-arena      │  │
│  └─────────────┘    │  │ web (React19) │  │ (Svelte 5)   │  │ (Svelte 5)      │  │
│                    │  │  94.1% cov.   │  │  放置游戏      │  │  AI Agent竞技    │  │
│  ┌─────────────┐    │  └───────────────┘  └──────────────┘  └──────────────────┘  │
│  │ 30-SCRIPTS │    │                                                              │
│  │ TOOLS/     │    │  ┌───────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ automation  │    │  │ crucix        │  │ knowledge-   │  │ public-apis      │  │
│  └─────────────┘    │  │  27 OSINT源   │  │ bridge       │  │  419K★ API目录  │  │
│                    │  │  D3拓扑图     │  │ D3知识图谱   │  │  健康度监测      │  │
│  ┌─────────────┐    │  └───────────────┘  └──────────────┘  └──────────────────┘  │
│  │ 40-TOOLS/  │    │                                                              │
│  │ skills &   │    │  ┌───────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ plugins    │    │  │ rl-trading    │  │ stock-       │  │ material-price-  │  │
│  └─────────────┘    │  │  GRPO+PRM    │  │ analysis-    │  │ tracker         │  │
│                    │  │  强化学习交易  │  │ agent        │  │  塑化原料期货    │  │
│  ┌─────────────┐    │  └───────────────┘  └──────────────┘  └──────────────────┘  │
│  │ openclaw-   │    │                                                              │
│  │ mcp-       │    │              ┌──────────────────────────────┐                 │
│  │ registry    │    │              │   openclaw-mcp-registry     │                 │
│  │ (port 3847)│    │              │   MCP Server注册发现平台    │                 │
│  │ + billing  │    │              │   + Stripe计费 + Web UI     │                 │
│  └─────────────┘    │              └──────────────────────────────┘                 │
│                                                                                    │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

## 核心能力

| 能力 | 项目 | 描述 |
|------|------|------|
| **浏览器自动化** | `opencli` | 79个适配器，CDP协议，AI智能交互 |
| **任务编排** | `task-orchestrator` | Browser+CLI任务链，MCP工具发现 |
| **多智能体协作** | `multi-agent-hub` | 辩论引擎、新闻分析、代码分析 |
| **CLI生成** | `CLI-Anything` | 任意软件自动生成Agent可控CLI |
| **RL交易** | `rl-trading` | GRPO+PRM强化学习，paper trading |
| **股票分析** | `stock-analysis-agent` | ReAct+技术指标+多LLM路由 |
| **情报聚合** | `crucix` | 27个OSINT数据源，实时拓扑 |
| **知识图谱** | `knowledge-bridge` | URL→D3力导向图谱 |
| **会话记忆** | `openviking-mcp` | 跨session上下文持久化 |
| **公共API** | `public-apis` | 419K★，免费API可用性监测 |

## 共享基础设施

- **`shared/`** — error-middleware、metrics、pino日志配置
- **`shared-types/`** — `Result<T>`泛型、`MockMemoryStore`、`MockLogger`
- **`shared-test-fixtures/`** — 通用测试mock
- **`openclaw-mcp-registry/`** — MCP server注册发现+计费Web UI
- **`scripts/`** — 80+项目检查脚本（meta/keywords/scripts/env/gitignore等）

## 游戏项目

| 项目 | 技术 | 说明 |
|------|------|------|
| `idle-empire` | Svelte 5 | 放置挂机游戏，itch.io发布 |
| `agent-arena` | Svelte 5 | AI Agent养成竞技 |

## 快速开始

```bash
# 统一CLI入口
opencli "操作指令"           # 浏览器自动化
task-orchestrator --task X   # 任务编排
multi-agent-hub --debate X    # 多智能体辩论

# 项目开发
cd 80-PROJECTS/<project>
npm run dev
```

## 架构约定

- **MCP协议** — 所有agent能力通过MCP暴露
- **Result schema** — `shared-types`统一结果格式
- **Registry发现** — `openclaw-mcp-registry:3847`做能力路由
- **零配置** — 所有能力通过SKILL.md自我描述
