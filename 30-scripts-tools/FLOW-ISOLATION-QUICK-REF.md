# 🚀 通用工作流 - 快速参考卡

**Last Updated:** 2026-03-18  
**Status:** ✅ Ready to Use  
**默认 Flow ID:** `20260318-universal-workflow-001`

---

## 📋 快速启动 (3 步)

### Step 1: 启动工作流 (可选)
```bash
# 方式 A: 使用快速启动脚本 (不指定 = 通用工作流)
30-scripts-tools\start-flow.bat

# 方式 B: 指定业务类型
30-scripts-tools\start-flow.bat backend-crud
```

### Step 2: 执行任务
```markdown
隔离铁则:
- 所有文件读写 → flow-archive/{flow_id}/
- 所有日志 → flow-archive/{flow_id}/execution-log.json
- 禁止修改/引用其他工作流内容
```

### Step 3: 完成归档 (自动使用通用 Flow ID)
```bash
# 不指定 Flow ID = 默认使用 20260318-universal-workflow-001
py 30-scripts-tools\session_end.py "完成描述"

# 或指定特定 Flow ID
py 30-scripts-tools\session_end.py "完成描述" --flow_id 20260318-backend-crud-001
```

---

## 🎯 常用命令速查

### 启动工作流
```bash
# 快速启动 (不指定 = 通用工作流)
30-scripts-tools\start-flow.bat
# → Flow ID: 20260318-universal-workflow-001

# 指定业务类型
30-scripts-tools\start-flow.bat backend-crud
# → Flow ID: 20260318-backend-crud-001

# 手动启动 (不指定 --flow_id = 默认通用工作流)
py session_end.py "Task"
# → Flow ID: 20260318-universal-workflow-001

# 手动指定 Flow ID
py session_end.py "Task" --flow_id 20260318-backend-crud-001
```

### 批判者审查
```bash
# 最终审查
py auto-critic_v7.py -t "Task-Name" -p final --flow_id 20260318-xxx-001

# 中期审查
py auto-critic_v7.py -t "Task-Name" -p mid --flow_id 20260318-xxx-001
```

### 查看状态
```bash
# 查看所有 Flow
dir flow-archive /b

# 查看注册表
cat flow-archive/flow_registry.json

# 查看特定 Flow 审查结果
cat flow-archive/20260318-xxx-001/review.json
```

### 并行工作流
```bash
# 终端 1
start-flow.bat backend-api

# 终端 2
start-flow.bat frontend-ui

# 终端 3
start-flow.bat db-migration
```

---

## ⚠️ 3 条避坑红线

### 🔴 红线 1: 切换必须先快照
```bash
# 暂停当前 Flow
py memory_benchmark.py --tag snapshot --flow_id 20260318-universal-workflow-001

# ... 处理其他 Flow ...

# 恢复
py memory_benchmark.py --tag restore --flow_id 20260318-universal-workflow-001
```

### 🔴 红线 2: 并行必须独立子会话
```bash
# ❌ 错误：同一上下文跑多个 Flow
# ✅ 正确：开多个终端窗口

# 终端 1: 通用工作流 (默认)
start-flow.bat

# 终端 2: 后端任务
start-flow.bat backend-crud
```

### 🔴 红线 3: 完成后立即归档
```bash
# 自动归档 (使用默认通用 Flow ID)
py session_end.py "归档"

# 只同步核心结论到主会话
```

---

## 📁 文件隔离结构

```
flow-archive/
├── flow_registry.json                    # Flow 注册表
├── 20260318-backend-crud-001/           # Flow 1
│   ├── review.json                       # 批判者审查
│   ├── execution-log.json                # 执行日志
│   └── snapshot.json                     # 状态快照
└── 20260318-frontend-ui-002/            # Flow 2
    ├── review.json
    ├── execution-log.json
    └── snapshot.json
```

---

## 🔍 批判者检查清单

### 启动前
- [ ] Flow ID 格式正确 (`{日期}-{业务}-{序号}`)
- [ ] flow-archive 目录存在
- [ ] flow_registry.json 可写

### 执行中
- [ ] 无跨 Flow ID 文件访问
- [ ] 无全局状态污染
- [ ] 日志正确隔离

### 完成后
- [ ] review.json 已生成
- [ ] execution-log.json 已生成
- [ ] flow_registry.json 状态更新为 "archived"
- [ ] Git 提交包含 `[FLOW ID: xxx]`

---

## 📊 性能指标

| 指标 | 改造前 | 改造后 | 提升 |
|------|--------|--------|------|
| 并行工作流数 | 1 | ∞ | ∞ |
| 上下文污染 | 高 | 零 | -100% |
| 文件冲突风险 | 高 | 零 | -100% |
| 状态丢失风险 | 中 | 零 | -100% |

---

## 📚 相关文档

- **完整方案:** `30-scripts-tools/MULTI-WORKFLOW-FLOW-ISOLATION.md`
- **批判者 v7:** `15-docs/AUTO-CRITIC.md`
- **工具执行器:** `30-scripts-tools/tool_executor.py`
- **会话结束:** `30-scripts-tools/session_end.py`

---

**Quick Start:**
```bash
# 1. 启动 (可选)
30-scripts-tools\start-flow.bat
# → 默认 Flow ID: 20260318-universal-workflow-001

# 2. 执行任务
# ... 你的工作 ...

# 3. 归档 (自动使用默认 Flow ID)
py session_end.py "Done"
# → Flow ID: 20260318-universal-workflow-001
```

---

**Status:** ✅ Ready to Use  
**Version:** 1.0  
**Last Updated:** 20260318
