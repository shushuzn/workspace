---
name: ai-research
description: |
  AI Research Tool integrating FLARE planning, MEMORA memory, and AutoTool selection.
  Use when: researching papers, planning complex tasks, managing research memory,
  predicting next tool in a workflow.
metadata:
  version: "1.0.0"
  category: research
---

# AI Research Skill

AI 研究工具 - 基于 FLARE/MEMORA/AutoTool 论文实现。

## Capabilities

- **FLARE Planner**: Future-aware task planning (解决 myopic commitment 问题)
- **MEMORA Memory**: 双层记忆，98% token 节省
- **AutoTool**: 基于图的工具选择，30% 成本降低

## Architecture

```
ResearchTool
├── FLAREPlanner (lookahead=3, value_propagation=True)
├── HarmonicMemoryStore (MEMORA dual-layer)
└── ToolRegistry (AutoTool inertia tracking)
```

## Usage

```bash
# 运行研究任务
py active_skills/ai-research/run_ai_research.py research '{"task": "研究AI Agent规划"}'

# 添加研究记忆
py active_skills/ai-research/run_ai_research.py add '{"content": "FLARE saves 30% cost", "entities": ["FLARE", "cost"]}'

# 搜索研究记忆
py active_skills/ai-research/run_ai_research.py search '{"query": "FLARE", "limit": 3}'

# 获取下一工具 (AutoTool 惯性)
py active_skills/ai-research/run_ai_research.py next '{"current": "research_scan"}'

# 查看状态
py active_skills/ai-research/run_ai_research.py stats
```

## Actions

| Action | Description | Parameters |
|--------|-------------|------------|
| research | 执行研究任务 | task (str), use_planner (bool) |
| add | 添加研究记忆 | content (str), entities (list) |
| search | 搜索研究记忆 | query (str), mode (str), limit (int) |
| next | 获取下一工具 | current (str) |
| stats | 查看统计 | - |

## FLARE Planner

Future-aware planning with lookahead:

```python
planner = FLAREPlanner(lookahead_steps=3, value_propagation=True, commitment_threshold=0.7)
plan = planner.plan("Research AI agents")
```

**特点:**
- 防止 myopic commitment (只看眼前)
- Limited commitment strategies (FULL/SOFT/FLEXIBLE)
- Value propagation across steps

## MEMORA Memory

Dual-layer harmonic memory:

```python
memory = HarmonicMemoryStore()
memory.add("FLARE planner content", entities=["FLARE", "planner"])
results = memory.retrieve("FLARE", mode="harmonic", limit=5)
```

**特点:**
- Primary Abstractions + Concrete Values
- Harmonic retrieval (平衡 semantic + cue)
- 98% token reduction

## AutoTool

Graph-based tool selection with inertia:

```python
registry = ToolRegistry()
registry.learn_from_trajectory(["scan", "analyze", "write", "review"])
next_tool = registry.select_next("analyze")
```

**特点:**
- Tool Usage Inertia (工具惯性)
- 30% LLM inference cost reduction
- Efficiency tracking

## Examples

### 研究任务
```bash
py active_skills/ai-research/run_ai_research.py research '{"task": "研究自治Agent架构"}'
```

### 记忆管理
```bash
# 添加关键发现
py active_skills/ai-research/run_ai_research.py add '{"content": "MEMORA achieves 98% token reduction", "entities": ["MEMORA", "memory"]}'

# 搜索相关发现
py active_skills/ai-research/run_ai_research.py search '{"query": "memory efficiency"}'
```

### 工作流预测
```bash
# 基于当前工具预测下一个
py active_skills/ai-research/run_ai_research.py next '{"current": "research_analyze"}'
# 返回: research_write (via graph, 效率 95%)
```

## Implementation

- Python runner: `active_skills/ai-research/run_ai_research.py`
- Research library: `ai_memory_system/ai_research_tool.py`
- FLARE: `30-scripts-tools/05-AI-RESEARCH/flare_planner.py`
- MEMORA: `30-scripts-tools/05-AI-RESEARCH/harmonic_memory.py`
- AutoTool: `30-scripts-tools/05-AI-RESEARCH/autotool_selector.py`

## Dependencies

```bash
pip install sentence-transformers numpy
```

环境变量:
- `LOCAL_LLM_MODEL` - LLM model (default: qwen2.5:1.5b)
- `LOCAL_LLM_BASE_URL` - LLM API (default: http://localhost:11434)
