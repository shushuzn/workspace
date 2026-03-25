# AGENTS.md - Your Workspace

> [174 lines compressed | extreme mode]

## First Run
## Every Session
1. ✅ **Load only 7 core files** (<100KB)
   - SOUL.md, USER.md, AGENTS.md, TOOLS.md, HEARTBEAT.md
   py 30-scripts-tools/fast_load.py
## 🔴 强制安全规则 (2026-03-20 - 最高优先级)
### ⚠️ 自举例外 (Bootstrap Exception)
### 严禁操作
### 允许工具
- `read_file`, `write_file`, `edit_file`
### 违规后果
## 🛡️ 强制防护规则 (2026-03-20 新增)
### 防护检查点
| **停止检查** | forced_protection_executor.py | .STOP_FLAG 不存在 | ❌ 直接退出 |
### 强制防护执行器
# ❌ 错误：直接执行 (会被防护检查阻止)
# ✅ 正确：通过防护包装器
# ✅ 正确：通过 copaw_entry 启动会话后执行
# 然后工具调用会自动通过防护层
# ❌ 错误：直接使用 execute_shell_command (无法被防护检查)
# ✅ 正确：通过安全执行器
py 30-scripts-tools/safe_shell_executor.py echo "test"
# ✅ 或使用批处理
### 防护规则
   - .STOP_FLAG 存在 → 直接退出
   - 自动设置 .STOP_FLAG
### 防护工具
### 违规后果
## Communication Style