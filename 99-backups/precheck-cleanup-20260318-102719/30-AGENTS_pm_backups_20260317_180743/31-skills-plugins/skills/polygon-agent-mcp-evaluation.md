# Polygon Agent CLI MCP 集成评估报告

**评估时间:** 2026-03-07 04:23  
**仓库:** https://github.com/0xPolygon/polygon-agent-CLI  
**状态:** ✅ 评估完成

---

## 📊 当前状态分析

### 已有集成

| 集成方式 | 状态 | 说明 |
|----------|------|------|
| **Skills 协议** | ✅ 支持 | `skills/SKILL.md` 已提供 |
| **npm/npx** | ✅ 支持 | `@polygonlabs/agent-cli` |
| **MCP 协议** | ❌ 不支持 | 未找到 MCP 相关代码 |

### 技术栈

| 技术 | 用途 | MCP 兼容性 |
|------|------|------------|
| **TypeScript** | 主要语言 | ✅ 兼容 |
| **Node.js 20+** | 运行时 | ✅ 兼容 |
| **yargs** | CLI 框架 | ✅ 可包装 |
| **Skills** | Agent 文档 | ✅ 已有 |

---

## 🔍 MCP 集成可行性

### 优势

| 优势 | 说明 | 评分 |
|------|------|------|
| **CLI 结构清晰** | 命令模块化 (setup/wallet/operations/agent) | ⭐⭐⭐⭐⭐ |
| **已有 Skills** | 已有 Agent 友好文档 | ⭐⭐⭐⭐⭐ |
| **TypeScript** | 易添加 MCP SDK | ⭐⭐⭐⭐⭐ |
| **无状态命令** | 大多数命令是独立的 | ⭐⭐⭐⭐ |
| **干跑模式** | 默认 `--broadcast` 需显式 | ⭐⭐⭐⭐⭐ |

### 挑战

| 挑战 | 影响 | 缓解 |
|------|------|------|
| **Session 状态** | 钱包 Session 需持久化 | 使用现有 `~/.polygon-agent/` |
| **浏览器回调** | wallet create 需浏览器交互 | 保持现有 Cloudflare Tunnel |
| **加密存储** | AES-256-GCM 密钥管理 | 复用现有存储层 |
| **环境依赖** | 需要 Node.js 20+ | MCP 服务器独立运行 |

---

## 🎯 集成方案

### 方案 A: MCP 包装器 (推荐) ⭐⭐⭐⭐⭐

**工作量:** ~2-4 小时

**方法:** 创建 MCP 包装器脚本，类似 arxiv-daily

**文件:** `polygon-agent-mcp-wrapper.ts`

```typescript
#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { exec } from 'child_process';
import util from 'util';

const execPromise = util.promisify(exec);

const server = new Server({
  name: 'polygon-agent-cli',
  version: '0.2.2'
}, {
  capabilities: {
    tools: {}
  }
});

// 定义工具
server.setRequestHandler('tools/list', async () => {
  return {
    tools: [
      {
        name: 'setup',
        description: 'Setup EOA and Sequence project',
        inputSchema: {
          type: 'object',
          properties: {
            name: { type: 'string', description: 'Agent name' }
          }
        }
      },
      {
        name: 'wallet_create',
        description: 'Create ecosystem wallet',
        inputSchema: { ... }
      },
      {
        name: 'balances',
        description: 'Check token balances',
        inputSchema: { ... }
      },
      {
        name: 'send',
        description: 'Send tokens',
        inputSchema: { ... }
      },
      {
        name: 'swap',
        description: 'Swap tokens',
        inputSchema: { ... }
      },
      {
        name: 'agent_register',
        description: 'Register agent on-chain (ERC-8004)',
        inputSchema: { ... }
      }
    ]
  };
});

server.setRequestHandler('tools/call', async (request) => {
  const { name, arguments: args } = request.params;
  
  // 调用 CLI 命令
  const command = `npx @polygonlabs/agent-cli ${name} ${formatArgs(args)}`;
  const { stdout, stderr } = await execPromise(command);
  
  return {
    content: [{ type: 'text', text: stdout || stderr }]
  };
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch(console.error);
```

**优点:**
- ✅ 无需修改原始 CLI
- ✅ 快速实施
- ✅ 易于调试
- ✅ 可独立测试

**缺点:**
- ⚠️ 进程开销 (每个命令启动新进程)
- ⚠️ 状态管理复杂

---

### 方案 B: 原生 MCP 集成 ⭐⭐⭐⭐

**工作量:** ~8-16 小时

**方法:** 直接修改 polygon-agent-cli 添加 MCP 支持

**修改:**
1. 添加 `@modelcontextprotocol/sdk` 依赖
2. 创建 `src/mcp-server.ts`
3. 添加 `mcp` 命令
4. 导出工具定义

**优点:**
- ✅ 性能更好 (无进程开销)
- ✅ 状态共享
- ✅ 官方支持

**缺点:**
- ⚠️ 需要上游合并
- ⚠️ 维护成本高
- ⚠️ 需要测试

---

### 方案 C: mcporter 包装 ⭐⭐⭐

**工作量:** ~30 分钟

**方法:** 使用 mcporter 直接包装现有 CLI

**配置:**
```json
{
  "mcpServers": {
    "polygon-agent": {
      "command": "npx",
      "args": ["@polygonlabs/agent-cli"],
      "transport": "stdio",
      "tools": {
        "setup": { ... },
        "wallet_create": { ... },
        "balances": { ... }
      }
    }
  }
}
```

**优点:**
- ✅ 最快实施
- ✅ 无需代码修改

**缺点:**
- ⚠️ mcporter 配置复杂
- ⚠️ 工具定义手动维护
- ⚠️ 错误处理困难

---

## 📋 推荐方案：方案 A (MCP 包装器)

### 理由

1. **平衡速度和灵活性** - 2-4 小时完成
2. **无需上游修改** - 独立维护
3. **可测试验证** - 先验证概念
4. **可迁移** - 未来可迁移到原生集成

### 实施步骤

**Step 1: 创建项目** (~30 分钟)
```bash
mkdir polygon-agent-mcp
cd polygon-agent-mcp
npm init -y
npm install @modelcontextprotocol/sdk
```

**Step 2: 编写包装器** (~1 小时)
- 定义工具列表
- 实现工具调用
- 错误处理

**Step 3: 测试** (~1 小时)
- 测试每个工具
- 验证 Session 管理
- 测试错误场景

**Step 4: 集成** (~30 分钟)
- 配置 mcporter
- 测试 MCP 调用
- 文档更新

---

## 🔧 工具定义

### 核心工具

| 工具 | 功能 | 参数 |
|------|------|------|
| **setup** | 创建 EOA 和 Sequence 项目 | name |
| **wallet_create** | 创建生态钱包 | name, limits, timeout |
| **wallet_list** | 列出钱包 | - |
| **balances** | 查询余额 | wallet, chain |
| **send** | 发送代币 | to, amount, symbol, broadcast |
| **swap** | 交换代币 | from, to, amount, slippage |
| **deposit** | DeFi 存款 | asset, amount, protocol |
| **agent_register** | 注册链上身份 | name, metadata |
| **agent_reputation** | 查询声誉 | agent-id |
| **agent_feedback** | 提交反馈 | agent-id, value |

---

## ⚠️ 特殊考虑

### Session 管理

**问题:** wallet create 需要浏览器交互和 Session 回调

**解决方案:**
- 保持现有 Cloudflare Tunnel 机制
- MCP 服务器等待回调完成
- 返回 approvalUrl 给客户端

### 安全考虑

**敏感操作:**
- 私钥管理 (加密存储)
- Session 权限 (消费上限)
- 干跑模式 (默认不广播)

**MCP 安全:**
- 工具调用需显式 `broadcast: true`
- Session 权限继承 CLI
- 审计日志记录

### 错误处理

**常见错误:**
- `Missing SEQUENCE_PROJECT_ACCESS_KEY` → 提示运行 setup
- `Session expired` → 提示重新 wallet create
- `Insufficient funds` → 提示 fund
- `Callback timeout` → 增加 timeout 或手动模式

---

## 📊 工作量估算

| 阶段 | 时间 | 产出 |
|------|------|------|
| **项目设置** | 30 分钟 | 项目结构、依赖 |
| **包装器开发** | 1-2 小时 | MCP 服务器代码 |
| **工具定义** | 30 分钟 | 工具 schema |
| **测试** | 1 小时 | 测试用例、验证 |
| **集成** | 30 分钟 | mcporter 配置 |
| **文档** | 30 分钟 | README、示例 |
| **总计** | **3-5 小时** | **完整 MCP 集成** |

---

## 🎯 下一步

### 立即行动

1. **确认需求** - 是否需要 MCP 集成
2. **选择方案** - 方案 A/B/C
3. **开始实施** - 根据选择方案

### 替代方案

如果 MCP 集成不急：
- 继续使用 Skills 协议 (已支持)
- 等待上游原生 MCP 支持
- 监控社区动态

---

## 📋 总结

**MCP 集成可行性:** ✅ 高

**推荐方案:** 方案 A (MCP 包装器)

**工作量:** 3-5 小时

**风险:** 低 (独立包装，不影响原 CLI)

**收益:**
- ✅ 与现有 MCP 架构统一
- ✅ 支持 Claude Desktop 直接调用
- ✅ 支持自动化编排
- ✅ 支持错误处理和重试

---

*评估完成，等待决策*
