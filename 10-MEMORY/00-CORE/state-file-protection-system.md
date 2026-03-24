# State 文件防护系统 - 防止脚本跳过步骤

**日期:** 2026-03-20
**会话:** session-20260320111128

---

## 问题

用户指出："仍然能通过写脚本跳过步骤"

**根本漏洞:**
- 直接修改 `execution-state.json` 可以跳过所有步骤
- 写脚本设置 `completion_percentage=100` 可以绕过 workflow
- 没有文件完整性验证

---

## 解决方案

### 1. State 保护器 (`state_protector.py`)

**功能:**
- 唯一允许修改 state 的入口
- 所有修改必须记录审计日志
- 所有修改必须包含数字签名
- 检测并报告未经授权的修改

**核心机制:**
```python
# 只有 copaw_entry.py 可以写入
ALLOWED_WRITERS = ['copaw_entry.py', 'state_protector.py']

# 数字签名验证
def compute_signature(state: dict) -> str:
    content = json.dumps(state, sort_keys=True)
    return hashlib.sha256((content + SECRET_KEY).encode()).hexdigest()
```

### 2. State 监控器 (`state_monitor.py`)

**功能:**
- 监控 state 文件的文件哈希
- 检测未经授权的修改
- 自动创建备份
- 可从备份恢复

**核心机制:**
```python
# 文件哈希监控
def compute_file_hash(filepath: Path) -> str:
    with open(filepath, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

# 检测篡改
if current_hash != known_hash:
    log_tampering()
    create_backup()
    return False
```

### 3. Pre-commit Hook v4.0 增强

**新增检查:**
- Check 2.5: 验证 state 文件数字签名
- Check 2.6: 验证 state 文件哈希

```bash
# Check 2.5
py 30-scripts-tools/state_protector.py --verify

# Check 2.6
py 30-scripts-tools/state_monitor.py --check
```

### 4. CoPaw Entry 集成

**更新:**
- 初始化 state 时添加数字签名
- 启用 State 保护器
- 记录保护状态

---

## 防护测试

### 测试 1: 直接修改 state 文件

```
尝试直接修改 execution-state.json...
  已修改 completion_percentage 为 100%
  [BLOCK] 签名验证失败 - 防护生效
[PASS] 防护生效
```

### 测试 2: 写脚本跳过步骤

```
尝试写脚本直接更新 state...
  脚本输出：State modified
  [BLOCK] 签名验证失败 - 防护生效
[PASS] 防护生效
```

### 测试 3: git commit --no-verify

```
尝试 git commit --no-verify...
  [BLOCK] 检测到 --no-verify - 防护生效
[PASS] 防护生效
```

**测试结果：3/3 通过**

---

## 防护层级

| 层级 | 防护 | 绕过难度 |
|------|------|---------|
| **数字签名** | state_protector.py | 🔴 需要破解 SHA256 |
| **文件哈希** | state_monitor.py | 🔴 需要同时修改哈希文件 |
| **审计日志** | state-audit.jsonl | 🟡 会留下痕迹 |
| **Git Hook** | pre-commit v4.0 | 🔴 需要修改 hook |
| **调用者检查** | check_caller() | 🟡 需要修改源码 |

---

## 使用方式

### 正常流程
```bash
# 启动会话（自动启用保护）
py 30-scripts-tools/copaw_entry.py "任务"

# 提交（自动验证）
py 30-scripts-tools/git_commit_helper.py "message"
```

### 验证完整性
```bash
# 验证签名
py 30-scripts-tools/state_protector.py --verify

# 验证哈希
py 30-scripts-tools/state_monitor.py --check
```

### 测试防护
```bash
py 30-scripts-tools/test_bypass_protection.py
```

---

## 提交文件

| 文件 | 说明 |
|------|------|
| `30-scripts-tools/state_protector.py` | State 保护器 |
| `30-scripts-tools/state_monitor.py` | State 监控器 |
| `30-scripts-tools/test_bypass_protection.py` | 绕过测试 |
| `.git/hooks/pre-commit` | v4.0 - 添加签名和哈希检查 |
| `30-scripts-tools/copaw_entry.py` | 集成 State 保护器 |

---

## 核心原则

> **"无签名，不信任"**

- ✅ 所有 state 修改必须有数字签名
- ✅ 所有 state 文件必须有有效哈希
- ✅ 任何修改都会被审计记录
- ✅ 未经授权的修改会被检测
- ✅ 可自动从备份恢复

---

**状态:** 完成，等待提交
