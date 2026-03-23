# 05-AI-RESEARCH - AI Agent 研究工具 v2.0

**用途:** AI Agent 论文分析、FLARE/MEMORA/HiMAC 实现、自主研究系统

**基于论文 (2026-03-23):**
- FLARE Planner (arXiv:2601.22311)
- MEMORA Memory (arXiv:2602.03315)
- HiMAC Executor (arXiv:2603.00977)
- ABC Contracts (arXiv:2602.22302)

---

## 📁 目录结构

```
05-AI-RESEARCH/
├── flare_planner.py              # FLARE 未来感知规划器
├── himac_executor.py            # HiMAC 层次化执行器
├── flare_memory_integration.py  # 统一集成入口
├── himac_workflow_integration.py # HiMAC 工作流引擎
├── research_workflow_v2.py      # 研究工作流 (FLARE + MEMORA + HiMAC)
├── research_workflow_cli.py     # 研究 CLI 工具
├── multi-agent/                 # 多 Agent 系统
│   ├── multi-agent-framework.py
│   └── multi-agent-executors.py
├── tdd/                        # TDD 调试
│   └── tdd-debug-agent.py
└── README.md
```

---

## 🚀 核心组件

### 1. FLARE Planner (未来感知规划)
**文件:** `flare_planner.py`

```python
from flare_planner import FLAREPlanner

planner = FLAREPlanner(
    lookahead_steps=3,
    value_propagation=True,
    commitment_threshold=0.7
)
plan = planner.plan("Research AI agents and write report")
```

**核心特性:**
- Future-aware lookahead: 考虑行动对未来步骤的影响
- Value propagation: 下游结果反向影响早期决策
- Limited commitment: 避免过早锁定行动

### 2. MEMORA Memory (双层记忆)
**文件:** `harmonic_memory.py`

```python
from harmonic_memory import HarmonicMemoryStore

store = HarmonicMemoryStore()
store.add("Important research finding", entities=["AI", "planning"])
results = store.retrieve("planning", mode="harmonic")
```

**核心特性:**
- Primary Abstractions: 抽象层索引
- Cue Anchors: 检索锚点扩展
- 节省 98% token

### 3. HiMAC Executor (层次执行)
**文件:** `himac_executor.py`

```python
from himac_executor import HiMACExecutor, MacroPlanner

executor = HiMACExecutor(planner=MacroPlanner())
blueprint = executor.planner.generate_blueprint("Research task")
```

**核心特性:**
- Macro-Level: 结构化蓝图生成
- Micro-Level: 目标条件执行
- Critic-free 优化

### 4. ABC Contracts (契约执行)
**文件:** `agent_contracts.py`

```python
from agent_contracts import ContractBuilder, ViolationType

contract = ContractBuilder("safety")\
    .with_precondition(check_fn, "Precondition failed")\
    .with_invariant(lambda r: r is not None, "Result is None")\
    .build()
```

**核心特性:**
- P/I/G/R 契约: Preconditions, Invariants, Governance, Recovery
- 漂移边界定理: γ > α → D* = α/γ
- 运行时强制执行

---

## 🎯 研究工作流 v2.0

**文件:** `research_workflow_v2.py` + `research_workflow_cli.py`

```bash
# 运行研究任务
python research_workflow_cli.py run "Research AI agent planning methods"

# 查看状态
python research_workflow_cli.py status

# 搜索记忆
python research_workflow_cli.py memory "FLARE planner"

# 添加研究发现
python research_workflow_cli.py add "FLARE solves myopic commitment"

# 运行演示
python research_workflow_cli.py demo
```

---

## 📊 统计信息

| 组件 | 文件 | 功能 |
|------|------|------|
| FLARE Planner | flare_planner.py | 未来感知规划 |
| MEMORA Memory | harmonic_memory.py | 双层记忆存储 |
| HiMAC Executor | himac_executor.py | 层次化执行 |
| ABC Contracts | agent_contracts.py | 契约执行 |
| 集成模块 | flare_memory_integration.py | 统一入口 |
| 研究工作流 | research_workflow_v2.py | 完整流程 |

---

## 🔗 集成关系

```
research_workflow_cli.py
         ↓
research_workflow_v2.py
         ↓
    ┌────┴────┐
    ↓         ↓
FLARE      MEMORA
Planner    Memory
    ↓
HiMAC
Executor
    ↓
ABC
Contracts
```

---

*最后更新：2026-03-23 | 版本 v2.0 | 基于 4 篇 AI Agent 论文*
