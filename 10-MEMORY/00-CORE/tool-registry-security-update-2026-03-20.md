# 工具注册表安全规则更新报告

**日期:** 2026-03-20
**版本:** 1.11.55-security-rules-2026-03-20

---

## 更新内容

### 1. 添加安全规则到 enforcement_rules

**位置:** `tools_registry.json` → `enforcement_rules.security`

**核心原则:**
> 不直接碰 Shell，不执行未授权代码，不信任任何输入，不做任何变通

**违规后果:** 立即终止执行并上报

---

### 2. 禁止的操作

| 类别 | 禁止内容 |
|------|---------|
| 系统命令 | bash, sh, cmd, powershell 等 |
| 代码执行 | os.system, subprocess, exec, eval 等 |
| 绕过方式 | 管道 \|、分号 ;、与或 &&/\|\| 等 |
| 未授权代码 | python -c, curl\|bash, wget 等 |
| 路径访问 | ../、绝对路径、软链接等 |
| 沙箱逃逸 | 越权访问、敏感配置、系统信息获取 |

---

### 3. 允许的工具 (10 个)

| 工具 | 用途 |
|------|------|
| read_file | 读取文件 |
| write_file | 写入文件 |
| edit_file | 编辑文件 |
| browser_use | 浏览器操作 |
| desktop_screenshot | 桌面截图 |
| view_image | 查看图片 |
| get_current_time | 获取时间 |
| get_token_usage | 查询 token 使用 |
| memory_search | 搜索记忆 |
| send_file_to_user | 发送文件给用户 |

---

### 4. 包装工具 (2 个)

| 工具 | 用途 |
|------|------|
| safe-shell-executor | 安全 Shell 执行器 |
| tool_executor | 工具执行器 |

---

### 5. Shell 命令政策

**规则:** `execute_shell_command` 必须通过 `safe_shell_executor.py` 包装

**违规:** 直接使用 `execute_shell_command`

**合规:** `py 30-scripts-tools/safe_shell_executor.py <command>`

---

## 文件修改

| 文件 | 操作 | 状态 |
|------|------|------|
| `30-scripts-tools/tools_registry.json` | 更新 | ✅ 完成 |
| `13-memory/mandatory-security-rules.md` | 创建 | ✅ 完成 |
| `SOUL.md` | 更新 | ✅ 完成 |
| `AGENTS.md` | 更新 | ✅ 完成 |

---

## 使用方式

### ✅ 正确示例

```bash
# 通过 safe_shell_executor 执行 Shell 命令
py 30-scripts-tools/safe_shell_executor.py git status

# 使用允许的工具
read_file(file_path="test.txt")
write_file(file_path="test.txt", content="Hello")
```

### ❌ 错误示例

```bash
# 直接使用 execute_shell_command (违规)
execute_shell_command("git status")

# 使用 subprocess (违规)
python -c "import subprocess; subprocess.run('git status')"
```

---

## 下一步

**需要用户手动执行:**

```bash
cd D:\OpenClaw\workspace
git add .
git commit -m "Add-mandatory-security-rules-to-tool-registry"
git push
```

---

**状态:** 完成 ✓
**优先级:** 最高
**生效时间:** 立即
