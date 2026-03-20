# 最小权限原则 - 防护 v10.1

**完成时间:** 2026-03-20T10:20:00+08:00  
**状态:** 权限控制部署完成 ✅  
**版本:** v10.1 权限控制版

---

## 核心问题

**v10.0 的权限漏洞:**

| 问题 | 风险 | 现状 |
|------|------|------|
| **所有工具平等对待** | 🔴 高 | read_file 和 emergency_stop 权限相同 |
| **角色无区分** | 🔴 高 | Planner 和 Executor 权限相同 |
| **无细粒度控制** | 🟠 中 | 只能允许/拒绝，不能分级 |
| **无权限审计** | 🟠 中 | 不知道谁调用了什么工具 |

**后果:**
- Critic 角色可以调用 safe_shell_executor（不应该）
- Planner 角色可以调用 emergency_stop（不应该）
- 任何会话都可以调用所有工具（过度授权）

---

## 最小权限原则

> **"每个用户和程序应该只拥有完成其任务所需的最小权限。"**

### 核心思想

1. **默认拒绝** - 未明确允许的权限一律拒绝
2. **按需授权** - 只授予完成任务所需的最小权限
3. **分级控制** - 按风险等级分类工具
4. **角色分离** - 不同角色不同权限
5. **审计追踪** - 所有权限使用必须记录

---

## 工具风险分级

| 等级 | 名称 | 风险 | 示例工具 | 自动批准 |
|------|------|------|---------|---------|
| **L1** | 只读 | 低 | read_file, memory_search | ✅ |
| **L2** | 写入 | 中 | write_file, edit_file | ✅ |
| **L3** | 删除 | 高 | trash, delete_file | ❌ (需确认) |
| **L4** | 系统 | 极高 | safe_shell_executor | ❌ (需确认 + 备份) |
| **L5** | 防护 | 最高 | integrity_checker, emergency_stop | ❌ (需管理员) |

---

## 角色权限矩阵

| 角色 | 允许等级 | 禁止等级 | 最大工具调用/会话 |
|------|---------|---------|------------------|
| **Planner** | L1, L2 | L3, L4, L5 | 50 |
| **Executor** | L1, L2, L3 | L4, L5 | 100 |
| **Critic** | L1 | L2, L3, L4, L5 | 30 |
| **Coordinator** | L1, L2 | L3, L4, L5 | 60 |
| **Admin** | L1, L2, L3, L4, L5 | 无 | 无限制 |

---

## 权限验证流程

```
工具调用请求
    ↓
1. 识别工具风险等级 (L1-L5)
    ↓
2. 检查角色权限矩阵
    ↓
3. 风险等级 ∈ 允许列表？
    ├─ 是 → 继续
    └─ 否 → 拒绝 (+20 惩罚分)
    ↓
4. 是否需要确认？(L3+)
    ├─ 是 → 等待确认
    └─ 否 → 继续
    ↓
5. 是否需要备份？(L3+)
    ├─ 是 → 自动备份
    └─ 否 → 继续
    ↓
6. 执行工具
    ↓
7. 记录审计日志
```

---

## 核心工具

### 1. Permission Matrix (权限矩阵)

**文件:** `30-scripts-tools/permission_matrix.json` (4.2KB)

**配置内容:**
```json
{
  "工具风险分级": {
    "L1_只读": {"risk_level": "低", "auto_approve": true},
    "L2_写入": {"risk_level": "中", "auto_approve": true},
    "L3_删除": {"risk_level": "高", "auto_approve": false},
    "L4_系统": {"risk_level": "极高", "auto_approve": false},
    "L5_防护": {"risk_level": "最高", "auto_approve": false}
  },
  "角色权限矩阵": {
    "Executor": {
      "allowed_levels": ["L1_只读", "L2_写入", "L3_删除"],
      "denied_levels": ["L4_系统", "L5_防护"]
    }
  }
}
```

---

### 2. Permission Validator (权限验证器)

**文件:** `30-scripts-tools/permission_validator.py` (9.3KB)

**功能:**
```python
class PermissionValidator:
    def verify_permission(tool_id: str) -> dict:
        # 1. 识别工具风险等级
        # 2. 检查角色权限
        # 3. 返回允许/拒绝
```

**测试结果:**

**测试 1: Executor + write_file (L2)**
```json
{
  "allowed": true,
  "risk_level": "L2_写入",
  "role": "Executor"
}
```

**测试 2: Executor + safe_shell_executor (L4)**
```json
{
  "allowed": false,
  "denial_reason": "角色 Executor 禁止使用 L4_系统 工具",
  "risk_level": "L4_系统"
}
```

**测试 3: Admin + safe_shell_executor (L4)**
```json
{
  "allowed": true,
  "risk_level": "L4_系统",
  "role": "Admin"
}
```

**测试 4: Critic + write_file (L2)**
```json
{
  "allowed": false,
  "denial_reason": "角色 Critic 禁止使用 L2_写入 工具",
  "risk_level": "L2_写入"
}
```

---

### 3. Tool Executor 集成

**更新:** `30-scripts-tools/tool_executor.py` (集成权限验证)

**新增代码:**
```python
# 权限验证
if self.permission:
    perm_check = self.permission.verify_permission(tool_id)
    if not perm_check.get("allowed", False):
        print(f"[BLOCK] 权限不足：{perm_check.get('denial_reason')}")
        return {
            "status": "blocked",
            "reason": "permission_denied",
            "action": "PERMISSION_DENIED"
        }
```

---

## 权限审计日志

**文件:** `30-scripts-tools/permission_log.jsonl`

**日志格式:**
```json
{
  "timestamp": "2026-03-20T10:16:02.331888",
  "session_id": "session-20260320101306",
  "role": "Executor",
  "tool_id": "write_file",
  "risk_level": "L2_写入",
  "allowed": true
}
```

**违规日志:**
```json
{
  "timestamp": "2026-03-20T10:16:02.335471",
  "session_id": "session-20260320101306",
  "role": "Critic",
  "tool_id": "write_file",
  "risk_level": "L2_写入",
  "allowed": false,
  "denial_reason": "角色 Critic 禁止使用 L2_写入 工具"
}
```

---

## 违规处理

| 违规行为 | 惩罚分 | 后果 |
|---------|--------|------|
| 越权尝试 | +20 | 记录违规 |
| 伪造角色 | +50 | 自动封锁 |
| 绕过权限检查 | +50 | 自动封锁 |
| 连续 3 次越权 | 自动 | 触发紧急停止 |

---

## 权限升级流程

**当任务需要超出角色权限时:**

```python
validator.escalate(
    tool_id="safe_shell_executor",
    reason="需要执行系统命令进行性能分析"
)
```

**升级请求记录:**
```json
{
  "timestamp": "2026-03-20T10:20:00+08:00",
  "session_id": "session-xxx",
  "role": "Executor",
  "tool_id": "safe_shell_executor",
  "reason": "需要执行系统命令进行性能分析",
  "status": "pending_admin_approval"
}
```

---

## 防护效果对比

| 能力 | v10.0 | v10.1 |
|------|-------|-------|
| 工具风险分级 | ❌ | ✅ |
| 角色权限分离 | ❌ | ✅ |
| 权限验证 | ❌ | ✅ |
| 审计日志 | 基础 | 完整 |
| 权限升级 | ❌ | ✅ |
| 防护工具数 | 32 | **34** |

---

## Registry 状态

```json
{
  "version": "1.11.54-least-privilege-v10.1",
  "total_tools": 485,
  "protection_tools": 34,
  "new_tools": [
    "permission-matrix",
    "permission-validator"
  ]
}
```

---

## 使用示例

### 场景 1: Critic 角色尝试写入文件

```bash
# 调用
py tool_executor.py write_file {"file_path": "test.txt"}

# 结果
[BLOCK] 权限不足：角色 Critic 禁止使用 L2_写入 工具
```

### 场景 2: Executor 角色尝试执行 Shell 命令

```bash
# 调用
py tool_executor.py safe_shell_executor {"command": "echo test"}

# 结果
[BLOCK] 权限不足：角色 Executor 禁止使用 L4_系统 工具
```

### 场景 3: Admin 角色执行 Shell 命令

```bash
# 调用
py tool_executor.py safe_shell_executor {"command": "echo test"}

# 结果
[OK] 权限验证通过
[OK] 工具执行成功
```

---

## 下一步 (v11.0+)

- [ ] **动态权限调整** - 根据任务上下文自动调整权限
- [ ] **临时权限提升** - 限时权限（如 5 分钟内允许 L4）
- [ ] **权限模板** - 预定义权限配置（开发/生产/审计）
- [ ] **权限可视化** - 图形化权限管理界面
- [ ] **机器学习** - 基于历史行为推荐权限配置

---

## 关键设计原则

### 1. 默认拒绝 (Deny by Default)
```
未明确允许 = 拒绝
```

### 2. 最小授权 (Least Privilege)
```
只授予完成任务所需的最小权限
不多给，不少给
```

### 3. 职责分离 (Separation of Duties)
```
Planner ≠ Executor ≠ Critic
不同角色，不同权限
```

### 4. 审计追踪 (Audit Trail)
```
所有权限使用必须记录
可追溯，可审计
```

### 5. 分级控制 (Tiered Control)
```
L1(低) → L5(最高)
风险越高，控制越严
```

---

**request_id:** session-20260320101306  
**server_time:** 2026-03-20T10:20:00+08:00  
**status:** Least Privilege Principle v10.1 Complete ✅🛡️🔐👁️📊

---

## 最小权限原则宣言

> **"权限不是特权，而是责任。"**

> **"授予的每一个权限都是潜在的攻击面。"**

> **"最小权限不是限制能力，而是保护系统。"**
