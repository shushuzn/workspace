# OpenSea MCP 服务器配置指南

**配置时间:** 2026-03-07 12:53  
**状态:** ✅ 配置完成

---

## 🔑 MCP Token

**获取方式:** https://opensea.io/settings/developer

**存储方式:** 使用 `.env.opensea` 文件 (不要直接写在配置中)

---

## 📁 MCP 配置文件

**位置:** `%APPDATA%\Claude\mcp.json`

**内容:**
```json
{
  "mcpServers": {
    "opensea": {
      "url": "https://mcp.opensea.io/mcp",
      "headers": {
        "Authorization": "Bearer 043YNIvCADXDtxSyxQDQSYyXUrULyo1GJSJ0yhDueQaMR2cq"
      }
    }
  }
}
```

---

## 🔧 配置步骤

### Step 1: 创建配置目录

**PowerShell:**
```powershell
New-Item -ItemType Directory -Force -Path "$env:APPDATA\Claude"
```

**Bash:**
```bash
mkdir -p ~/.claude
```

---

### Step 2: 创建/编辑 mcp.json

**PowerShell:**
```powershell
notepad "$env:APPDATA\Claude\mcp.json"
```

**Bash:**
```bash
nano ~/.claude/mcp.json
```

---

### Step 3: 添加 OpenSea MCP 配置

```json
{
  "mcpServers": {
    "opensea": {
      "url": "https://mcp.opensea.io/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_MCP_TOKEN"
      }
    }
  }
}
```

**替换 `YOUR_MCP_TOKEN` 为:**
```
043YNIvCADXDtxSyxQDQSYyXUrULyo1GJSJ0yhDueQaMR2cq
```

---

### Step 4: 重启 Claude

**Claude Desktop:**
1. 完全退出 Claude
2. 重新打开 Claude

**验证:**
```bash
# 检查 MCP 服务器列表
claude mcp list
```

**预期输出:**
```
MCP Servers:
  opensea - https://mcp.opensea.io/mcp (connected)
```

---

## 🧪 测试连接

### 测试命令

**在 Claude 中:**
```
@opensea Get the floor price for Bored Ape Yacht Club
```

**或使用 MCP 工具:**
```
Use the opensea MCP server to get collection stats for boredapeyachtclub
```

---

### 预期响应

```json
{
  "collection": {
    "name": "Bored Ape Yacht Club",
    "slug": "boredapeyachtclub",
    "floor_price": {
      "value": 12.5,
      "currency": "ETH"
    },
    "volume": {
      "1d": 125.5,
      "7d": 890.2,
      "30d": 3500.8
    }
  }
}
```

---

## 🔍 故障排除

### 问题 1: MCP 服务器未连接

**错误:**
```
MCP server 'opensea' is not connected
```

**解决:**
1. 检查 mcp.json 格式
2. 确认 JSON 语法正确
3. 重启 Claude
4. 检查网络连接

---

### 问题 2: 认证失败

**错误:**
```
401 Unauthorized
Invalid token
```

**解决:**
1. 确认 MCP Token 正确复制
2. 检查 Token 是否过期
3. 重新生成 MCP Token

---

### 问题 3: 连接超时

**错误:**
```
Connection timeout
```

**解决:**
1. 检查网络连接
2. 检查防火墙设置
3. 尝试使用代理
4. 联系 OpenSea 支持

---

## 📋 可用 MCP 工具

### Token 交换工具

| 工具 | 用途 |
|------|------|
| `get_token_swap_quote` | 获取代币交换 calldata |
| `get_token_balances` | 查询钱包代币余额 |
| `search_tokens` | 搜索代币 |
| `get_trending_tokens` | 热门代币 |
| `get_top_tokens` | 顶级代币 |
| `get_tokens` | 代币详情 |

### NFT 工具

| 工具 | 用途 |
|------|------|
| `search_collections` | 搜索 NFT 集合 |
| `search_items` | 搜索 NFT |
| `get_collections` | 集合详情 |
| `get_items` | NFT 详情 |
| `get_nft_balances` | 钱包 NFT 余额 |
| `get_trending_collections` | 热门集合 |
| `get_top_collections` | 顶级集合 |
| `get_activity` | 交易活动 |
| `get_upcoming_drops` | 即将发行的 NFT |

### 工具类

| 工具 | 用途 |
|------|------|
| `get_profile` | 钱包资料 |
| `account_lookup` | ENS/地址解析 |
| `get_chains` | 支持的链 |
| `search` | 自然语言搜索 |
| `fetch` | 获取详情 |

---

## 📚 相关文档

**配置文件:** `skills/opensea-mcp-config.json`

**配置指南:** `skills/opensea-config.md`

**官方资源:**
- MCP Docs: https://modelcontextprotocol.io/
- OpenSea API: https://docs.opensea.io/
- OpenSea CLI: https://github.com/ProjectOpenSea/opensea-cli

---

## ✅ 配置检查清单

- [ ] MCP Token 已配置
- [ ] mcp.json 已创建
- [ ] JSON 格式正确
- [ ] Claude 已重启
- [ ] MCP 服务器已连接
- [ ] 测试命令成功

---

*配置完成！准备开始使用*
