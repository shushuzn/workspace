# 📦 Git 工作流配置

**创建日期:** 2026-03-27

---

## Git 配置

```bash
# 用户信息
git config --global user.name "Feishu"
git config --global user.email "feishu@openclaw.ai"

# 默认分支
git config --global init.defaultBranch main

# 拉取策略
git config --global pull.rebase false

# 推送策略
git config --global push.default current
```

---

## 分支策略

```
main          # 主分支，稳定版本
├── develop   # 开发分支
├── feature/* # 功能分支
├── fix/*     # 修复分支
└── release/* # 发布分支
```

### 分支命名

```
feature/{ticket-id}-{short-description}
fix/{ticket-id}-{short-description}
docs/{description}
refactor/{description}
```

示例:
```
feature/ABC-123-user-auth
fix/ABC-456-login-bug
```

---

## 提交规范

### 格式

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### 类型

| 类型 | 说明 |
|------|------|
| feat | 新功能 |
| fix | Bug 修复 |
| docs | 文档更新 |
| style | 代码格式 |
| refactor | 重构 |
| test | 测试 |
| chore | 构建/工具 |

### 示例

```
feat(auth): 添加 GitHub OAuth 登录

- 实现 GitHub OAuth 流程
- 添加用户信息同步
- 添加登录状态管理

Closes #123
```

---

## 提交检查

### Pre-commit Hook

```bash
# 安装钩子
setup_hooks.bat

# 或手动
cp .git-hooks/pre-commit .git/hooks/
```

### 检查项

- [ ] 代码格式检查
- [ ] 工具验证
- [ ] 工具命名规范
- [ ] 测试运行 (可选)

---

## 常用命令

### 日常工作流

```bash
# 创建功能分支
git checkout -b feature/ABC-123-new-feature

# 提交更改
git add .
git commit -m "feat(scope): description"

# 推送
git push -u origin feature/ABC-123-new-feature

# 创建 PR
gh pr create --title "feat: new feature" --body "Description"
```

### 审查后合并

```bash
# 更新分支
git fetch origin
git rebase origin/main

# 解决冲突后
git add .
git rebase --continue

# 强制推送 (谨慎使用)
git push --force-with-lease
```

---

## 协作规则

| 规则 | 说明 |
|------|------|
| PR 必须审查 | 不能自己合并自己的 PR |
| 分支及时清理 | 合并后删除远程分支 |
| 保持最新 | 经常 rebase main |
| 提交信息清晰 | 方便 Code Review |

---

## 冲突解决

### 策略

1. **先拉取最新**: `git fetch && git rebase origin/main`
2. **逐个解决**: 不要一次性解决所有冲突
3. **测试验证**: 解决后运行测试
4. **沟通**: 有疑问及时沟通

### 命令

```bash
# 查看冲突
git status

# 解决后标记
git add <resolved-file>

# 继续 rebase
git rebase --continue

# 放弃 rebase
git rebase --abort
```

---

## 快捷命令

| 命令 | 执行 |
|------|------|
| `git状态` | 查看当前状态 |
| `git提交` | 交互式提交 |
| `git推送` | 推送到远程 |
| `git分支` | 列出分支 |
| `git清理` | 清理已合并分支 |
