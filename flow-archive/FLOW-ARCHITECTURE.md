# 工作流架构设计

**主工作流:** `20260318-universal-workflow-001`  
**版本:** 1.0  
**日期:** 2026-03-19

---

## 🏗️ 架构原则

### 1. 唯一主工作流原则

```
✅ 20260318-universal-workflow-001 - 主工作流 (总控/指挥)
    │
    ├── session-end.json - 子工作流 (会话结束处理)
    ├── brainstorm-001.json - 子工作流 (头脑风暴)
    ├── research-001.json - 子工作流 (研究任务)
    └── project-001.json - 子工作流 (项目管理)
```

**规则:**
- 主工作流只有一个：`universal-workflow-001`
- 主工作流可以调用任何子工作流
- 子工作流只能被调用，不能调用其他工作流
- 子工作流之间不能互相调用

### 2. 职责分离原则

| 工作流 | 类型 | 职责 | 触发时机 |
|--------|------|------|---------|
| `universal-workflow-001` | 主工作流 | 总控、调度、协调 | 所有任务 |
| `session-end.json` | 子工作流 | 会话结束处理 | 每次对话结束 |
| `brainstorm-001.json` | 子工作流 | 头脑风暴 | 需要创意时 |
| `research-001.json` | 子工作流 | 深度研究 | 需要调研时 |
| `project-001.json` | 子工作流 | 项目管理 | 启动项目时 |

### 3. 调用层级

```
Level 0: universal-workflow-001 (主工作流)
    ↓ 调用
Level 1: session-end, brainstorm, research, project (子工作流)
    ↓ 执行
Level 2: 工具脚本 (brainstorm_define.py, auto-critic.py, etc.)
```

**禁止:**
- ❌ Level 1 调用 Level 0
- ❌ Level 1 调用 Level 1
- ❌ Level 2 调用 Level 0/1

---

## 📋 主工作流职责

### 核心功能

1. **任务调度** - 根据任务类型选择子工作流
2. **资源协调** - 分配工具、时间、优先级
3. **质量把控** - 确保所有子工作流符合标准
4. **状态管理** - 跟踪所有子工作流执行状态
5. **异常处理** - 处理子工作流失败

### 调用逻辑

```python
# 主工作流调度逻辑 (伪代码)
def execute_task(task_type, context):
    if task_type == "session_end":
        call_subworkflow("session-end.json")
    elif task_type == "brainstorm":
        call_subworkflow("brainstorm-001.json")
    elif task_type == "research":
        call_subworkflow("research-001.json")
    elif task_type == "project":
        call_subworkflow("project-001.json")
    else:
        execute_default_workflow()
    
    # 质量检查
    verify_quality()
    
    # 提交结果
    commit_and_push()
```

---

## 📋 子工作流职责

### session-end.json (会话结束)

**职责:** 每次对话结束后的标准处理流程

**步骤:**
1. 会话压缩
2. 上下文验证
3. 当日笔记检查
4. 记忆系统维护 (周末)
5. 批判者审查
6. 质量门检查
7. P1 问题修复
8. Git 提交

**触发:** 每次对话结束  
**阻塞性:** 是 (必须通过)

### brainstorm-001.json (头脑风暴)

**职责:** 创造性思维任务

**步骤:**
1. 问题定义
2. 背景研究 (可选)
3. 自由联想
4. 强制关联 (可选)
5. 初步筛选
6. 深度评估 (可选)
7. 优先级排序
8. 行动规划

**触发:** 用户要求头脑风暴时  
**阻塞性:** 否 (可选任务)

### research-001.json (研究任务)

**职责:** 深度调研和信息收集

**步骤:** (待定义)

**触发:** 需要文献调研时  
**阻塞性:** 否

### project-001.json (项目管理)

**职责:** 项目启动和跟踪

**步骤:** (待定义)

**触发:** 启动新项目时  
**阻塞性:** 否

---

## 🔧 实现方式

### 主工作流调用子工作流

**方式 1: tool_executor 调用**

```bash
# 主工作流通过 tool_executor 调用子工作流
py 30-scripts-tools\tool_executor.py --workflow session-end --context {...}
py 30-scripts-tools\tool_executor.py --workflow brainstorm-001 --context {...}
```

**方式 2: Python 脚本调用**

```python
# 在主工作流脚本中
from tool_executor import ToolExecutor

executor = ToolExecutor(context)
executor.execute_workflow("session-end", context)
```

### 子工作流注册

所有子工作流必须在 `tools_registry.json` 中注册为工具：

```json
{
  "tools": {
    "workflow-session-end": {
      "tool_id": "workflow-session-end",
      "name": "Session End Workflow",
      "command": "py 30-scripts-tools\\tool_executor.py --workflow session-end",
      "type": "subworkflow"
    },
    "workflow-brainstorm": {
      "tool_id": "workflow-brainstorm",
      "name": "Brainstorm Workflow",
      "command": "py 30-scripts-tools\\tool_executor.py --workflow brainstorm-001",
      "type": "subworkflow"
    }
  }
}
```

---

## ⚠️ 常见错误

### ❌ 错误 1: 子工作流调用主工作流

```json
// brainstorm-001.json 中
{
  "step_id": 8,
  "tool_id": "workflow-universal"  // ❌ 禁止！
}
```

**正确做法:** 主工作流调用子工作流，不是反过来

### ❌ 错误 2: 子工作流互相调用

```json
// session-end.json 中
{
  "step_id": 10,
  "tool_id": "workflow-brainstorm"  // ❌ 禁止！
}
```

**正确做法:** 都通过主工作流调度

### ❌ 错误 3: 多个主工作流

```
flow-archive/
├── universal-workflow-001/  ✅ 主工作流
├── brainstorm-001/          ✅ 子工作流
└── another-main-001/        ❌ 禁止！只能有一个主工作流
```

---

## ✅ 验收标准

- [x] 只有一个主工作流 (`universal-workflow-001`)
- [ ] 所有子工作流在 `tools_registry.json` 中注册为工具类型
- [ ] 子工作流不包含调用其他工作流的步骤
- [ ] 主工作流有明确的任务调度逻辑
- [ ] 文档清晰说明主从关系

---

**状态:** 📝 设计中  
**下一步:** 更新子工作流配置，移除越权调用
