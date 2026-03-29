# Multi-Agent Memory Mesh + A2A Protocol — Implementation Plan

> **Source:** GitHub/arXiv 研究 + 头脑风暴  
> **Selected:** 方案 A + C 组合  
> **Status:** 📝 Writing Plans → ⏳ Executing Plans

---

## 项目概述

### 目标
构建 Multi-Agent Memory Mesh，让 Patrol Agent、AI Roundtable、Agent Arena 共享 OpenViking 记忆库，并通过 A2A 协议实现标准化通信。

### 核心价值
1. **记忆共享** — Patrol 发现的问题，Roundtable 自动讨论解决方案
2. **知识继承** — 新 Agent 接入即拥有历史经验
3. **协作编排** — Agent 之间可以委托任务、查询数据
4. **生态扩展** — 标准化协议支持未来 Agent 接入

---

## 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                    Multi-Agent Ecosystem                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │Patrol Agent │    │AI Roundtable│    │Agent Arena  │     │
│  │             │    │             │    │             │     │
│  │ • 巡逻发现   │    │ • 深度讨论   │    │ • 对战模拟   │     │
│  │ • 问题记录   │    │ • 方案生成   │    │ • 策略优化   │     │
│  │ • 任务执行   │    │ • 决策建议   │    │ • 结果反馈   │     │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘     │
│         │                  │                  │              │
│         └──────────────────┼──────────────────┘              │
│                            │                                 │
│                            ↓                                 │
│              ┌─────────────────────────┐                    │
│              │     A2A Router          │                    │
│              │     (MCP Server)        │                    │
│              │                         │                    │
│              │ • Message Routing       │                    │
│              │ • Service Discovery     │                    │
│              │ • Load Balancing        │                    │
│              │ • Priority Queue        │                    │
│              └───────────┬─────────────┘                    │
│                          │                                   │
│                          ↓                                   │
│              ┌─────────────────────────┐                    │
│              │   OpenViking Memory     │                    │
│              │       Mesh              │                    │
│              │                         │                    │
│              │ viking://shared/        │                    │
│              │ ├── problems/           │                    │
│              │ ├── solutions/          │                    │
│              │ ├── decisions/          │                    │
│              │ ├── patterns/           │                    │
│              │ └── agent-comm/         │                    │
│              └─────────────────────────┘                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Memory Mesh 基础设施

### Task 1.1: 扩展 OpenViking 共享命名空间

**目标:** 在 OpenViking 中创建共享记忆空间

- [ ] **1.1.1** 设计共享记忆目录结构
  ```
  viking://shared/
  ├── problems/          # 共享问题记录
  ├── solutions/         # 共享解决方案
  ├── decisions/         # 共享决策记录
  ├── patterns/          # 共享模式识别
  └── agent-comm/        # Agent 间通信记录
  ```

- [ ] **1.1.2** 创建共享目录初始化脚本
  ```javascript
  // scripts/init-shared-memory.js
  ```

- [ ] **1.1.3** 测试共享空间写入/读取

**依赖:** OpenViking Docker 运行中
**输出:** 共享记忆空间可用

---

### Task 1.2: 升级 Memory Manager 支持共享空间

**目标:** MemoryManager 可以写入/读取共享空间

- [ ] **1.2.1** 添加共享空间配置
  ```javascript
  // memoryManager.js
  const SHARED_PATH = 'shared';
  const AGENT_PATH = `agent/${AGENT_ID}`;
  ```

- [ ] **1.2.2** 实现 `storeSharedMemory(type, content, metadata)`
  - 写入 viking://shared/
  - 添加来源 Agent 标记

- [ ] **1.2.3** 实现 `retrieveSharedMemories(query, options)`
  - 搜索共享空间
  - 支持按 Agent 过滤

- [ ] **1.2.4** 实现 `syncAgentToShared()`
  - 将 Agent 私有记忆同步到共享空间

**依赖:** Task 1.1
**输出:** MemoryManager 支持双空间（私有+共享）

---

### Task 1.3: 修改 Patrol Agent 集成共享记忆

**目标:** Patrol Agent 发现问题时写入共享空间

- [ ] **1.3.1** 修改 `index.js` 中的记忆存储
  ```javascript
  // 发现问题时
  await memoryManager.storeSharedMemory('problem', {
    source: 'patrol-agent',
    event: 'lint_error',
    description: '...',
    project: '...'
  });
  ```

- [ ] **1.3.2** 添加共享记忆检索到巡逻循环
  ```javascript
  // 执行计划前检索相关共享记忆
  const sharedMemories = await memoryManager.retrieveSharedMemories(
    `project:${project} type:problem`
  );
  ```

- [ ] **1.3.3** 测试共享记忆写入/读取

**依赖:** Task 1.2
**输出:** Patrol Agent 可以读写共享记忆

---

### Task 1.4: 修改 AI Roundtable 读取共享记忆

**目标:** AI Roundtable 可以读取 Patrol Agent 发现的问题

- [ ] **1.4.1** 在 Roundtable 初始化时加载共享记忆
  ```javascript
  // ai-roundtable/src/index.js
  const recentProblems = await memoryManager.retrieveSharedMemories(
    'type:problem',
    { limit: 10, sort: 'time:desc' }
  );
  ```

- [ ] **1.4.2** 在讨论时注入共享记忆上下文
  ```javascript
  // 构建 prompt 时添加
  context += `\n\n## Recent Problems from Patrol Agent\n`;
  context += formatMemories(recentProblems);
  ```

- [ ] **1.4.3** 讨论完成后将解决方案写入共享空间
  ```javascript
  await memoryManager.storeSharedMemory('solution', {
    source: 'ai-roundtable',
    relatedProblem: problemId,
    solution: '...'
  });
  ```

**依赖:** Task 1.2
**输出:** AI Roundtable 可以消费 Patrol Agent 的记忆

---

## Phase 2: A2A Protocol 通信层

### Task 2.1: 设计 A2A 协议规范

**目标:** 定义 Agent 间通信标准

- [ ] **2.1.1** 设计消息格式
  ```typescript
  // a2a-protocol/types.ts
  interface A2AMessage {
    id: string;
    type: 'TASK' | 'QUERY' | 'RESPONSE' | 'EVENT';
    priority: 'CRITICAL' | 'HIGH' | 'NORMAL' | 'LOW';
    from: string;      // Agent ID
    to: string;        // Agent ID or 'broadcast'
    timestamp: number;
    payload: any;
    metadata: {
      ttl?: number;    // Time to live
      retry?: number;  // Retry count
      tags?: string[];
    };
  }
  ```

- [ ] **2.1.2** 设计服务发现格式
  ```typescript
  interface AgentCapability {
    agentId: string;
    capabilities: string[];  // ['research', 'code-review', 'test']
    status: 'idle' | 'busy' | 'offline';
    load: number;            // 0-1
  }
  ```

- [ ] **2.1.3** 编写 A2A 协议文档
  ```
  docs/a2a-protocol/v1.0-spec.md
  ```

**输出:** A2A Protocol v1.0 规范文档

---

### Task 2.2: 实现 A2A Router (MCP Server)

**目标:** 构建 Agent 间消息路由器

- [ ] **2.2.1** 创建 A2A Router 项目结构
  ```
  80-PROJECTS/a2a-router/
  ├── src/
  │   ├── server.js       # MCP Server
  │   ├── router.js       # Message routing logic
  │   ├── registry.js     # Agent registry
  │   └── queue.js        # Message queue
  ├── package.json
  └── README.md
  ```

- [ ] **2.2.2** 实现 MCP Server 基础框架
  ```javascript
  // src/server.js
  // 基于 MCP SDK 实现
  ```

- [ ] **2.2.3** 实现消息路由逻辑
  - Direct routing (指定 Agent)
  - Broadcast (广播)
  - Discovery (服务发现)

- [ ] **2.2.4** 实现 Agent 注册/心跳机制
  ```javascript
  // Agent 启动时注册
  // 定期发送心跳
  // 超时自动标记为 offline
  ```

- [ ] **2.2.5** 实现优先级队列
  - CRITICAL: 立即处理
  - HIGH: 优先队列
  - NORMAL: 普通队列
  - LOW: 后台处理

**依赖:** Task 2.1
**输出:** A2A Router MCP Server 可用

---

### Task 2.3: 为 Patrol Agent 添加 A2A 客户端

**目标:** Patrol Agent 可以发送/接收 A2A 消息

- [ ] **2.3.1** 创建 A2A Client 模块
  ```javascript
  // .omc/patrol-agent/src/a2a/client.js
  class A2AClient {
    constructor(agentId, routerEndpoint) {}
    async register() {}
    async send(message) {}
    async subscribe(handler) {}
    async discover(capability) {}
  }
  ```

- [ ] **2.3.2** 集成到 Patrol Agent 初始化
  ```javascript
  // index.js
  const a2aClient = new A2AClient('patrol-agent', 'http://localhost:3000');
  await a2aClient.register();
  ```

- [ ] **2.3.3** 实现消息处理器
  ```javascript
  // 处理来自其他 Agent 的任务请求
  a2aClient.subscribe(async (msg) => {
    if (msg.type === 'TASK' && msg.payload.task === 'scan') {
      // 执行扫描任务
      const result = await performScan(msg.payload.target);
      await a2aClient.send({
        type: 'RESPONSE',
        to: msg.from,
        payload: result
      });
    }
  });
  ```

- [ ] **2.3.4** 在发现问题时广播事件
  ```javascript
  // 发现问题时
  await a2aClient.send({
    type: 'EVENT',
    to: 'broadcast',
    priority: 'HIGH',
    payload: {
      event: 'problem_detected',
      problem: problemData
    }
  });
  ```

**依赖:** Task 2.2
**输出:** Patrol Agent 可以 A2A 通信

---

### Task 2.4: 为 AI Roundtable 添加 A2A 客户端

**目标:** AI Roundtable 可以响应 Patrol Agent 的事件

- [ ] **2.4.1** 集成 A2A Client
  ```javascript
  // ai-roundtable/src/index.js
  const a2aClient = new A2AClient('ai-roundtable', 'http://localhost:3000');
  ```

- [ ] **2.4.2** 订阅 Patrol Agent 事件
  ```javascript
  a2aClient.subscribe(async (msg) => {
    if (msg.payload.event === 'problem_detected') {
      // 自动启动讨论
      await startDiscussion({
        topic: `Problem: ${msg.payload.problem.description}`,
        context: msg.payload.problem
      });
    }
  });
  ```

- [ ] **2.4.3** 讨论完成后发送解决方案
  ```javascript
  await a2aClient.send({
    type: 'RESPONSE',
    to: msg.from,  // 回复 Patrol Agent
    payload: {
      solution: discussionResult
    }
  });
  ```

**依赖:** Task 2.3
**输出:** AI Roundtable 可以响应 Patrol Agent

---

### Task 2.5: 为 Agent Arena 添加 A2A 客户端

**目标:** Agent Arena 可以查询其他 Agent 能力

- [ ] **2.5.1** 集成 A2A Client

- [ ] **2.5.2** 对战前查询可用对手
  ```javascript
  const availableAgents = await a2aClient.discover('arena-opponent');
  ```

- [ ] **2.5.3** 对战结果广播
  ```javascript
  await a2aClient.send({
    type: 'EVENT',
    to: 'broadcast',
    payload: {
      event: 'arena_match_complete',
      result: matchResult
    }
  });
  ```

**依赖:** Task 2.2
**输出:** Agent Arena 可以 A2A 通信

---

## Phase 3: 集成测试

### Task 3.1: 端到端测试

- [ ] **3.1.1** 测试 Patrol → Roundtable 事件流
  ```
  1. Patrol 发现问题
  2. 广播 EVENT 消息
  3. Roundtable 接收并启动讨论
  4. Roundtable 发送解决方案
  5. Patrol 接收解决方案
  ```

- [ ] **3.1.2** 测试共享记忆同步
  ```
  1. Patrol 写入共享问题
  2. Roundtable 读取共享问题
  3. Roundtable 写入共享解决方案
  4. Patrol 读取共享解决方案
  ```

- [ ] **3.1.3** 测试服务发现
  ```
  1. 启动多个 Agent
  2. 查询特定能力
  3. 验证返回正确的 Agent
  ```

---

### Task 3.2: 性能测试

- [ ] **3.2.1** 测试消息吞吐量
  - 目标: 100 msg/sec

- [ ] **3.2.2** 测试共享记忆检索延迟
  - 目标: < 100ms

- [ ] **3.2.3** 测试并发 Agent 连接
  - 目标: 支持 50+ Agent

---

### Task 3.3: 故障恢复测试

- [ ] **3.3.1** 测试 A2A Router 故障恢复

- [ ] **3.3.2** 测试 Agent 断线重连

- [ ] **3.3.3** 测试消息丢失重传

---

## Phase 4: 文档与部署

### Task 4.1: 编写文档

- [ ] **4.1.1** Memory Mesh 使用文档
- [ ] **4.1.2** A2A Protocol API 文档
- [ ] **4.1.3** Agent 接入指南
- [ ] **4.1.4** 架构设计文档

---

### Task 4.2: 部署配置

- [ ] **4.2.1** Docker Compose 配置
  ```yaml
  # docker-compose.yml
  services:
    openviking:
      # ...
    a2a-router:
      # ...
  ```

- [ ] **4.2.2** 环境变量模板
- [ ] **4.2.3** 监控配置 (Prometheus/Grafana)

---

## 依赖关系图

```
Phase 1: Memory Mesh
├── 1.1 OpenViking 共享空间
├── 1.2 Memory Manager 升级 ← 依赖 1.1
├── 1.3 Patrol Agent 集成 ← 依赖 1.2
└── 1.4 AI Roundtable 集成 ← 依赖 1.2

Phase 2: A2A Protocol
├── 2.1 协议设计
├── 2.2 A2A Router ← 依赖 2.1
├── 2.3 Patrol A2A ← 依赖 2.2
├── 2.4 Roundtable A2A ← 依赖 2.3
└── 2.5 Arena A2A ← 依赖 2.2

Phase 3: 测试
└── 依赖 Phase 1 + Phase 2

Phase 4: 文档
└── 依赖 Phase 3
```

---

## 时间估算

| Phase | 任务数 | 估算时间 | 优先级 |
|-------|--------|----------|--------|
| Phase 1 | 4 | 2-3 天 | P0 |
| Phase 2 | 5 | 3-4 天 | P0 |
| Phase 3 | 3 | 2 天 | P1 |
| Phase 4 | 2 | 1 天 | P2 |
| **总计** | **14** | **8-10 天** | - |

---

## 成功标准

1. **功能标准**
   - [ ] Patrol Agent 发现问题 → AI Roundtable 自动讨论
   - [ ] AI Roundtable 生成方案 → Patrol Agent 自动执行
   - [ ] Agent Arena 可以查询并邀请其他 Agent 对战
   - [ ] 新 Agent 接入后可以读取历史共享记忆

2. **性能标准**
   - [ ] 消息延迟 < 100ms
   - [ ] 支持 50+ Agent 并发
   - [ ] 共享记忆检索 < 200ms

3. **稳定性标准**
   - [ ] 7x24 小时运行无故障
   - [ ] Agent 断线自动重连
   - [ ] 消息不丢失

---

## 风险与缓解

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| OpenViking 性能瓶颈 | 中 | 高 | 本地缓存 + 异步写入 |
| A2A Router 单点故障 | 中 | 高 | 支持多实例 + 负载均衡 |
| Agent 版本不兼容 | 低 | 中 | 协议版本协商机制 |
| 消息循环依赖 | 低 | 高 | 消息 TTL + 循环检测 |

---

## 下一步行动

**立即执行:**
1. ✅ 完成本计划文档
2. ⏳ 开始 Phase 1.1: OpenViking 共享空间初始化
3. ⏳ 并行开始 Phase 2.1: A2A 协议设计

**需要决策:**
- A2A Router 使用 HTTP 还是 WebSocket？
- 共享记忆是否需要访问控制？
- 是否需要消息持久化？

---

**计划完成时间:** 2026-04-06 (10天)

**负责人:** Feishu (nWyDpW)

**状态:** 📝 Planning Complete → Ready for Execution
