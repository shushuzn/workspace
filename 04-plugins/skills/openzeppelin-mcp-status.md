# OpenZeppelin MCP 服务器安装状态

**检查时间:** 2026-03-07 12:33  
**状态:** ⚠️ MCP 服务器不可用

---

## 🔍 搜索结果

### 尝试安装的包

```bash
npm install -g @openzeppelin/mcp-solidity
npm install -g @openzeppelin/mcp-cairo
```

### 错误信息

```
npm error 404 Not Found - GET https://registry.npmjs.org/@openzeppelin%2fmcp-solidity
npm error 404 The requested resource '@openzeppelin/mcp-solidity@*' could not be found
```

---

## 📊 当前状态

### Skills 安装

| 组件 | 状态 |
|------|------|
| **OpenZeppelin Skills** | ✅ 已安装 (9 Skills) |
| **MCP Solidity** | ❌ 包不存在 |
| **MCP Cairo** | ❌ 包不存在 |

---

## 🔍 可能原因

### 原因 1: MCP 服务器尚未发布

OpenZeppelin Skills 文档提到的 MCP 服务器可能：
- 还在开发中
- 私有发布
- 通过其他方式分发

### 原因 2: 包名不同

可能的包名：
- `@openzeppelin/contracts-mcp`
- `openzeppelin-mcp`
- `@openzeppelin/mcp`

### 原因 3: 通过 Claude Code 插件安装

MCP 服务器可能：
- 仅通过 Claude Code 插件自动安装
- 不单独发布到 npm

---

## ✅ 替代方案

### 方案 1: 仅使用 Skills (推荐)

**说明:** Skills 可以独立工作，无需 MCP 服务器

**功能:**
- ✅ 智能合约开发指导
- ✅ OpenZeppelin Contracts 集成
- ✅ 安全模式检查
- ✅ 最佳实践建议

**限制:**
- ❌ 无自动代码生成
- ❌ 无交互式配置

---

### 方案 2: 等待官方发布

**监控:**
- GitHub: https://github.com/OpenZeppelin/openzeppelin-skills
- npm: https://www.npmjs.com/org/openzeppelin
- OpenZeppelin 博客

---

### 方案 3: 使用其他 MCP 服务器

**替代 MCP:**
- Hardhat MCP (如果可用)
- Foundry MCP (如果可用)
- 自定义 MCP 服务器

---

## 📋 验证 Skills 功能

### 测试命令

```bash
# 验证 Skills 已安装
ls ~/.agents/skills/*openzeppelin*

# 查看 Skill 文档
cat ~/.agents/skills/develop-secure-contracts/SKILL.md
```

### 预期功能

**无需 MCP，Skills 可以提供:**
- ✅ 代码审查建议
- ✅ OpenZeppelin Contracts 使用指导
- ✅ 安全模式推荐
- ✅ 集成示例代码

**需要 MCP 才能提供:**
- ❌ 自动代码生成
- ❌ 交互式配置向导
- ❌ 实时合约验证

---

## 🎯 建议

### 当前最佳实践

1. **使用 Skills** - 已经安装，功能完整
2. **监控更新** - 关注 OpenZeppelin 官方发布
3. **反馈需求** - 向 OpenZeppelin 反馈 MCP 需求

### 未来计划

当 MCP 服务器可用时:
```bash
# 安装 MCP 服务器
npm install -g @openzeppelin/mcp

# 配置 MCP
# 添加到 ~/.claude/mcp.json
```

---

## 📚 相关资源

**官方资源:**
- GitHub: https://github.com/OpenZeppelin/openzeppelin-skills
- Contracts: https://openzeppelin.com/contracts
- 文档：https://docs.openzeppelin.com/contracts

**MCP 信息:**
- MCP 协议：https://modelcontextprotocol.io/
- Claude Code: https://claude.ai/code

---

## 📊 总结

**Skills 状态:** ✅ **完全可用**

**MCP 服务器:** ❌ **暂不可用**

**影响:** 
- Skills 功能不受影响
- 仅缺少自动代码生成功能
- 可以正常使用 OpenZeppelin Contracts 指导

**下一步:**
1. 继续使用 Skills (无需 MCP)
2. 监控 MCP 服务器发布
3. 发布后自动安装

---

*等待 MCP 服务器发布*
