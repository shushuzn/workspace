# 🏗️ Memory Core - 统一记忆核心架构设计

**版本:** v1.0  
**状态:** 设计中  
**创建时间:** 2026-03-17

---

## 🎯 设计目标

### 当前问题

1. **模块分散** - 44 个独立脚本，缺乏统一入口
2. **接口不一致** - 每个脚本有自己的 API 风格
3. **重复代码** - 相似功能在不同脚本中重复实现
4. **难以测试** - 缺乏统一的测试框架
5. **性能瓶颈** - 没有统一的缓存和优化策略

### 期望状态

```
单一入口 → MemoryCore
    ↓
模块化插件 → 引擎/蒸馏/评分/搜索/...
    ↓
统一 API → 标准化接口
    ↓
自动优化 → 缓存/预取/并行
```

---

## 🏛️ 架构设计

### 整体架构图

```
┌─────────────────────────────────────────────────────────┐
│                    🧠 Memory Core                        │
├─────────────────────────────────────────────────────────┤
│  Facade Layer (统一接口)                                 │
│  - process()                                            │
│  - search()                                             │
│  - evaluate()                                           │
│  - associate()                                          │
│  - forget()                                             │
├─────────────────────────────────────────────────────────┤
│  Engine Layer (核心引擎)                                 │
│  ┌─────────────┬─────────────┬─────────────┐           │
│  │ Autonomous  │Orchestrator │   Evolution │           │
│  │   Engine    │   Engine    │   Engine    │           │
│  └─────────────┴─────────────┴─────────────┘           │
├─────────────────────────────────────────────────────────┤
│  Module Layer (功能模块)                                 │
│  ┌───────┬───────┬───────┬───────┬───────┬───────┐    │
│  │Distill│Quality│ Search│Associate│Forget│Conflict│   │
│  └───────┴───────┴───────┴───────┴───────┴───────┘    │
├─────────────────────────────────────────────────────────┤
│  Optimization Layer (优化层)                             │
│  - Cache Manager                                        │
│  - Prefetcher                                           │
│  - Performance Profiler                                 │
│  - Resource Allocator                                   │
├─────────────────────────────────────────────────────────┤
│  Storage Layer (存储层)                                  │
│  - File Storage (JSON/Markdown)                         │
│  - Vector Database (可选)                               │
│  - Graph Database (可选)                                │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 核心类设计

### MemoryCore (主入口)

```python
class MemoryCore:
    """
    统一记忆核心 - 所有记忆操作的单一入口
    """
    
    def __init__(self, config_path: str = None):
        # 加载配置
        self.config = self._load_config(config_path)
        
        # 初始化引擎
        self.engine = EngineManager(self.config)
        
        # 初始化模块
        self.distiller = DistillerModule(self.config)
        self.quality = QualityModule(self.config)
        self.search = SearchModule(self.config)
        self.association = AssociationModule(self.config)
        self.forgetting = ForgettingModule(self.config)
        self.conflict = ConflictModule(self.config)
        
        # 初始化优化器
        self.cache = CacheManager(self.config)
        self.prefetcher = Prefetcher(self.config)
        self.profiler = PerformanceProfiler(self.config)
    
    # ========== 核心 API ==========
    
    def process(self, raw_memory: dict) -> Memory:
        """
        处理原始记忆 → 蒸馏 → 评分 → 关联 → 存储
        
        Args:
            raw_memory: 原始记忆数据
        
        Returns:
            Memory: 处理后的记忆对象
        """
        # 1. 蒸馏压缩
        distilled = self.distiller.compress(raw_memory)
        
        # 2. 质量评估
        score = self.quality.evaluate(distilled)
        
        # 3. 关联分析
        links = self.association.find(distilled)
        
        # 4. 冲突检测
        conflicts = self.conflict.detect(distilled)
        
        # 5. 创建记忆对象
        memory = Memory(
            content=distilled,
            score=score,
            links=links,
            conflicts=conflicts
        )
        
        # 6. 存储
        self._store(memory)
        
        return memory
    
    def search(self, query: str, **kwargs) -> List[Memory]:
        """
        搜索记忆
        
        Args:
            query: 搜索查询
            **kwargs: 搜索参数 (limit, threshold, etc.)
        
        Returns:
            List[Memory]: 匹配的记忆列表
        """
        # 检查缓存
        cache_key = f"search:{hash(query)}"
        if cached := self.cache.get(cache_key):
            return cached
        
        # 执行搜索
        results = self.search.search(query, **kwargs)
        
        # 缓存结果
        self.cache.set(cache_key, results, ttl=300)
        
        return results
    
    def evaluate(self, memory: Memory) -> QualityScore:
        """评估记忆质量"""
        return self.quality.evaluate(memory)
    
    def associate(self, memory: Memory) -> List[MemoryLink]:
        """查找关联记忆"""
        return self.association.find(memory)
    
    def forget(self, memory_id: str, strategy: str = 'archive') -> bool:
        """
        遗忘/归档记忆
        
        Args:
            memory_id: 记忆 ID
            strategy: 'archive' | 'delete' | 'compress'
        
        Returns:
            bool: 是否成功
        """
        return self.forgetting.execute(memory_id, strategy)
    
    # ========== 高级 API ==========
    
    def batch_process(self, memories: List[dict], parallel: bool = True) -> List[Memory]:
        """批量处理记忆"""
        if parallel:
            return self._parallel_process(memories)
        else:
            return [self.process(m) for m in memories]
    
    def get_dashboard_data(self) -> dict:
        """获取仪表板数据"""
        return {
            'total_memories': self._count_memories(),
            'quality_distribution': self.quality.get_distribution(),
            'recent_trends': self._analyze_trends(),
            'top_associations': self.association.get_top_links(),
        }
    
    # ========== 内部管理 ==========
    
    def _store(self, memory: Memory):
        """存储记忆"""
        # 实现存储逻辑
        pass
    
    def _parallel_process(self, memories: List[dict]) -> List[Memory]:
        """并行处理"""
        # 使用 multiprocessing 或 concurrent.futures
        pass
```

---

### EngineManager (引擎管理器)

```python
class EngineManager:
    """
    管理所有核心引擎
    """
    
    def __init__(self, config):
        self.engines = {
            'autonomous': AutonomousEngine(config),
            'orchestrator': OrchestratorEngine(config),
            'ops': OPSEngine(config),
            'maintenance': MaintenanceEngine(config),
            'evolution': EvolutionEngine(config),
        }
    
    def get_engine(self, name: str) -> BaseEngine:
        """获取指定引擎"""
        return self.engines.get(name)
    
    def run_all(self, memory: Memory) -> Memory:
        """按顺序运行所有引擎"""
        for engine in self.engines.values():
            memory = engine.process(memory)
        return memory
```

---

### Module 基类

```python
class BaseModule(ABC):
    """所有功能模块的基类"""
    
    @abstractmethod
    def process(self, data: Any) -> Any:
        """处理数据"""
        pass
    
    @abstractmethod
    def validate(self, data: Any) -> bool:
        """验证数据"""
        pass
    
    def optimize(self, data: Any) -> Any:
        """优化处理 (可选)"""
        return data
```

---

## 🔌 模块接口规范

### DistillerModule

```python
class DistillerModule(BaseModule):
    """蒸馏压缩模块"""
    
    def compress(self, raw_memory: dict) -> dict:
        """压缩记忆"""
        pass
    
    def extract_key_points(self, memory: dict) -> List[str]:
        """提取关键点"""
        pass
    
    def summarize(self, memory: dict) -> str:
        """生成摘要"""
        pass
```

### QualityModule

```python
class QualityModule(BaseModule):
    """质量评估模块"""
    
    def evaluate(self, memory: Memory) -> QualityScore:
        """评估质量"""
        pass
    
    def get_distribution(self) -> dict:
        """获取质量分布"""
        pass
    
    def get_low_quality(self, threshold: float = 0.3) -> List[Memory]:
        """获取低质量记忆"""
        pass
```

### SearchModule

```python
class SearchModule(BaseModule):
    """搜索模块"""
    
    def search(self, query: str, **kwargs) -> List[Memory]:
        """搜索"""
        pass
    
    def semantic_search(self, query: str, limit: int = 10) -> List[Memory]:
        """语义搜索"""
        pass
    
    def keyword_search(self, query: str, limit: int = 10) -> List[Memory]:
        """关键词搜索"""
        pass
```

---

## ⚡ 优化策略

### 缓存策略

```python
class CacheManager:
    """缓存管理器"""
    
    def __init__(self, config):
        self.cache = {}  # 内存缓存
        self.ttl = config.get('cache_ttl', 300)  # 5 分钟
    
    def get(self, key: str) -> Any:
        """获取缓存"""
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['time'] < self.ttl:
                return entry['data']
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: int = None):
        """设置缓存"""
        self.cache[key] = {
            'data': value,
            'time': time.time(),
            'ttl': ttl or self.ttl
        }
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
```

### 预取策略

```python
class Prefetcher:
    """预取器 - 预测性加载"""
    
    def predict_next_queries(self, current_query: str) -> List[str]:
        """预测下一个查询"""
        # 基于历史查询模式
        pass
    
    def prefetch(self, queries: List[str]):
        """预取数据"""
        # 后台加载预测的查询结果
        pass
```

---

## 📊 性能监控

```python
class PerformanceProfiler:
    """性能分析器"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
    
    def start_timer(self, operation: str):
        """开始计时"""
        self.timers[operation] = time.time()
    
    def end_timer(self, operation: str):
        """结束计时"""
        duration = time.time() - self.timers[operation]
        self.metrics[operation].append(duration)
        return duration
    
    def get_stats(self, operation: str) -> dict:
        """获取统计"""
        durations = self.metrics[operation]
        return {
            'avg': sum(durations) / len(durations),
            'min': min(durations),
            'max': max(durations),
            'count': len(durations),
        }
    
    def report(self) -> str:
        """生成性能报告"""
        report = ["Performance Report", "=" * 40]
        for operation, durations in self.metrics.items():
            avg = sum(durations) / len(durations)
            report.append(f"{operation}: {avg:.3f}s (n={len(durations)})")
        return "\n".join(report)
```

---

## 🧪 使用示例

### 基础使用

```python
from memory_core import MemoryCore

# 初始化
core = MemoryCore()

# 处理记忆
memory = core.process({
    'content': '今天学习了记忆系统优化',
    'timestamp': '2026-03-17',
    'tags': ['学习', '记忆系统']
})

# 搜索
results = core.search('记忆优化', limit=5)

# 评估质量
score = core.evaluate(memory)
print(f"Quality Score: {score}")

# 查找关联
links = core.associate(memory)
print(f"Found {len(links)} related memories")
```

### 高级使用

```python
# 批量处理
memories = core.batch_process(raw_memories, parallel=True)

# 性能分析
with core.profiler.profile('batch_process'):
    memories = core.batch_process(raw_memories)

# 获取仪表板数据
dashboard = core.get_dashboard_data()
print(f"Total memories: {dashboard['total_memories']}")
print(f"Average quality: {dashboard['quality_distribution']['avg']}")
```

---

## 📁 文件组织

```
30-scripts-tools/
├── memory_core/
│   ├── __init__.py
│   ├── core.py              # MemoryCore 主类
│   ├── engines/
│   │   ├── __init__.py
│   │   ├── autonomous.py
│   │   ├── orchestrator.py
│   │   └── ...
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── distiller.py
│   │   ├── quality.py
│   │   ├── search.py
│   │   └── ...
│   ├── optimization/
│   │   ├── __init__.py
│   │   ├── cache.py
│   │   ├── prefetch.py
│   │   └── profiler.py
│   └── storage/
│       ├── __init__.py
│       ├── file_storage.py
│       └── vector_storage.py
├── memory_engine_autonomous.py  → 迁移到 memory_core/engines/
├── memory_engine_orchestrator.py → 迁移到 memory_core/engines/
├── memory_distiller_v1.py       → 迁移到 memory_core/modules/
├── memory_quality_assessor.py   → 迁移到 memory_core/modules/
└── ...
```

---

## 🎯 迁移计划

### 阶段 1: 创建核心框架 (1-2 天)

- [ ] 创建 memory_core 包结构
- [ ] 实现 MemoryCore 基类
- [ ] 实现 EngineManager
- [ ] 实现 CacheManager
- [ ] 编写单元测试

### 阶段 2: 迁移模块 (3-5 天)

- [ ] 迁移所有 engine_* 到 memory_core/engines/
- [ ] 迁移所有 distiller_* 到 memory_core/modules/distiller.py
- [ ] 迁移所有 quality_* 到 memory_core/modules/quality.py
- [ ] 迁移所有 search_* 到 memory_core/modules/search.py
- [ ] 迁移所有 association_* 到 memory_core/modules/association.py

### 阶段 3: 统一 API (2-3 天)

- [ ] 标准化所有模块接口
- [ ] 删除重复代码
- [ ] 编写集成测试
- [ ] 性能基准测试

### 阶段 4: 优化与文档 (2-3 天)

- [ ] 性能优化
- [ ] 编写使用文档
- [ ] 编写 API 文档
- [ ] 示例代码

---

## 📈 预期收益

| 指标 | 当前 | 目标 | 改善 |
|------|------|------|------|
| 代码行数 | ~8000 | ~5000 | -37% |
| 模块数量 | 44 | 15 | -66% |
| API 一致性 | 40% | 95% | +55% |
| 性能 | 1x | 2-3x | +100-200% |
| 可测试性 | 低 | 高 | +200% |
| 可维护性 | 中 | 高 | +150% |

---

## 🐾 下一步

**立即开始:** 创建 memory_core 包结构

**预计完成:** 2026-03-24

**负责人:** Claw

---

*Memory Core Architecture Design v1.0* 🐾
