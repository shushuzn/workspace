# 工作流架构设计

**主工作流:** `20260318-universal-workflow-001`  
**版本:** 1.0.0  
**日期:** 2026-03-19  
**配置状态:** ✅ 显式配置已完成

---

## 🏗️ 架构原则

### 1. 唯一主工作流原则

```
✅ 20260318-universal-workflow-001 - 主工作流 (总控/指挥)
    │
    ├── 20260318-brainstorm-001 - 子工作流 (头脑风暴)
    ├── 20260318-session-end - 子工作流 (会话结束处理)
    ├── 20260318-research-001 - 子工作流 (研究任务)
    └── 20260318-project-001 - 子工作流 (项目管理)
```

**规则:**
- 主工作流只有一个：`universal-workflow-001`
- 主工作流可以调用任何子工作流
- 子工作流只能被调用，不能调用其他工作流
- 子工作流之间不能互相调用

### 2. 职责分离原则

| 工作流 | 类型 | 职责 | 触发时机 | 步骤数 |
|--------|------|------|----------|--------|
| `universal-workflow-001` | 主工作流 | 总控、调度、协调 | 所有任务 | 12 |
| `session-end` | 子工作流 | 会话结束处理 | 每次对话结束 | 16 |
| `brainstorm-001` | 子工作流 | 头脑风暴 | 需要创意时 | 8 |
| `research-001` | 子工作流 | 深度研究 | 需要调研时 | TBD |
| `project-001` | 子工作流 | 项目管理 | 启动项目时 | TBD |

### 3. 调用层级

```
Level 0: 20260318-universal-workflow-001 (主工作流)
    ↓ 调用
Level 1: 子工作流 (brainstorm, session-end, research, project)
    ↓ 执行
Level 2: 工具脚本 (auto-critic-v7.py, session-compress.py, etc.)
```

**禁止:**
- ❌ Level 1 调用 Level 0
- ❌ Level 1 调用 Level 1
- ❌ Level 2 调用 Level 0/1

---

## 📋 主工作流详细配置

### 核心信息

| 属性 | 值 |
|------|-----|
| **Flow ID** | `20260318-universal-workflow-001` |
| **名称** | 通用主工作流 |
| **版本** | 1.0.0 |
| **类型** | main (主工作流) |
| **总步骤数** | 12 |
| **配置文件** | `flow-archive/20260318-universal-workflow-001/workflow.json` |
| **版本目录** | `flow-archive/20260318-universal-workflow-001/versions/` |

### 12 个核心步骤

| 阶段 | Step | 名称 | 工具 | 阻塞性 | 超时 |
|------|------|------|------|--------|------|
| **Initialization** | 1 | 上下文加载验证 | context-verify | ✅ | 30s |
| | 2 | Flow ID 绑定 | flow-manager | ✅ | 60s |
| **Task Analysis** | 3 | 任务解析 | task-analyzer | ✅ | 120s |
| | 4 | 工具/工作流选择 | tool-suggester | ✅ | 60s |
| **Execution** | 5 | 子工作流调度 | workflow-scheduler | ✅ | 1800s |
| | 6 | 工具执行 | tool-executor | ✅ | 600s |
| | 7 | 执行日志记录 | execution-logger | ❌ | 30s |
| | 8 | 检查点保存 | checkpoint-saver | ❌ | 30s |
| **Validation** | 9 | 批判者最终审查 | auto-critic-v7 | ✅ | 300s |
| | 10 | 质量门禁 | quality-gate | ✅ | 120s |
| **Completion** | 11 | 会话压缩保存 | session-compress | ✅ | 60s |
| | 12 | Git 提交推送 | git-commit-push | ✅ | 120s |

### 阶段说明

```
Stage 1: Initialization (Step 1-2)
  - 验证 7 个核心文件已正确加载 (<100KB)
  - 创建或绑定当前任务的 Flow ID
  - 确保隔离工作目录已创建

Stage 2: Task Analysis (Step 3-4)
  - 分析用户请求，确定任务类型和复杂度
  - 根据任务类型选择合适的工具或子工作流
  - 简单任务 (<10 分钟) → 直接调用工具
  - 复杂任务 (>30 分钟) → 调用子工作流

Stage 3: Execution (Step 5-8)
  - 调用子工作流或工具执行任务
  - 记录执行日志到 execution-log.json
  - 保存检查点支持断点续传

Stage 4: Validation (Step 9-10)
  - Auto-Critic v7.0 最终审查 (≥95 分通过)
  - 质量门禁检查 (代码质量≥80, 安全漏洞 0)

Stage 5: Completion (Step 11-12)
  - 压缩会话内容并保存到 daily note
  - 提交所有变更并推送到远程仓库
```

---

## 📋 子工作流注册

### 已注册子工作流

| Flow ID | 名称 | 触发关键词 | 预计用时 | 步骤数 | 状态 |
|---------|------|------------|----------|--------|------|
| `20260318-brainstorm-001` | 头脑风暴工作流 | 头脑风暴/brainstorm/创意/想法 | 45 分钟 | 8 | ✅ 活跃 |
| `20260318-session-end` | 会话结束工作流 | 会话结束/session-end/完成/提交 | 5 分钟 | 16 | ✅ 活跃 |
| `20260318-research-001` | 研究任务工作流 | 研究/research/论文/文献 | 60 分钟 | 10 | ✅ 活跃 |
| `20260318-project-001` | 项目管理工作流 | 项目/project/任务管理 | 30 分钟 | 8 | ✅ 活跃 |

### 子工作流选择规则

```json
{
  "priority": "keyword_match_first",
  "fallback": "manual_selection",
  "max_parallel": 1
}
```

**逻辑:**
1. 优先匹配触发关键词
2. 无匹配时由用户手动选择
3. 同时只允许 1 个子工作流执行

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

## 🛡️ 错误处理

### 重试策略

```json
{
  "max_retries": 3,
  "retry_delay_seconds": 5,
  "exponential_backoff": true
}
```

### 失败处理

| 步骤范围 | 失败动作 |
|----------|----------|
| Step 1-4 (初始化) | 中止并报告错误 |
| Step 5-8 (执行) | 从检查点恢复 |
| Step 9-10 (验证) | 需要人工审查 |
| Step 11-12 (完成) | 继续但不提交 |

### 断点续传

```bash
# 从检查点恢复执行
py flow_manager.py --resume 20260318-universal-workflow-001
```

**检查点文件:** `flow-archive/20260318-universal-workflow-001/checkpoint.json`

---

## 📦 版本控制

### 工具库版本控制

| 配置 | 位置 | 状态 |
|------|------|------|
| **工具库** | `30-scripts-tools/tools_registry.json` | ✅ 已实施 |
| **版本目录** | `flow-archive/tools_registry_versions/` | ✅ 已创建 |
| **当前版本** | v1.4.0 | ✅ 活跃 |

**命令:**
```bash
# 查看可用版本
py flow_manager.py --list-versions

# 回滚到指定版本
py flow_manager.py --rollback-registry --to 1.4.0
```

### 主工作流版本控制

| 配置 | 位置 | 状态 |
|------|------|------|
| **主工作流** | `flow-archive/20260318-universal-workflow-001/workflow.json` | ✅ 已实施 |
| **版本目录** | `flow-archive/20260318-universal-workflow-001/versions/` | ✅ 已创建 |
| **当前版本** | v1.0.0 | ✅ 活跃 |

**版本历史:**
- v1.0.0 (2026-03-19) - 初始版本，定义 12 个核心步骤

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
- [x] 主工作流有显式配置文件 (`workflow.json`)
- [x] 主工作流版本控制已实施
- [x] 12 个核心步骤已定义
- [x] 4 个子工作流已注册 (brainstorm/session-end/research/project)
- [x] 所有子工作流在 `tools_registry.json` 中注册为工具类型
- [x] 子工作流不包含调用其他工作流的步骤
- [x] 错误处理策略已定义
- [x] 断点续传机制已实现
- [x] 文档清晰说明主从关系

---

## 📁 文件结构

```
flow-archive/
├── 20260318-universal-workflow-001/       ✅ 主工作流
│   ├── workflow.json                      ✅ 主工作流配置 (v1.0.0)
│   ├── execution-log.json                 ✅ 执行日志
│   ├── review.json                        ✅ 批判者审查结果
│   └── versions/
│       ├── VERSION_INDEX.json             ✅ 版本索引
│       └── v1.0.0-20260319.json           ✅ v1.0.0 备份
│
├── 20260318-brainstorm-001/               ✅ 子工作流
│   ├── workflow.json                      ✅ 子工作流配置 (v1.0.0)
│   └── versions/
│       └── v1.0.0-20260318.json           ✅ 备份
│
├── 20260318-session-end/                  ✅ 子工作流
│   ├── workflow.json                      ✅ 子工作流配置
│   └── execution-log.json                 ✅ 执行日志
│
├── 20260318-research-001/                 ✅ 子工作流 (新增)
│   ├── workflow.json                      ✅ 子工作流配置 (v1.0.0)
│   └── versions/
│       ├── VERSION_INDEX.json             ✅ 版本索引
│       └── v1.0.0-20260319.json           ✅ 备份
│
├── 20260318-project-001/                  ✅ 子工作流 (新增)
│   ├── workflow.json                      ✅ 子工作流配置 (v1.0.0)
│   └── versions/
│       ├── VERSION_INDEX.json             ✅ 版本索引
│       └── v1.0.0-20260319.json           ✅ 备份
│
├── tools_registry_versions/               ✅ 工具库版本目录
│   ├── VERSION_INDEX.json
│   └── v1.4.0-20260319.json
│
├── flow_registry.json                     ✅ Flow ID 注册表 (v1.0.0)
└── FLOW-ARCHITECTURE.md                   ✅ 架构文档
```

---

**状态:** ✅ 已完成  
**所有子工作流:** 4/4 已完成 (brainstorm/session-end/research/project)  
**工具库版本:** v1.5.0 (新增 workflow-research, workflow-project)  
**下一步:** 无 - 工作流架构完整
