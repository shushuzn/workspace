# AutoTool: Efficient Tool Selection for LLM Agents

**Version:** 1.0  
**Based on:** arXiv:2511.14650 (AAAI 2026)  
**Status:** Proposed  
**Last Updated:** 2026-03-23

---

## 核心问题

### 当前瓶颈

| 方法 | 问题 |
|------|------|
| ReAct | 每步调用 LLM 选择工具，推理成本高 |
| ToolBench | 需要大量工具描述，检索开销大 |
| ReWOO | 分离规划与执行，但工具选择仍需 LLM |

### 关键观察：Tool Usage Inertia

> "工具调用遵循可预测的顺序模式"

例如：
```
Search → Analyze → Write → Review
         ↑_________↑
         惯性模式
```

---

## AutoTool 核心思想

### 有向图建模

```
工具选择图:
┌─────────┐       0.7       ┌─────────┐
│ Search  │ ──────────────→ │ Analyze │
└─────────┘                 └─────────┘
     ↑                            │
     │                            ↓
     └────────────────────────────┘
              0.9 (惯性)
```

**图结构：**
- 节点 = 工具
- 边 = 转移概率 (基于历史轨迹)
- 权重 = 惯性强度

### 工作流程

```
1. 从历史轨迹构建工具图
2. 学习转移概率
3. 遍历图结构选择工具
4. 最小化 LLM 调用
```

---

## 架构设计

### ToolGraph

```python
class ToolGraph:
    def __init__(self):
        self.nodes: Set[str] = {}           # 工具
        self.edges: Dict[str, Dict[str, float]] = {}  # 转移概率
        self.inertia_threshold: float = 0.6  # 惯性阈值
    
    def add_trajectory(self, trajectory: List[str]):
        """从轨迹学习"""
        for i in range(len(trajectory) - 1):
            self._add_edge(trajectory[i], trajectory[i+1])
    
    def select_tool(self, current_tool: str) -> Optional[str]:
        """基于惯性选择下一个工具"""
        if current_tool not in self.edges:
            return None
        
        next_tools = self.edges[current_tool]
        max_prob = max(next_tools.values())
        
        if max_prob >= self.inertia_threshold:
            return max(next_tools, key=next_tools.get)
        return None
```

### AutoTool 框架

```python
class AutoTool:
    def __init__(self, tools: List[Tool], llm: LLM):
        self.graph = ToolGraph()
        self.tools = {t.name: t for t in tools}
        self.llm = llm
        self.use_graph = True
    
    def select_and_execute(self, state: AgentState) -> ToolResult:
        if self.use_graph:
            next_tool = self._graph_select(state.current_tool)
            if next_tool:
                return self._execute_tool(next_tool, state)
        
        # 回退到 LLM 选择
        return self._llm_select_and_execute(state)
```

---

## 与 OpenClaw 集成

### 工具注册表

OpenClaw 有 **352 个工具**，工具选择是关键瓶颈。

| 当前方式 | AutoTool 方式 |
|----------|---------------|
| 每步 LLM 选择 | 基于历史惯性图 |
| 成本高 | 节省 30% |
| 速度慢 | 图遍历 O(1) |

### 集成点

```python
# 30-scripts-tools/ 工具注册
TOOL_REGISTRY = {
    "search": ["analyze", "write"],
    "analyze": ["write", "review"],
    "write": ["review", "submit"],
    "review": ["search", "submit"]
}

# 惯性转移概率
TOOL_INERTIA = {
    ("search", "analyze"): 0.8,
    ("analyze", "write"): 0.9,
    ("write", "review"): 0.7
}
```

---

## 实现状态

| 组件 | 状态 |
|------|------|
| ToolGraph | ✅ 已完成 |
| AutoTool 选择器 | ✅ 已完成 |
| OpenClaw 集成 | ⏳ 待完成 |

---

## 关联文件

- `30-scripts-tools/05-AI-RESEARCH/autotool_selector.py` - 实现代码
- `06-research/AI-研究/02-Models/AutoTool_v1.0.md` - 本文档

---

## 参考

- Jia & Li "AutoTool: Efficient Tool Selection for Large Language Model Agents" arXiv:2511.14650 (AAAI 2026)
