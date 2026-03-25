# MCP 服务器集成方案

**创建时间:** 2026-03-07 03:59  
**状态:** 📋 设计中

---

## 🎯 集成目标

使用 MCP (Model Context Protocol) 服务器实现 arxiv-daily 和 AI Research OS 的完全自动化集成。

---

## 📊 MCP 架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Desktop / Agent                    │
│                         (MCP Client)                         │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   arxiv-daily   │ │  ai-research-os │ │   github-sync   │
│    MCP Server   │ │    MCP Server   │ │    MCP Server   │
│                 │ │                 │ │                 │
│ - qmd_search    │ │ - analyze_paper │ │ - commit        │
│ - qmd_get       │ │ - generate_note │ │ - push          │
│ - qmd_status    │ │ - compare_papers│ │                 │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

---

## 🔧 配置步骤

### Step 1: 安装 MCP 服务器

**arxiv-daily MCP:**
```bash
# 检查是否支持 MCP
py -m arxiv_daily mcp --help

# 如果支持，安装为 MCP 服务器
# 如果不支持，需要扩展脚本
```

**ai-research-os MCP:**
```bash
# 检查是否支持 MCP
py -m ai_research_os mcp --help
```

---

### Step 2: 配置 Claude Desktop

**配置文件:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "arxiv-daily": {
      "command": "py",
      "args": ["-m", "arxiv_daily", "mcp"]
    },
    "ai-research-os": {
      "command": "py",
      "args": ["-m", "ai_research_os", "mcp"]
    },
    "github-sync": {
      "command": "gh",
      "args": ["mcp"]
    }
  }
}
```

---

### Step 3: 创建工作流自动化

**方案 A: Claude 自动触发**

```
1. Claude 定期调用 arxiv-daily MCP
   ↓
2. 获取高优先级论文列表
   ↓
3. 对每篇论文调用 ai-research-os MCP
   ↓
4. 生成 P-Note/C-Note
   ↓
5. 调用 github-sync MCP 提交
```

**方案 B: 独立 MCP 编排器**

```python
# mcp-orchestrator.py
import asyncio
from mcp import Client

async def daily_workflow():
    async with Client("arxiv-daily") as arxiv:
        papers = await arxiv.call("get_daily_papers", min_score=4.0)
    
    async with Client("ai-research-os") as research:
        for paper in papers[:3]:
            note = await research.call("analyze_paper", paper)
            await research.call("save_note", note)
    
    async with Client("github-sync") as git:
        await git.call("commit_and_push", "Daily papers analyzed")

# 配置定时任务
asyncio.run(daily_workflow())
```

---

## ⚠️ 前提条件检查

### 检查 MCP 支持

**arxiv-daily:**
- [ ] 检查是否支持 MCP 模式
- [ ] 如果不支持，需要扩展
- [ ] 测试 MCP 服务器启动

**ai-research-os:**
- [ ] 检查是否支持 MCP 模式
- [ ] 如果不支持，需要扩展
- [ ] 测试 MCP 服务器启动

### 检查 MCP 客户端

- [ ] Claude Desktop 已安装
- [ ] 或 OpenClaw MCP 客户端已配置
- [ ] 或自定义 MCP 客户端已准备

---

## 🛡️ 安全审查

**MCP 服务器权限:**

| 服务器 | 文件访问 | 网络请求 | 系统命令 |
|--------|----------|----------|----------|
| arxiv-daily | 只读 (输出目录) | arxiv.org | 无 |
| ai-research-os | 读写 (笔记目录) | arxiv.org, GitHub | 无 |
| github-sync | 只读 (Git 仓库) | GitHub | git 命令 |

**风险评估:**
- ✅ 所有服务器都是本地运行
- ✅ 网络请求仅限可信源
- ✅ 无系统级命令执行
- ✅ 文件访问限制在 workspace

---

## 📋 实施步骤

### Phase 1: 检查 MCP 支持 (15 分钟)

1. 检查 arxiv-daily 是否支持 MCP
2. 检查 ai-research-os 是否支持 MCP
3. 如果不支持，评估扩展工作量

### Phase 2: 配置 MCP 客户端 (30 分钟)

1. 安装/配置 MCP 客户端
2. 配置 claude_desktop_config.json
3. 测试各服务器连接

### Phase 3: 创建工作流 (1 小时)

1. 编写 MCP 编排脚本
2. 配置定时任务
3. 测试完整流程

### Phase 4: 监控与优化 (持续)

1. 监控首次自动运行
2. 检查输出质量
3. 优化筛选规则

---

## 🤔 优缺点分析

### 优点

- ✅ **完全自动化** - 无需人工干预
- ✅ **模块化** - 各服务独立，易于维护
- ✅ **可扩展** - 容易添加新服务
- ✅ **标准化** - MCP 是开放协议

### 缺点

- ⚠️ **复杂度高** - 需要配置多个组件
- ⚠️ **依赖多** - MCP 服务器 + 客户端 + 编排器
- ⚠️ **调试困难** - 分布式系统调试复杂
- ⚠️ **资源消耗** - 多个服务器常驻内存

---

## 🎯 建议

**如果选择 MCP 方案:**

1. **先验证 MCP 支持** - 检查现有技能是否支持
2. **从小规模开始** - 先手动触发，再自动化
3. **详细日志** - 记录每个步骤，便于调试
4. **监控资源** - 监控内存和 CPU 使用

**替代方案:**

如果 MCP 太复杂，可以考虑:
- **PowerShell 桥接** (方案 1) - 简单直接
- **手动触发** - 需要时手动运行

---

## 📋 下一步

**立即行动:**

1. 检查 arxiv-daily MCP 支持
   ```bash
   py -m arxiv_daily --help | Select-String "mcp"
   ```

2. 检查 ai-research-os MCP 支持
   ```bash
   py -m ai_research_os --help | Select-String "mcp"
   ```

3. 根据结果决定:
   - 如果支持 → 继续 MCP 方案
   - 如果不支持 → 选择 PowerShell 桥接

---

*等待 MCP 支持检查结果*
