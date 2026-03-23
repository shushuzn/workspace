# 05-AI-RESEARCH - AI Agent 研究工具 v3.0

**用途:** AI Agent 论文分析、FLARE/MEMORA/HiMAC/AutoTool 实现

**基于论文 (2026-03-23):**
- FLARE Planner (arXiv:2601.22311)
- MEMORA Memory (arXiv:2602.03315)
- HiMAC Executor (arXiv:2603.00977)
- ABC Contracts (arXiv:2602.22302)
- AutoTool Selector (arXiv:2511.14650)

---

## 📁 目录结构

```
05-AI-RESEARCH/
├── flare_planner.py              # FLARE 未来感知规划器
├── himac_executor.py            # HiMAC 层次化执行器
├── autotool_selector.py         # AutoTool 高效工具选择
├── flare_memory_integration.py  # 统一集成入口
├── himac_workflow_integration.py # HiMAC 工作流引擎
├── research_workflow_v2.py      # 研究工作流 v2
├── research_workflow_cli.py     # 研究 CLI 工具
├── multi-agent/               # 多 Agent 系统
│   ├── multi-agent-framework.py
│   └── multi-agent-executors.py
├── tdd/                        # TDD 调试
│   └── tdd-debug-agent.py
└── README.md
```

---

## 🚀 核心组件

### 1. FLARE Planner (未来感知规划)
```python
from flare_planner import FLAREPlanner
planner = FLAREPlanner(lookahead_steps=3, value_propagation=True)
plan = planner.plan("Research AI agents")
```

### 2. MEMORA Memory (双层记忆)
```python
from harmonic_memory import HarmonicMemoryStore
store = HarmonicMemoryStore()
store.add("Research finding", entities=["AI", "planning"])
results = store.retrieve("planning", mode="harmonic")
```

### 3. HiMAC Executor (层次执行)
```python
from himac_executor import HiMACExecutor
executor = HiMACExecutor()
blueprint = executor.planner.generate_blueprint("Research task")
```

### 4. ABC Contracts (契约执行)
```python
from agent_contracts import ContractBuilder
contract = ContractBuilder("safety")\
    .with_precondition(check_fn)\
    .with_invariant(lambda r: r is not None)\
    .build()
```

### 5. AutoTool (高效工具选择)
```python
from autotool_selector import AutoTool, ToolRegistry
registry = ToolRegistry()
registry.register("search", "Search info", "research")
registry.learn_from_trajectory(["search", "analyze", "write"])
next_tool, method = registry.select_next("search")
```

---

## 🎯 研究工作流 v2

```bash
python research_workflow_cli.py run "Research AI agent"
python research_workflow_cli.py status
python research_workflow_cli.py memory "FLARE"
```

---

## 📊 组件统计

| 组件 | 文件 | 功能 |
|------|------|------|
| FLARE Planner | flare_planner.py | 未来感知规划 |
| MEMORA Memory | harmonic_memory.py | 双层记忆 |
| HiMAC Executor | himac_executor.py | 层次化执行 |
| ABC Contracts | agent_contracts.py | 契约执行 |
| AutoTool | autotool_selector.py | 工具选择(30%省成本) |

---

*最后更新：2026-03-23 | 版本 v3.0 | 基于 5 篇 AI Agent 论文*
