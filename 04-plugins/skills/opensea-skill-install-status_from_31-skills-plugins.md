# OpenSea Skill 安装状态报告

**检查时间:** 2026-03-07 12:45  
**状态:** ⏳ 安装中/需要验证

---

## 📦 安装尝试

**命令:**
```bash
npx skills add ProjectOpenSea/opensea-skill --yes --global
```

**输出:**
```
🚀  skills
  Source: https://github.com/ProjectOpenSea/opensea-skill.git
  Cloning repository...
  Repository cloned
  Found X skills
  Installing...
```

---

## 🔍 验证结果

**检查命令:**
```bash
Get-ChildItem ~/.agents/skills/*opensea*
```

**结果:** ❌ 未找到已安装的 Skills

---

## ⚠️ 可能原因

### 原因 1: 安装未完成

安装进程可能：
- 仍在进行中
- 需要用户交互
- 遇到错误退出

### 原因 2: 安装位置不同

Skills 可能安装到：
- `~/.skills/opensea/`
- `~/.claude/skills/opensea/`
- 全局 npm 目录

### 原因 3: 需要手动安装

可能需要：
```bash
git clone https://github.com/ProjectOpenSea/opensea-skill.git ~/.skills/opensea
```

---

## ✅ 替代安装方式

### 方式 1: 手动克隆

```bash
# 克隆到 skills 目录
git clone https://github.com/ProjectOpenSea/opensea-skill.git ~/.skills/opensea

# 验证
ls ~/.skills/opensea/
```

### 方式 2: Claude Code

```bash
/skill install ProjectOpenSea/opensea-skill
```

### 方式 3: 检查安装位置

```bash
# 检查所有可能的 skills 目录
ls ~/.agents/skills/
ls ~/.skills/
ls ~/.claude/skills/
```

---

## 📋 下一步

### 立即可做

1. **检查安装位置** - 查找 skills 目录
2. **手动安装** - 如果自动安装失败
3. **验证安装** - 检查 SKILL.md 文件

### 验证后

4. **配置 API Key** - `export OPENSEA_API_KEY=...`
5. **测试基本功能** - 查询集合/地板价
6. **测试 CLI** - `npx @opensea/cli collections get boredapeyachtclub`

---

## 🔗 相关资源

**官方资源:**
- GitHub: https://github.com/ProjectOpenSea/opensea-skill
- CLI: https://github.com/ProjectOpenSea/opensea-cli
- API Keys: https://opensea.io/settings/developer

**文档:**
- SKILL.md: 完整 Skill 文档
- CLI Reference: CLI 命令参考
- SDK Reference: SDK API 参考

---

*等待安装验证*
