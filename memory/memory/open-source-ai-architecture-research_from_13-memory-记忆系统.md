# 开源 AI 系统架构研究笔记

**日期:** 2026-03-07  
**来源:** GitHub Topics - ai-agent-framework  
**项目数:** 78 个公开仓库

---

## 🏆 Top 开源项目

| 项目 | Stars | 语言 | 核心特点 |
|------|-------|------|----------|
| [trigger.dev](https://github.com/triggerdotdev/trigger.dev) | 14k | TypeScript | 全托管 AI 代理工作流 |
| [awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) | 12.8k | Shell | 100+ 专业化 Claude 子代理 |
| [intentkit](https://github.com/crestalnetwork/intentkit) | 6.5k | Python | 基于意图的代理集群 |
| [PraisonAI](https://github.com/MervinPraison/PraisonAI) | 5.6k | Python | 低代码多代理系统 |
| [ii-agent](https://github.com/Intelligent-Internet/ii-agent) | 3.2k | Python | 智能互联网代理框架 |

---

## 🏗️ 核心架构模式

### 1. 意图驱动架构 (Intent-Driven)

**代表项目:** intentkit

**核心思想:**
- 定义系统"想要什么"而非"怎么做"
- 意图编码为可执行目标
- 代理自主决策实现路径

**与信念探针关联:**
```
意图定义 → 目标状态
信念探针 → 确定性检测
早退决策 → 意图达成度评估
```

### 2. 多代理协作 (Multi-Agent Collaboration)

**代表项目:** PraisonAI, swarmzero

**架构特点:**
- 专业化代理分工
- 动态任务分配
- 代理间通信协议

**应用场景:**
- 复杂任务分解
- 并行处理
- 知识共享

### 3. 工作流编排 (Workflow Orchestration)

**代表项目:** trigger.dev, agent-kit

**核心组件:**
- 可视化工作流编辑器
- 确定性路由
- 丰富工具集成 (MCP)

**技术栈:**
- TypeScript/Python
- Serverless 部署
- 背景任务调度

### 4. 子代理模式 (Sub-Agent Pattern)

**代表项目:** awesome-claude-code-subagents

**特点:**
- 100+ 专业化子代理
- 覆盖开发全场景
- 即插即用架构

**子代理类型:**
- 代码审查
- 测试生成
- 文档编写
- Bug 修复
- 性能优化

---

## 🔗 与创意 3 验证的关联

### 信念探针早退机制整合方案

**架构层次:**
```
┌─────────────────────────────────────┐
│         意图工程层                   │
│  (定义系统目标和成功标准)             │
├─────────────────────────────────────┤
│         信念探针层                   │
│  (检测模型确定性和意图达成度)         │
├─────────────────────────────────────┤
│         早退决策层                   │
│  (基于意图 - 信念对齐的动态早退)      │
├─────────────────────────────────────┤
│         模型执行层                   │
│  (Qwen3.5-2B + 早退优化)             │
└─────────────────────────────────────┘
```

**创新点:**
1. **意图 - 信念对齐检测**
   - 意图定义"想要什么"
   - 信念探针检测"确定性"
   - 对齐度作为早退额外条件

2. **动态阈值调整**
   - 基于意图复杂度自动调整置信度阈值
   - 简单意图：低阈值早退
   - 复杂意图：高阈值或全模型

3. **多代理早退协调**
   - 主代理早退决策
   - 子代理继续执行
   - 资源最优分配

---

## 📚 学习资源

### 必读项目
1. [intentkit](https://github.com/crestalnetwork/intentkit) - 意图工程实践
2. [trigger.dev](https://github.com/triggerdotdev/trigger.dev) - 工作流编排
3. [awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) - 子代理模式

### 技术博客
- Intent Engineering: The Missing Layer in AI Systems (Towards AI)
- Build multi-agent networks in TypeScript (Inngest)

---

## 💡 下一步行动

- [ ] 深入研究 intentkit 意图编码机制
- [ ] 实验信念探针与意图工程整合
- [ ] 设计意图 - 信念对齐度量化方法
- [ ] 实现动态阈值调整算法
- [ ] 撰写技术报告

---

*持续更新中...*
