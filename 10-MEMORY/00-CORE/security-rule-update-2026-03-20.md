# 安全规则更新 - 自举例外 (Bootstrap Exception)

**日期:** 2026-03-20 12:41  
**类型:** 元任务 (Meta-Task) - 防护系统自修复  
**授权:** 用户明确要求修改

---

## 问题

**循环依赖:**
- 没有 session → 不能调用工具
- 不能调用工具 → 无法自动运行 copaw_entry.py
- 用户不运行 copaw_entry.py → 永远没有 session

**结果:** 系统无法自举

---

## 解决方案

**添加自举例外条款:**

允许在无 session 时执行 `copaw_entry.py`，用于会话初始化。

**条件:**
1. 仅限 `copaw_entry.py` 这一个脚本
2. 必须是直接调用，不能有参数注入
3. 执行后必须创建 `execution-state.json`

**原则:** 允许合理的自举机制，但不允许借此绕过后续防护

---

## 修改文件

| 文件 | 修改内容 |
|------|---------|
| `13-memory/mandatory-security-rules.md` | 添加第 0 条：自举例外 |
| `30-scripts-tools/tool_wrapper.py` | before_tool_call() 添加 copaw_entry 白名单 |
| `AGENTS.md` | 强制安全规则部分添加自举例外说明 |

---

## 核心原则更新

**原原则:**
> 不直接碰 Shell，不执行未授权代码，不信任任何输入，不做任何变通。

**新原则:**
> 不直接碰 Shell，不执行未授权代码，不信任任何输入，不做任何变通。
> **例外:** 允许 copaw_entry.py 作为自举机制（仅此一个脚本）。

---

## 验证

**测试命令:**
```bash
# 在无 session 时运行
py 30-scripts-tools/test_wrapper_strict.py

# 预期结果：
# - copaw_entry.py → 允许执行
# - 其他工具 → 拒绝执行
```

---

## 风险评估

| 风险 | 等级 | 缓解措施 |
|------|------|---------|
| 被滥用于绕过防护 | 低 | 仅限 copaw_entry.py 一个脚本 |
| 参数注入 | 低 | copaw_entry.py 内部有参数验证 |
| 伪造 session | 低 | execution-state.json 有完整性检查 |

**总体风险:** 低 ✅

---

## 后续

1. ✅ 安全规则已更新
2. ✅ tool_wrapper.py 已更新
3. ⏳ 用户运行 `copaw_entry.py` 初始化会话
4. ⏳ 之后所有操作通过工作流执行

---

**状态:** 完成  
**下一步:** 等待用户运行 copaw_entry.py
