# arxiv-daily MCP 扩展方案

**创建时间:** 2026-03-07 04:01  
**状态:** 📋 设计中  
**预计工作量:** 2-4 小时

---

## 🎯 目标

为 arxiv-daily 添加 MCP 服务器支持，使其可以被 MCP 客户端调用。

---

## 📦 MCP 协议基础

**MCP (Model Context Protocol):**
- 开放协议，用于 AI 模型与外部工具通信
- 支持 stdio 和 HTTP 传输
- 工具定义：名称、描述、参数 schema

**arxiv-daily MCP 工具:**
```json
{
  "name": "arxiv_daily_collect",
  "description": "Collect daily arXiv papers for specified categories",
  "inputSchema": {
    "type": "object",
    "properties": {
      "categories": {"type": "array", "items": {"type": "string"}},
      "days": {"type": "integer", "default": 1},
      "min_score": {"type": "number", "default": 3.0},
      "output": {"type": "string", "default": "Medium/Raw/"}
    }
  }
}
```

---

## 🔧 实施方案

### 方案 A: 使用 mcporter (推荐)

**mcporter 已支持:**
- ✅ 创建自定义 MCP 服务器
- ✅ 包装现有脚本为 MCP 工具
- ✅ HTTP 和 stdio 传输

**实施步骤:**

**Step 1: 创建 mcporter 配置**

```json
// arxiv-daily-mcp.json
{
  "servers": {
    "arxiv-daily": {
      "command": "py",
      "args": ["D:/npm-global/node_modules/openclaw/skills/arxiv-daily/scripts/arxiv-daily.py"],
      "transport": "stdio",
      "tools": {
        "collect": {
          "description": "Collect daily arXiv papers",
          "input": {
            "categories": ["cs.AI", "cs.LG"],
            "days": 1,
            "min_score": 3.0
          }
        },
        "get_papers": {
          "description": "Get collected papers from JSON file",
          "input": {
            "date": "2026-03-07",
            "min_score": 4.0
          }
        }
      }
    }
  }
}
```

**Step 2: 测试 MCP 服务器**

```bash
# 启动 MCP 服务器
mcporter daemon start

# 列出可用工具
mcporter list arxiv-daily --schema

# 调用工具
mcporter call arxiv-daily.collect categories='["cs.AI","cs.LG"]' days=1
```

**Step 3: 配置 Claude Desktop**

```json
// ~/Library/Application Support/Claude/claude_desktop_config.json
{
  "mcpServers": {
    "arxiv-daily": {
      "command": "mcporter",
      "args": ["call", "arxiv-daily.collect"]
    }
  }
}
```

---

### 方案 B: 原生 MCP 服务器 (高级)

**使用 Python MCP SDK:**

**Step 1: 安装依赖**

```bash
pip install mcp
```

**Step 2: 创建 MCP 服务器包装器**

```python
# arxiv-daily-mcp.py
from mcp.server import Server
from mcp.server.stdio import stdio_server
from arxiv_daily import collect_papers

server = Server("arxiv-daily")

@server.tool()
async def collect(categories: list[str], days: int = 1, min_score: float = 3.0) -> dict:
    """Collect daily arXiv papers"""
    papers = collect_papers(categories, days)
    high_priority = [p for p in papers if p['priority_score'] >= min_score]
    return {
        "total": len(papers),
        "high_priority": len(high_priority),
        "papers": high_priority
    }

@server.tool()
async def get_papers(date: str, min_score: float = 4.0) -> list:
    """Get collected papers from JSON file"""
    import json
    with open(f"Medium/Raw/arxiv-{date}.json") as f:
        data = json.load(f)
    return [p for p in data['papers'] if p['priority_score'] >= min_score]

async def main():
    async with stdio_server() as streams:
        await server.run(streams[0], streams[1])

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

**Step 3: 配置 MCP 客户端**

```json
{
  "mcpServers": {
    "arxiv-daily": {
      "command": "py",
      "args": ["arxiv-daily-mcp.py"]
    }
  }
}
```

---

## 📋 推荐方案：mcporter (方案 A)

**理由:**
- ✅ 无需修改 arxiv-daily 原始脚本
- ✅ mcporter 已安装 (v0.7.3)
- ✅ 配置简单，易于调试
- ✅ 支持多个工具定义

---

## 🔍 实施检查清单

### Phase 1: 准备 (15 分钟)

- [ ] 确认 mcporter 已安装
- [ ] 测试 mcporter 基本功能
- [ ] 创建 arxiv-daily-mcp.json 配置

### Phase 2: 配置 (30 分钟)

- [ ] 定义 MCP 工具 (collect, get_papers)
- [ ] 配置输入参数 schema
- [ ] 配置输出格式

### Phase 3: 测试 (30 分钟)

- [ ] 启动 MCP 服务器
- [ ] 列出可用工具
- [ ] 调用 collect 工具
- [ ] 调用 get_papers 工具
- [ ] 验证输出格式

### Phase 4: 集成 (30 分钟)

- [ ] 配置 Claude Desktop
- [ ] 测试 Claude 调用
- [ ] 创建编排工作流
- [ ] 测试完整流程

### Phase 5: 监控 (持续)

- [ ] 监控首次自动运行
- [ ] 检查错误日志
- [ ] 优化性能

---

## 🛡️ 安全审查

**MCP 服务器权限:**

| 权限 | 范围 | 说明 |
|------|------|------|
| 文件读取 | Medium/Raw/*.json | 只读收集结果 |
| 文件写入 | Medium/Raw/*.json | 仅 arxiv-daily 输出 |
| 网络请求 | arxiv.org | 仅 API 调用 |
| 系统命令 | 无 | 不执行系统命令 |

**风险评估:**
- ✅ 权限最小化
- ✅ 仅访问指定目录
- ✅ 单一可信网络源
- ✅ 无系统命令执行

---

## 📊 预期效果

**工作流:**
```
Claude / Agent
    ↓
MCP Client
    ↓
arxiv-daily MCP Server (via mcporter)
    ↓
collect() → 获取高优先级论文
    ↓
ai-research-os MCP Server
    ↓
analyze_paper() → 生成 P-Note
    ↓
github-sync MCP Server
    ↓
commit() → Git 提交
```

**自动化程度:**
- ✅ 完全自动化
- ✅ 无需人工干预
- ✅ 错误自动重试
- ✅ 状态自动报告

---

## ⚠️ 风险与挑战

**技术风险:**
- ⚠️ mcporter 配置复杂
- ⚠️ MCP 协议版本兼容
- ⚠️ stdio 传输稳定性

**运维风险:**
- ⚠️ MCP 服务器常驻内存
- ⚠️ 需要监控和日志
- ⚠️ 错误处理复杂

**缓解措施:**
- ✅ 详细文档
- ✅ 测试用例
- ✅ 监控告警

---

## 📋 下一步

**立即行动:**

1. **确认 mcporter 功能**
   ```bash
   mcporter --help
   mcporter config list
   ```

2. **创建 MCP 配置**
   - 定义工具 schema
   - 配置输入输出
   - 测试调用

3. **测试完整流程**
   - 手动调用
   - Claude 调用
   - 自动化调用

---

*等待 mcporter 功能确认*
