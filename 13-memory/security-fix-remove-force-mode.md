# 安全修复 - 移除 --force 跳过选项

**日期:** 2026-03-20
**问题:** git_commit_helper.py 添加了 --force 选项，允许跳过 pre-commit hook

---

## 问题

**用户指出:** "禁止跳过 session"

**根本问题:**
- ❌ 添加了 `--force` 选项
- ❌ 允许 `--no-verify` 跳过 pre-commit hook
- ❌ 违反了"无 session 不执行"的核心原则

---

## 修复

### 1. 移除 --force 参数

**修改前:**
```python
def main():
    message = sys.argv[1]
    force_mode = "--force" in sys.argv
```

**修改后:**
```python
def main():
    if len(sys.argv) < 2:
        print("注意：不允许跳过 pre-commit hook 检查")
        print("如需提交，请先完成 workflow 步骤")
    message = sys.argv[1]
```

### 2. 移除 --no-verify

**修改前:**
```python
commit_cmd = f'git commit -m "{message}"'
if force_mode:
    commit_cmd += ' --no-verify'
```

**修改后:**
```python
code, out, err = run_command(f'git commit -m "{message}"')
```

### 3. 移除 git add -A

**修改前:**
```python
add_cmd = "git add -A" if force_mode else "git add -u"
```

**修改后:**
```python
code, out, err = run_command("git add -u")
```

---

## 核心原则

> **"禁止跳过 session 检查"**

- ✅ 所有 git 提交必须通过 pre-commit hook
- ✅ pre-commit hook 检查 session 存在
- ✅ pre-commit hook 检查 workflow compliance
- ✅ 不允许任何方式绕过

---

## 提交

```bash
git add 30-scripts-tools/git_commit_helper.py
git commit -m "Remove-force-mode-prevent-session-bypass"
git push
```

---

**状态:** 已修复，等待提交
