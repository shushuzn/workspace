# OpenZeppelin Skills - Claude Code 插件安装指南

**创建时间:** 2026-03-07 12:26  
**状态:** 📋 准备安装

---

## 🚀 安装步骤

### Step 1: 添加插件到市场

**命令:**
```bash
/plugin marketplace add OpenZeppelin/openzeppelin-skills
```

**预期输出:**
```
✅ Added OpenZeppelin/openzeppelin-skills to marketplace
📦 9 skills available
```

---

### Step 2: 安装插件

**命令:**
```bash
/plugin install openzeppelin-skills
```

**预期输出:**
```
📦 Installing openzeppelin-skills...
✅ Installed 9 skills:
   - develop-secure-contracts
   - setup-solidity-contracts
   - setup-cairo-contracts
   - setup-stylus-contracts
   - setup-stellar-contracts
   - upgrade-solidity-contracts
   - upgrade-cairo-contracts
   - upgrade-stylus-contracts
   - upgrade-stellar-contracts

🔧 Installing MCP servers...
✅ MCP servers installed and configured
```

---

### Step 3: 验证安装

**命令:**
```bash
/plugin list
```

**预期输出:**
```
📦 Installed plugins:
   - openzeppelin-skills (9 skills, MCP enabled)
```

---

### Step 4: 测试功能

**命令:**
```bash
# 测试 Solidity 合约开发
@openzeppelin develop-secure-contracts create ERC20 token

# 或测试项目设置
@openzeppelin setup-solidity-contracts new-project
```

---

## 🔧 MCP 服务器配置

### 自动配置

Claude Code 插件会自动配置 MCP 服务器。

**配置文件:** `~/.claude/mcp.json`

**预期内容:**
```json
{
  "mcpServers": {
    "openzeppelin-solidity": {
      "command": "npx",
      "args": ["@openzeppelin/mcp-solidity"]
    },
    "openzeppelin-cairo": {
      "command": "npx",
      "args": ["@openzeppelin/mcp-cairo"]
    },
    "openzeppelin-stylus": {
      "command": "npx",
      "args": ["@openzeppelin/mcp-stylus"]
    },
    "openzeppelin-stellar": {
      "command": "npx",
      "args": ["@openzeppelin/mcp-stellar"]
    }
  }
}
```

---

### 手动验证

**命令:**
```bash
# 检查 MCP 服务器
npx @openzeppelin/mcp-solidity --version

# 测试 MCP 连接
npx @openzeppelin/mcp-solidity --help
```

---

## 📋 可用 Skills

### 开发 Skills

| Skill | 用途 | 链 |
|-------|------|-----|
| **develop-secure-contracts** | 开发安全智能合约 | 通用 |

### 设置 Skills

| Skill | 用途 | 链 |
|-------|------|-----|
| **setup-solidity-contracts** | 设置 Solidity 项目 | Ethereum |
| **setup-cairo-contracts** | 设置 Cairo 项目 | Starknet |
| **setup-stylus-contracts** | 设置 Stylus 项目 | Arbitrum |
| **setup-stellar-contracts** | 设置 Stellar 项目 | Stellar |

### 升级 Skills

| Skill | 用途 | 链 |
|-------|------|-----|
| **upgrade-solidity-contracts** | 升级 Solidity 合约 | Ethereum |
| **upgrade-cairo-contracts** | 升级 Cairo 合约 | Starknet |
| **upgrade-stylus-contracts** | 升级 Stylus 合约 | Arbitrum |
| **upgrade-stellar-contracts** | 升级 Stellar 合约 | Stellar |

---

## 🎯 使用示例

### 示例 1: 创建 ERC-20 代币

```
@openzeppelin develop-secure-contracts create ERC20 token with:
- name: MyToken
- symbol: MYT
- initialSupply: 1000000
- pausable: true
- mintable: true
```

### 示例 2: 设置 Solidity 项目

```
@openzeppelin setup-solidity-contracts new-project my-defi-protocol
```

### 示例 3: 添加 Pausable 功能

```
@openzeppelin develop-secure-contracts add pausable to existing contract
```

### 示例 4: 升级合约

```
@openzeppelin upgrade-solidity-contracts make upgradeable
```

---

## ⚠️ 故障排除

### 问题 1: 插件未找到

**错误:**
```
Plugin not found: OpenZeppelin/openzeppelin-skills
```

**解决:**
```bash
# 检查网络连接
ping github.com

# 重试添加
/plugin marketplace add OpenZeppelin/openzeppelin-skills
```

---

### 问题 2: MCP 服务器安装失败

**错误:**
```
Failed to install MCP servers
```

**解决:**
```bash
# 手动安装 MCP 服务器
npm install -g @openzeppelin/mcp-solidity
npm install -g @openzeppelin/mcp-cairo

# 验证安装
npx @openzeppelin/mcp-solidity --version
```

---

### 问题 3: Skills 未激活

**错误:**
```
Skill not found: develop-secure-contracts
```

**解决:**
```bash
# 重新安装
/plugin uninstall openzeppelin-skills
/plugin install openzeppelin-skills

# 验证
/plugin list
```

---

## 📊 验证清单

安装完成后，检查以下项目：

- [ ] 插件已添加到市场
- [ ] 9 个 Skills 已安装
- [ ] MCP 服务器已配置
- [ ] `~/.claude/mcp.json` 已更新
- [ ] 可以调用 Skills
- [ ] MCP 服务器正常工作

---

## 🎉 完成！

安装成功后，你可以：

1. **开发安全合约** - 使用 OpenZeppelin Contracts
2. **多链部署** - Solidity/Cairo/Stylus/Stellar
3. **合约升级** - 使用代理模式
4. **安全审计** - 使用 OpenZeppelin 工具

---

*准备开始安装*
