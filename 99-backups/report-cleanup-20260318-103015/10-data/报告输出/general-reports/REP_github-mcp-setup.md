# GitHub MCP 配置总结

**配置日期:** 2026-03-04  
**认证状态:** ✅ 已登录 (shushuzn)

---

## 配置说明

### ⚠️ GitHub 不是标准 MCP 服务器

GitHub API 不支持标准 MCP 协议，mcporter 无法直接连接。

**替代方案:** 使用 `gh CLI` (GitHub 官方命令行工具)

---

## ✅ gh CLI 已认证

| 属性 | 值 |
|------|-----|
| **账户** | shushuzn |
| **Token 范围** | gist, read:org, repo |
| **协议** | HTTPS |
| **状态** | ✅ 已登录 |

---

## 🔧 可用的 GitHub 操作

### 仓库操作
```powershell
# 查看仓库信息
gh repo view shushuzn/obsidian-sync --json name,description,stargazerCount

# 列出仓库
gh repo list --limit 10

# 创建仓库
gh repo create my-new-repo --public
```

### Issue 操作
```powershell
# 列出 Issue
gh issue list --repo shushuzn/obsidian-sync --limit 5

# 创建 Issue
gh issue create --title "Bug" --body "Description"

# 查看 Issue
gh issue view 123
```

### PR 操作
```powershell
# 列出 PR
gh pr list --limit 5

# 创建 PR
gh pr create --title "Fix" --body "Description"

# 查看 PR 状态
gh pr status
```

### CI/CD 操作
```powershell
# 查看 CI 运行
gh run list --limit 5

# 查看运行日志
gh run view 123 --log
```

---

## 📊 测试结果

### ✅ 仓库查询
```json
{
  "name": "obsidian-sync",
  "description": "",
  "stargazerCount": 0,
  "forkCount": 0,
  "updatedAt": "2026-03-02T20:01:19Z"
}
```

### ✅ Issue 查询
```
[]  (无 Issue)
```

---

## 📦 MCP 配置状态

| 服务器 | 状态 | 说明 |
|--------|------|------|
| **Tavily** | ✅ 可用 | HTTP API 直接调用 |
| **Filesystem** | ⚠️ 不可用 | Windows 兼容性问题 |
| **GitHub** | ⚠️ 非 MCP | 使用 gh CLI 替代 |

---

## 快速参考

### 使用 gh CLI 操作 GitHub

```powershell
# 认证状态
gh auth status

# 重新认证
gh auth login -w

# 查看帮助
gh help
```

### 常用命令

| 操作 | 命令 |
|------|------|
| 认证 | `gh auth login -w` |
| 仓库 | `gh repo view/list/create` |
| Issue | `gh issue list/view/create` |
| PR | `gh pr list/view/create` |
| CI | `gh run list/view` |

---

## 总结

- ✅ GitHub 已认证 (gh CLI)
- ⚠️ GitHub 不是标准 MCP 服务器
- ✅ 使用 gh CLI 可实现所有 GitHub 操作
- ✅ 已测试仓库查询和 Issue 查询

---

*使用 `gh help` 查看完整命令列表*
*使用 `gh auth status` 检查认证状态*
