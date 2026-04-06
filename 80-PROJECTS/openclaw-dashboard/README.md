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
npm run test:e2e    # 运行e2e测试
```

## 项目结构

```
openclaw-dashboard/
├── self-evolving-loop.mjs   # Self-Evolution入口（重定向到src/index.mjs）
├── dashboard-server.js        # Dashboard HTTP服务器
├── dashboard.html           # Dashboard前端（单文件HTML，内联CSS/JS）
├── generate-dashboard-data.js  # 扫描workspace生成dashboard-data.json
├── dashboard-data.json      # Dashboard数据（由generate生成，git ignore）
├── playwright.config.js      # E2E测试配置
├── src/
│   ├── index.mjs            # 自我优化循环主入口
│   ├── config/
│   │   └── default.mjs      # 默认配置
│   ├── core/
│   │   ├── agent.mjs       # Agent主控
│   │   ├── meta-cognizer.mjs   # 元认知分析
│   │   ├── tool-router.mjs    # 工具路由
│   │   └── working-memory.mjs   # 工作记忆
│   ├── evolution/
│   │   ├── hypothesis.mjs  # 假设生成
│   │   ├── population.mjs   # 群体管理
│   │   └── sandbox.mjs      # 沙盒执行
│   ├── governance/
│   │   ├── audit.mjs       # 审计
│   │   ├── budget.mjs       # 预算管理
│   │   ├── constitution.mjs  # 宪法约束
│   │   ├── rollback.mjs      # 回滚机制
│   │   └── safety.mjs        # 安全边界
│   ├── learn/
│   │   ├── candidate-pool.mjs  # 候选操作池
│   │   ├── curriculum.mjs   # 学习课程
│   │   ├── discoverer.mjs   # 发现器
│   │   ├── distiller.mjs    # 蒸馏器
│   │   └── filter.mjs       # 过滤器
│   ├── memory/
│   │   ├── ltm.mjs          # 长期记忆
│   │   ├── skill-library.mjs # 技能库
│   │   └── stm.mjs           # 短期记忆
│   ├── meta/
│   │   ├── architecture-search.mjs  # 架构搜索
│   │   └── self-modeling.mjs        # 自我建模
│   └── operations/
│       ├── base.mjs          # 操作基类
│       ├── detection-ops.mjs  # 检测操作
│       ├── improvement-ops.mjs   # 改进操作
│       ├── index.mjs         # 操作注册表
│       └── productive-ops.mjs    # 生产操作
├── tests/                   # 测试文件
├── node_modules/             # 依赖
└── package.json
```

## 使用方法

```bash
# 查看系统状态
node self-evolving-loop.mjs --status

# 运行元认知分析
node self-evolving-loop.mjs --analyze

# 运行一次优化迭代
node self-evolving-loop.mjs
```

## 核心机制

- **ε-greedy探索**：平衡探索(ε)与利用(1-ε)
- **操作历史**：`.omc/loop-history.json`记录每次迭代
- **Governance约束**：预算上限、安全边界、宪法约束
- **元认知**：发现能力缺口并优先修复

## Embeddable Widgets

This dashboard ships with reusable HTML widget snippets in `widgets/`:

### Badge Widget (`widgets/badge.html`)
```html
<div id="my-badge"></div>
<script src="/path/to/widgets/badge.html"></script>
<script>renderOCBadge('my-badge', '#science', 'green');</script>
```
Colors: `green` `amber` `cyan` `red` `gray`

### Trend Widget (`widgets/trend.html`)
```html
<div id="my-trend"></div>
<script src="/path/to/widgets/trend.html?data=1,3,2,5,4&label=Score&color=cyan"></script>
```
Query params: `data` (csv), `label`, `color`

### Project Status Widget (`widgets/project-status.html`)
```html
<div id="my-status"></div>
<script src="/path/to/widgets/project-status.html?project=my-app&status=active"></script>
```
Query params: `project`, `status` (active/warning/error/idle), `updated`

## 版本

- **version**: 1.0.0
