# MCP 配置总结

**配置日期:** 2026-03-04  
**配置文件:** `D:\OpenClaw\workspace\config\mcporter.json`

---

## 已配置服务器

### 1. Tavily Search 🔍 ✅

| 属性 | 值 |
|------|-----|
| **类型** | HTTP |
| **URL** | https://api.tavily.com/search |
| **认证** | API Key (已配置) |
| **状态** | ✅ 工作正常 |

**可用工具:**
- `search` - 搜索查询

**使用示例:**
```powershell
# PowerShell 直接调用
$apiKey = (Get-Content "C:\Users\华为\.openclaw\credentials\tavily.json" | ConvertFrom-Json).tavily.api_key
$body = @{query="AI Agent"; max_results=5; api_key=$apiKey} | ConvertTo-Json
Invoke-RestMethod -Uri "https://api.tavily.com/search" -Method Post -Body $body -ContentType "application/json"
```

**测试结果:** ✅ 返回 5 条 AI Agent Framework 相关结果 (0.91 秒)

---

### 2. Filesystem 📁 ⚠️

| 属性 | 值 |
|------|-----|
| **类型** | Stdio / HTTP |
| **状态** | ⚠️ Windows 兼容性問題 |

**问题:**
- Stdio 模式在 Windows 上有兼容性问题
- HTTP 模式启动失败 (端口绑定问题)

**替代方案:**
- 直接使用 PowerShell 命令操作文件
- 使用 OpenClaw 内置的 `read`/`write`/`edit` 工具

---

## 快速开始

### ✅ 搜索网络 (Tavily)

```powershell
$apiKey = (Get-Content "C:\Users\华为\.openclaw\credentials\tavily.json" | ConvertFrom-Json).tavily.api_key
$body = @{query="AI Agent 2026"; max_results=5; api_key=$apiKey} | ConvertTo-Json
Invoke-RestMethod -Uri "https://api.tavily.com/search" -Method Post -Body $body -ContentType "application/json"
```

### ⚠️ 文件操作

建议使用 OpenClaw 内置工具:
- `read path="file.md"` - 读取文件
- `write path="file.md" content="..."` - 写入文件
- `edit path="file.md" oldText="..." newText="..."` - 编辑文件

---

## 待配置服务器 (推荐)

| 服务器 | 用途 | 认证方式 |
|--------|------|----------|
| `github` | GitHub API | Personal Access Token |
| `notion` | 笔记管理 | OAuth |
| `linear` | 项目管理 | API Key |
| `slack` | 团队协作 | OAuth |
| `postgres` | PostgreSQL | Connection String |

---

## MCP 工具概览

**mcporter** 是 MCP 客户端工具，支持:

| 功能 | 命令 |
|------|------|
| 列出服务器 | `mcporter list` |
| 配置管理 | `mcporter config list\|add\|remove` |
| 调用工具 | `mcporter call <server.tool> args` |
| OAuth 认证 | `mcporter auth <server>` |
| 代码生成 | `mcporter generate-cli --server <name>` |

---

## 总结

| 项目 | 状态 | 说明 |
|------|------|------|
| Tavily 搜索 | ✅ 可用 | API Key 已配置，测试通过 |
| Filesystem MCP | ⚠️ 不可用 | Windows 兼容性问题 |
| 配置文件 | ✅ 已创建 | `D:\OpenClaw\workspace\config\mcporter.json` |

**建议:** 继续使用 OpenClaw 内置工具进行文件操作，Tavily 搜索可通过 PowerShell 或 mcporter 调用。

---

*使用 `mcporter list` 查看服务器状态*
*使用 `mcporter auth <server>` 进行认证*
