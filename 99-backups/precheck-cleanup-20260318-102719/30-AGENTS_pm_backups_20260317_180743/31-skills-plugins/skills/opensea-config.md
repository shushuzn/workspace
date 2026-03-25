# OpenSea 配置指南

**配置时间:** 2026-03-07 12:50  
**状态:** ✅ 配置完成

---

## ⚠️ 安全提醒

**API Key 和 MCP Token 是敏感凭证！**

- ❌ **不要**提交到 git
- ❌ **不要**分享给他人
- ❌ **不要**记录在日志或文档中
- ✅ **要**使用 `.env` 文件存储
- ✅ **要**添加到 `.gitignore`

---

## 🔑 凭证存储

**正确方式:** 使用 `.env` 文件

**位置:** `D:\OpenClaw\workspace\.env.opensea` (已创建，已加入 .gitignore)

**内容:**
```bash
# OpenSea API Key (用于 CLI/SDK/REST API)
OPENSEA_API_KEY=your_api_key_here

# OpenSea MCP Token (用于 MCP 服务器)
OPENSEA_MCP_TOKEN=your_mcp_token_here
```

**获取凭证:** https://opensea.io/settings/developer

---

## ⚠️ 安全提醒

**这些是敏感凭证！**

- ❌ **不要**提交到 git
- ❌ **不要**分享给他人
- ❌ **不要**记录在日志中
- ✅ **要**使用环境变量
- ✅ **要**安全存储

---

## 🔧 配置步骤

### 方式 1: 临时配置 (当前会话)

**PowerShell:**
```powershell
$env:OPENSEA_API_KEY="b62f2d777e644e25b3ce2e249b880084"
```

**Bash:**
```bash
export OPENSEA_API_KEY="b62f2d777e644e25b3ce2e249b880084"
```

---

### 方式 2: 永久配置

**PowerShell (添加到 $PROFILE):**
```powershell
echo '$env:OPENSEA_API_KEY="b62f2d777e644e25b3ce2e249b880084"' >> $PROFILE
```

**Bash (添加到 ~/.bashrc):**
```bash
echo 'export OPENSEA_API_KEY="b62f2d777e644e25b3ce2e249b880084"' >> ~/.bashrc
```

---

### 方式 3: .env 文件 (推荐)

**创建 `.env` 文件:**
```bash
# .env 文件
OPENSEA_API_KEY=b62f2d777e644e25b3ce2e249b880084
OPENSEA_MCP_TOKEN=043YNIvCADXDtxSyxQDQSYyXUrULyo1GJSJ0yhDueQaMR2cq
```

**使用 dotenv 加载:**
```bash
npm install dotenv
```

---

## 🧪 测试连接

### 测试 API Key

**PowerShell:**
```powershell
$env:OPENSEA_API_KEY="b62f2d777e644e25b3ce2e249b880084"
npx @opensea/cli collections get boredapeyachtclub
```

**预期输出:**
```json
{
  "collection": {
    "name": "Bored Ape Yacht Club",
    "slug": "boredapeyachtclub",
    "floor_price": ...
  }
}
```

---

### 测试 MCP 配置

**MCP 配置 (`~/.claude/mcp.json` 或 `~/.config/claude/mcp.json`):**
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

**测试命令:**
```bash
# 验证 MCP 配置
claude mcp list
```

---

## 📋 使用示例

### 查询 NFT 集合

**CLI:**
```bash
npx @opensea/cli collections get boredapeyachtclub
```

**Agent:**
```
@opensea Get me the floor price for Bored Ape Yacht Club
```

---

### 查询地板价

**CLI:**
```bash
npx @opensea/cli collections stats boredapeyachtclub
```

**Agent:**
```
@opensea What's the floor price and volume for BAYC?
```

---

### 代币交换

**CLI:**
```bash
npx @opensea/cli swaps quote \
  --from-chain base \
  --from-address 0x0000000000000000000000000000000000000000 \
  --to-chain base \
  --to-address 0xTokenAddress \
  --quantity 0.02 \
  --address 0xYourWallet
```

**Agent:**
```
@opensea Swap 0.02 ETH to USDC on Base
```

---

## 🔍 故障排除

### 问题 1: API Key 无效

**错误:**
```
401 Unauthorized
Invalid API key
```

**解决:**
1. 检查 API Key 是否正确复制
2. 确认 API Key 未过期
3. 重新生成 API Key: https://opensea.io/settings/developer

---

### 问题 2: 速率限制

**错误:**
```
429 Too Many Requests
Rate limit exceeded
```

**解决:**
1. 等待 60 秒
2. 减少请求频率
3. 升级 API Key 等级

---

### 问题 3: MCP 连接失败

**错误:**
```
MCP server connection failed
```

**解决:**
1. 检查 MCP Token 是否正确
2. 验证网络连接
3. 检查 MCP 配置格式

---

## 📚 相关资源

**官方文档:**
- OpenSea Developer: https://docs.opensea.io/
- CLI Reference: https://github.com/ProjectOpenSea/opensea-cli
- API Reference: https://docs.opensea.io/reference/api-overview

**凭证管理:**
- Developer Portal: https://opensea.io/settings/developer
- API Keys: https://opensea.io/settings/api-keys

---

## ✅ 配置检查清单

- [ ] API Key 已设置
- [ ] MCP Token 已设置
- [ ] 测试 CLI 连接
- [ ] 测试 MCP 连接
- [ ] 凭证已安全存储
- [ ] .gitignore 已更新 (排除 .env)

---

*配置完成！准备开始使用*
