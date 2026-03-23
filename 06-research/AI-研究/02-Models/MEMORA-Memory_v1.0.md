# MEMORA: Harmonic Memory Representation

**Version:** 1.0  
**Based on:** arXiv:2602.03315  
**Status:** Proposed  
**Last Updated:** 2026-03-23

---

## 核心问题

### 记忆系统的抽象-细节矛盾

| 问题 | 现状 | 需求 |
|------|------|------|
| 抽象多 → 细节丢失 | 摘要过多 | 保留关键细节 |
| 细节多 → 检索低效 | 线性存储 | 高效检索 |
| 扩展性差 | 固定格式 | 自适应结构 |

### MEMORA 解决方案

```
记忆结构:
┌─────────────────────────────────────┐
│     Primary Abstraction (抽象层)      │
│  - 记忆摘要                           │
│  - 索引到具体值                       │
│  - Cue Anchors (检索锚点)             │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│     Concrete Values (具体层)          │
│  - 原始记忆内容                        │
│  - 时间戳                             │
│  - 关联记忆引用                        │
└─────────────────────────────────────┘
```

---

## 架构设计

### HarmonicMemoryEntry

```python
class HarmonicMemoryEntry:
    primary_abstraction: str      # 抽象摘要
    concrete_values: List[MemoryValue]  # 具体记忆值
    cue_anchors: List[str]       # 检索锚点
    connections: List[str]        # 关联记忆 ID
    abstraction_level: float     # 抽象程度 0-1
    last_accessed: datetime
    access_count: int
```

### HarmonicMemoryStore

```python
class HarmonicMemoryStore:
    abstractions: Dict[str, HarmonicMemoryEntry]  # 抽象索引
    concrete_values: Dict[str, MemoryValue]         # 具体值存储
    cue_index: Dict[str, Set[str]]                 # 锚点 → 记忆 ID
    connection_graph: Dict[str, Set[str]]           # 关联图
    
    def add(self, memory: str, cue_anchors: List[str] = None):
        # 1. 创建抽象
        # 2. 存储具体值
        # 3. 建立锚点索引
        # 4. 建立关联
    
    def retrieve(self, query: str, mode: str = "harmonic") -> List[MemoryValue]:
        # Harmonic 检索模式
```

---

## 核心算法

### 1. 双层存储

```python
def create_abstraction(self, memory: str) -> HarmonicMemoryEntry:
    # 1. 使用 LLM 生成摘要
    abstraction = self.llm.summarize(memory)
    
    # 2. 提取关键实体
    entities = self.extract_entities(memory)
    
    # 3. 生成检索锚点
    cue_anchors = self.generate_cue_anchors(memory, entities)
    
    # 4. 计算抽象层级
    level = self.calculate_abstraction_level(memory)
    
    return HarmonicMemoryEntry(
        primary_abstraction=abstraction,
        concrete_values=[MemoryValue(content=memory, timestamp=now())],
        cue_anchors=cue_anchors,
        entities=entities,
        abstraction_level=level
    )
```

### 2. Cue-Based 检索

```python
def retrieve_harmonic(self, query: str) -> List[MemoryValue]:
    """
    Harmonic 检索：结合语义相似度和锚点匹配
    """
    # 语义检索
    semantic_scores = self.semantic_search(query)
    
    # 锚点检索
    cue_scores = self.cue_search(query)
    
    # 谐波综合
    combined_scores = {}
    for memory_id in set(semantic_scores) | set(cue_scores):
        s = semantic_scores.get(memory_id, 0)
        c = cue_scores.get(memory_id, 0)
        # 谐波平均：避免一方太强掩盖另一方
        combined_scores[memory_id] = 2 * s * c / (s + c + 1e-10)
    
    return sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
```

### 3. 关联扩展

```python
def expand_via_connections(self, memory_id: str, depth: int = 2) -> Set[str]:
    """
    通过关联扩展检索范围
    """
    expanded = {memory_id}
    current = {memory_id}
    
    for _ in range(depth):
        next_layer = set()
        for mid in current:
            # 获取直接关联
            connections = self.connection_graph.get(mid, set())
            next_layer.update(connections)
        expanded.update(next_layer)
        current = next_layer
    
    return expanded
```

---

## Token 节省分析

### 对比

| 方法 | 100 条记忆 | 1000 条记忆 |
|------|-----------|-------------|
| 全量存储 | 100K tokens | 1M tokens |
| 简单摘要 | 30K tokens | 300K tokens |
| **MEMORA** | **2K tokens** | **20K tokens** |

**节省 98% token**

---

## 集成建议

| 现有模块 | 集成方式 |
|----------|----------|
| memory_distiller_v2.py | 替换为 HarmonicMemoryStore |
| 13-memory/ | 使用双层结构存储 |
| autonomous_research_agent.py | 检索记忆时使用 harmonic 模式 |

---

## 关联文件

- `30-scripts-tools/13-memory/harmonic_memory.py` - 实现代码
- `06-research/AI-研究/02-Models/MEMORA-Memory_v1.0.md` - 本文档

---

## 参考

- Xia et al. "Memora: A Harmonic Memory Representation Balancing Abstraction and Specificity" arXiv:2602.03315
