# MCP Token 安全修复指南

**日期:** 2026-03-21
**优先级:** 🔴 CRITICAL

---

## 问题描述

`mcp.json` 中存在敏感信息暴露：

| 服务 | 风险 | 问题 |
|------|------|------|
| GitHub | 🔴 CRITICAL | PAT 完全暴露 |
| YouTube | 🔴 CRITICAL | API Key 完全暴露 |
| **额外问题** | ⚠️ | YouTube 使用了 GitHub Token 作为 API Key |

---

## 修复步骤

### 方案 1：手动设置环境变量（推荐）

**PowerShell 管理员模式：**

```powershell
# 设置 GitHub Token
[System.Environment]::SetEnvironmentVariable(
    "GITHUB_TOKEN",
    "YOUR_GITHUB_TOKEN_HERE",
    "User"
)

# 设置 YouTube API Key（需要替换为真实 Key）
[System.Environment]::SetEnvironmentVariable(
    "YOUTUBE_API_KEY",
    "YOUR_YOUTUBE_API_KEY_HERE",
    "User"
)

# 验证
Get-ChildItem Env: | Where-Object { $_.Name -match "TOKEN|API_KEY" }
```

### 方案 2：使用安全配置脚本

运行 `MCP-SECURITY-FIX.ps1`（见下方）

---

## 修改 mcp.json

手动编辑 `c:\Users\华为\AppData\Roaming\Trae CN\User\mcp.json`：

```json
{
  "mcpServers": {
    "GitHub": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "Youtube": {
      "command": "npx",
      "args": ["-y", "zubeid-youtube-mcp-server"],
      "env": {
        "YOUTUBE_API_KEY": "${YOUTUBE_API_KEY}"
      }
    }
  }
}
```

**注意：** Trae CN 可能不支持 `${VAR}` 语法，需要重启 Trae CN 或手动填入环境变量。

---

## 验证步骤

1. 重启 Trae CN
2. 测试 GitHub MCP：创建一个仓库
3. 测试 YouTube MCP：搜索视频

---

## GitHub Token 轮换建议

**立即行动：**
1. 访问 https://github.com/settings/tokens
2. 撤销当前 Token
3. 创建新 Token（仅授予必要权限）
4. 更新环境变量

**建议权限：**
- repo (全部)
- workflow (如果使用 GitHub Actions)
