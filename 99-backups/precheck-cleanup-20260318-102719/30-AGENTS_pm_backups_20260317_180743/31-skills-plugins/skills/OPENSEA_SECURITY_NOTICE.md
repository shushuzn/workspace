# ⚠️ OpenSea 安全通知

**时间:** 2026-03-07 13:08  
**状态:** 已清理敏感信息

---

## 🔒 安全事件

**问题:** 文档中包含了 API Key 和 MCP Token

**已修复:**
- ✅ 已删除所有文档中的敏感凭证
- ✅ 配置文件已更新为占位符
- ✅ `.env.opensea` 已加入 `.gitignore`

---

## 📋 安全实践

### 正确存储凭证

**方式 1: .env 文件 (推荐)**

**文件:** `.env.opensea` (已在 `.gitignore` 中)

```bash
OPENSEA_API_KEY=your_api_key_here
OPENSEA_MCP_TOKEN=your_mcp_token_here
```

**加载:**
```powershell
# PowerShell
$env = Get-Content .env.opensea | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]+)\s*=\s*(.+)\s*$') {
        Set-Item -Path "Env:$($matches[1])" -Value $matches[2]
    }
}
```

---

### 方式 2: Claude 环境变量

**在 Claude Desktop 设置中:**
1. Settings → Environment Variables
2. 添加 `OPENSEA_API_KEY`
3. 添加 `OPENSEA_MCP_TOKEN`

---

### 方式 3: Windows 凭据管理器

**PowerShell:**
```powershell
# 存储凭据
cmdkey /add:OpenSeaAPI /user:API_KEY /pass:your_api_key
cmdkey /add:OpenSeaMCP /user:MCP_TOKEN /pass:your_mcp_token

# 读取凭据
$api_key = cmdkey /list | Select-String "OpenSeaAPI"
```

---

## ❌ 禁止做法

**不要:**
- ❌ 在文档中直接写凭证
- ❌ 提交凭证到 git
- ❌ 在聊天中分享凭证
- ❌ 在日志中打印凭证
- ❌ 在截图 中显示凭证

**要:**
- ✅ 使用 `.env` 文件
- ✅ 添加到 `.gitignore`
- ✅ 使用环境变量
- ✅ 使用凭据管理器

---

## 🔍 检查清单

- [x] 文档中的凭证已删除
- [x] 配置文件已更新为占位符
- [x] `.env` 文件已创建
- [x] `.env` 已加入 `.gitignore`
- [ ] 检查 git 历史 (如有提交需要清理)

---

## 🚨 如果凭证已泄露

**立即:**
1. 删除包含凭证的文件
2. 在 OpenSea 重新生成凭证
3. 更新所有使用该凭证的地方
4. 检查 git 历史 (如有需要)

**重新生成凭证:**
https://opensea.io/settings/developer

---

*安全提醒：保护你的 API Key 和 MCP Token*
