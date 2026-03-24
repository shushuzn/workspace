# 📖 记忆系统快速使用指南

**版本:** 1.0  
**更新时间:** 2026-03-17  
**状态:** 生产就绪

---

## 🚀 5 分钟快速开始

### 1. 基础使用

```python
# 最简单的使用方式
from memory_engine_autonomous import AutonomousEngine

engine = AutonomousEngine()
memory = engine.process("今天学习了 Python 异步编程")
print(memory)
```

### 2. 质量评估

```python
from memory_quality_assessor import QualityAssessor

assessor = QualityAssessor()
score = assessor.evaluate(memory)
print(f"质量评分：{score}/100")
```

### 3. 搜索记忆

```python
from memory_search_v2 import MemorySearch

search = MemorySearch()
results = search.query("Python 编程", limit=5)
for r in results:
    print(f"- {r.content}")
```

---

## 📚 完整功能示例

### 处理记忆 (完整流程)

```python
from memory_engine_autonomous import AutonomousEngine
from memory_quality_assessor import QualityAssessor
from memory_association_basic import AssociationAnalyzer

# 1. 处理记忆
engine = AutonomousEngine()
memory = engine.process({
    'content': '学习了记忆系统架构设计',
    'timestamp': '2026-03-17',
    'tags': ['学习', '架构', '记忆系统'],
    'source': '工作会议'
})

# 2. 评估质量
assessor = QualityAssessor()
quality = assessor.evaluate(memory)
print(f"质量评分：{quality.score}/100")
print(f"维度评分：{quality.dimensions}")

# 3. 查找关联
association = AssociationAnalyzer()
links = association.find(memory)
print(f"找到 {len(links)} 个关联记忆:")
for link in links:
    print(f"  - {link.content} (相似度：{link.similarity:.2f})")

# 4. 存储记忆
engine.store(memory)
print("记忆已存储!")
```

---

### 搜索记忆

```python
from memory_search_v2 import MemorySearch

search = MemorySearch()

# 关键词搜索
results = search.keyword_search("记忆系统", limit=10)

# 语义搜索
results = search.semantic_search("如何优化记忆架构", limit=5)

# 组合搜索
results = search.advanced_search(
    query="记忆优化",
    tags=['架构', '设计'],
    min_quality=0.7,
    date_range=('2026-03-01', '2026-03-17')
)

# 打印结果
for i, result in enumerate(results, 1):
    print(f"{i}. {result.content}")
    print(f"   质量：{result.quality_score:.2f}")
    print(f"   标签：{', '.join(result.tags)}")
    print()
```

---

### 批量处理

```python
from memory_engine_autonomous import AutonomousEngine
from concurrent.futures import ThreadPoolExecutor

engine = AutonomousEngine()

# 批量处理 (并行)
raw_memories = [
    {'content': '记忆 1', 'tags': ['学习']},
    {'content': '记忆 2', 'tags': ['工作']},
    # ... 更多记忆
]

# 方式 1: 简单批量
memories = engine.batch_process(raw_memories)

# 方式 2: 并行批量 (更快)
with ThreadPoolExecutor(max_workers=4) as executor:
    memories = list(executor.map(engine.process, raw_memories))

print(f"处理完成：{len(memories)} 个记忆")
```

---

### 质量监控

```python
from memory_quality_assessor import QualityAssessor
from memory_util_health import HealthMonitor

assessor = QualityAssessor()
monitor = HealthMonitor()

# 获取所有记忆
all_memories = engine.get_all_memories()

# 评估所有记忆
scores = []
for memory in all_memories:
    score = assessor.evaluate(memory)
    scores.append(score)

# 统计分析
avg_score = sum(scores) / len(scores)
low_quality = [s for s in scores if s < 0.5]

print(f"总记忆数：{len(all_memories)}")
print(f"平均质量：{avg_score:.2f}")
print(f"低质量记忆：{len(low_quality)} ({len(low_quality)/len(all_memories)*100:.1f}%)")

# 健康报告
report = monitor.generate_report()
print(report)
```

---

### 遗忘管理

```python
from memory_forgetting_v1 import ForgettingEngine
from memory_quality_assessor import QualityAssessor

forgetting = ForgettingEngine()
assessor = QualityAssessor()

# 获取低质量记忆
all_memories = engine.get_all_memories()
low_quality = []

for memory in all_memories:
    score = assessor.evaluate(memory)
    if score < 0.3:  # 质量低于 30%
        low_quality.append(memory)

# 归档低质量记忆
for memory in low_quality:
    forgetting.archive(memory.id, reason='low_quality')
    print(f"已归档：{memory.id}")

# 或者压缩
for memory in low_quality[:5]:  # 只压缩前 5 个
    forgetting.compress(memory.id)
    print(f"已压缩：{memory.id}")
```

---

### 冲突检测与解决

```python
from memory_conflict_detector import ConflictDetector
from memory_conflict_resolver import ConflictResolver

detector = ConflictDetector()
resolver = ConflictResolver()

# 检测冲突
conflicts = detector.detect_all()
print(f"发现 {len(conflicts)} 个冲突:")

for conflict in conflicts:
    print(f"\n冲突类型：{conflict.type}")
    print(f"记忆 1: {conflict.memory1.content}")
    print(f"记忆 2: {conflict.memory2.content}")
    print(f"矛盾点：{conflict.contradiction}")

# 解决冲突
for conflict in conflicts[:3]:  # 解决前 3 个
    resolution = resolver.resolve(conflict)
    print(f"\n解决方案：{resolution.strategy}")
    print(f"保留：{resolution.keep}")
    print(f"归档：{resolution.archive}")
```

---

### 蒸馏压缩

```python
from memory_distiller_v1 import Distiller
from memory_distiller_llm import LLMDistiller

# 基础蒸馏
distiller = Distiller()
compressed = distiller.compress(long_memory)
print(f"原始长度：{len(long_memory.content)}")
print(f"压缩后：{len(compressed.content)}")
print(f"压缩率：{(1 - len(compressed.content)/len(long_memory.content))*100:.1f}%")

# LLM 辅助蒸馏 (更智能)
llm_distiller = LLMDistiller()
key_points = llm_distiller.extract_key_points(long_memory)
summary = llm_distiller.summarize(long_memory)

print("\n关键点:")
for point in key_points:
    print(f"  - {point}")

print(f"\n摘要：{summary}")
```

---

### 仪表板数据

```python
from memory_dashboard_v1 import DashboardGenerator

dashboard = DashboardGenerator()

# 生成完整仪表板
report = dashboard.generate_full_report()

print(f"总记忆数：{report.total_memories}")
print(f"今日新增：{report.today_added}")
print(f"平均质量：{report.avg_quality:.2f}")
print(f"关联总数：{report.total_links}")

# 质量分布
print("\n质量分布:")
for range_name, count in report.quality_distribution.items():
    print(f"  {range_name}: {count} ({count/report.total_memories*100:.1f}%)")

# 保存仪表板
dashboard.save_dashboard('MEMORY-DASHBOARD.md')
print("\n仪表板已保存到 MEMORY-DASHBOARD.md")
```

---

## 🔧 高级用法

### 自定义配置

```python
from memory_engine_autonomous import AutonomousEngine

config = {
    'quality_threshold': 0.7,      # 质量阈值
    'max_associations': 10,         # 最大关联数
    'enable_caching': True,         # 启用缓存
    'cache_ttl': 600,               # 缓存过期时间 (秒)
    'parallel_processing': True,    # 并行处理
    'auto_forget': False,           # 自动遗忘
}

engine = AutonomousEngine(config=config)
```

---

### 性能分析

```python
from memory_perf_profiler import PerformanceProfiler

profiler = PerformanceProfiler()

# 开始分析
profiler.start_timer('process_memory')
memory = engine.process(raw_memory)
profiler.end_timer('process_memory')

profiler.start_timer('search')
results = search.query("test")
profiler.end_timer('search')

# 查看统计
stats = profiler.get_stats('process_memory')
print(f"平均处理时间：{stats['avg']:.3f}s")
print(f"最快：{stats['min']:.3f}s")
print(f"最慢：{stats['max']:.3f}s")

# 完整报告
print(profiler.report())
```

---

### 缓存管理

```python
from memory_perf_prefetch import CacheManager

cache = CacheManager()

# 设置缓存
cache.set('search:python', results, ttl=300)

# 获取缓存
cached_results = cache.get('search:python')
if cached_results:
    print("使用缓存结果!")
else:
    print("缓存未命中，重新搜索")

# 清空缓存
cache.clear()
```

---

### 多 Agent 协作

```python
from memory_multi_agent import MultiAgentMemory
from memory_federated import FederatedMemory

# 多 Agent 共享记忆
multi_agent = MultiAgentMemory()

# Agent 1 写入
multi_agent.write(agent_id='agent1', memory=memory1)

# Agent 2 读取
memories = multi_agent.read(agent_id='agent2', query="共享知识")

# 联邦记忆
federated = FederatedMemory()
federated.sync_nodes()  # 同步所有节点
```

---

## 🧪 测试与调试

### 单元测试

```python
import unittest
from memory_quality_assessor import QualityAssessor

class TestQualityAssessor(unittest.TestCase):
    
    def setUp(self):
        self.assessor = QualityAssessor()
    
    def test_evaluate_high_quality(self):
        memory = {'content': '高质量内容', 'tags': ['test']}
        score = self.assessor.evaluate(memory)
        self.assertGreater(score, 0.7)
    
    def test_evaluate_low_quality(self):
        memory = {'content': '', 'tags': []}
        score = self.assessor.evaluate(memory)
        self.assertLess(score, 0.3)

if __name__ == '__main__':
    unittest.main()
```

---

### 集成测试

```python
from memory_test_integration import IntegrationTester

tester = IntegrationTester()

# 运行所有测试
results = tester.run_all_tests()

print(f"通过：{results.passed}")
print(f"失败：{results.failed}")
print(f"跳过：{results.skipped}")

# 详细报告
for test in results.tests:
    status = "✅" if test.passed else "❌"
    print(f"{status} {test.name}: {test.duration:.3f}s")
```

---

## 📊 最佳实践

### 1. 记忆处理

```python
# ✅ 好的做法
memory = engine.process({
    'content': '清晰的内容',
    'tags': ['相关', '标签'],
    'source': '来源',
    'timestamp': '2026-03-17'
})

# ❌ 不好的做法
memory = engine.process("一段没有元数据的文本")
```

### 2. 搜索优化

```python
# ✅ 好的做法 - 使用缓存
results = search.query("常用查询", use_cache=True)

# ❌ 不好的做法 - 每次都重新搜索
results = search.query("常用查询")  # 无缓存
```

### 3. 批量操作

```python
# ✅ 好的做法 - 并行处理
memories = engine.batch_process(memories, parallel=True)

# ❌ 不好的做法 - 串行处理大量数据
for m in memories:
    engine.process(m)  # 慢!
```

### 4. 质量管理

```python
# ✅ 好的做法 - 定期评估
for memory in all_memories:
    if assessor.evaluate(memory) < 0.3:
        forgetting.archive(memory)

# ❌ 不好的做法 - 从不清理
# 记忆系统越来越慢...
```

---

## 🐛 常见问题

### Q1: 处理速度慢怎么办？

```python
# 解决方案 1: 启用并行处理
engine = AutonomousEngine(parallel=True)

# 解决方案 2: 启用缓存
cache = CacheManager(enable=True)

# 解决方案 3: 批量处理
memories = engine.batch_process(raw_memories)
```

### Q2: 内存占用过高？

```python
# 解决方案 1: 定期清理缓存
cache.clear()

# 解决方案 2: 压缩旧记忆
forgetting.compress(old_memories)

# 解决方案 3: 限制关联数量
config = {'max_associations': 5}
```

### Q3: 搜索结果不准确？

```python
# 解决方案 1: 使用语义搜索
results = search.semantic_search(query)

# 解决方案 2: 调整质量阈值
results = search.query(query, min_quality=0.8)

# 解决方案 3: 添加标签过滤
results = search.query(query, tags=['相关标签'])
```

---

## 📖 更多资源

- **完整文档:** `MEMORY-CORE-DESIGN.md`
- **清理报告:** `MEMORY-CLEANUP-REPORT.md`
- **脚本清单:** `MEMORY-SCRIPTS-INVENTORY.md`
- **实验功能:** 查看 `memory_exp_*.py` 系列

---

## 🆘 获取帮助

```python
# 查看帮助
python memory_engine_autonomous.py --help

# 查看版本
python memory_quality_assessor.py --version

# 运行测试
python memory_test_integration.py
```

---

*Happy Memorizing!* 🐾
