# Agentic BPM

**AI-Driven Business Process Management** — 智能业务流程管理系统

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-0.1.0-orange)

---

## ✨ 特性

| 特性 | 描述 |
|-----|------|
| 🤖 **AI 决策** | 自动决定下一步做什么 |
| 🔗 **任务依赖** | 智能管理任务执行顺序 |
| 📊 **状态跟踪** | 实时监控工作流进度 |
| 🔄 **可扩展** | 轻松集成现有系统 |

---

## 📦 安装

```bash
cd 80-PROJECTS/agentic-bpm
pip install -r requirements.txt
```

---

## 🎮 快速开始

### CLI 用法

```bash
# 创建工作流
python -m agentic_bpm.cli create "My Project"

# 添加任务
python -m agentic_bpm.cli task "Step 1" -d "First task" -p 10

# 添加依赖任务
python -m agentic_bpm.cli task "Step 2" -D t1

# 执行下一个任务
python -m agentic_bpm.cli next

# 完成任务
python -m agentic_bpm.cli complete t1 -r "Success"

# 查看状态
python -m agentic_bpm.cli status

# 列出所有工作流
python -m agentic_bpm.cli list
```

### Python 模块

```python
from agentic_bpm import AgenticOrchestrator, Task

# 创建编排器
orch = AgenticOrchestrator()

# 创建工作流
wf = orch.create_workflow("My Project", "Description")

# 添加任务
orch.add_task(Task(
    id="t1",
    name="Step 1",
    description="First task",
    priority=10
))

orch.add_task(Task(
    id="t2", 
    name="Step 2",
    description="Second task",
    priority=5,
    depends_on=["t1"]  # 依赖 t1
))

# AI 决策下一步
result = orch.execute_next()
print(f"Executing: {result}")

# 完成任务
orch.complete_task("t1", result="Success")

# 查看状态
status = orch.get_status()
print(f"Progress: {status['progress']:.1f}%")
```

---

## 📁 项目结构

```
agentic-bpm/
├── README.md              # 本文件
├── requirements.txt       # 依赖
├── pyproject.toml         # 项目配置
└── agentic_bpm/
    ├── __init__.py        # 包入口
    ├── orchestrator.py    # 核心引擎
    └── cli.py             # 命令行工具
```

---

## 🎯 与现有系统集成

与 workflow 系统集成：

```python
from agentic_bpm import AgenticOrchestrator

orch = AgenticOrchestrator()
orch.integrate_with_workflow_enforcer()
```

---

## 📝 License

MIT License

---

**Made with ❤️ by OpenClaw**