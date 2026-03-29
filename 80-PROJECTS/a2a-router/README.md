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

```javascript
// 创建 LangChain agent
await router.handleRouterCommand({
  type: 'LANGCHAIN_CREATE',
  payload: { agentId: 'my-agent', config: { model: 'gpt-4' } }
});

// 调用 agent
const result = await router.handleRouterCommand({
  type: 'LANGCHAIN_INVOKE',
  payload: { agentId: 'my-agent', input: { messages: [...] } }
});

// 查询状态 / 列出所有 agent
router.handleRouterCommand({ type: 'LANGCHAIN_STATUS', payload: { runId } });
router.handleRouterCommand({ type: 'LANGCHAIN_LIST', payload: {} });
```

### Dify Workflow

支持 Dify 工作流编排：

```javascript
// 执行工作流
orchestrationEngine.executeWorkflow('workflow-id', { input: 'value' });
```

### 安全层

- API Key 管理（6 个 MCP 安全工具）
- ACL 访问控制（capability-based）
- 消息签名验证

## 测试

```bash
npm test
```

## 项目结构

```
src/
├── router.js              # 核心路由
├── server.js             # MCP Server 入口
└── protocols/
    ├── capability-registry.js   # 能力注册与匹配
    ├── orchestration/
    │   ├── orchestration-engine.js
    │   ├── langchain-adapter.js  # LangChain 适配器
    │   └── dify-adapter.js       # Dify 适配器
    ├── security/
    │   ├── security-manager.js   # API Key 生命周期
    │   └── access-control.js      # ACL
    └── task-decomposition/
        └── subtask-manager.js    # 任务分解

tests/                    # 单元测试 (vitest)
test/integration/         # 集成测试
```
