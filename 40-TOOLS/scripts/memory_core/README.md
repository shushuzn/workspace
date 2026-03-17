# 🧠 Memory Core 使用指南

**版本:** 2.0.0  
**创建时间:** 2026-03-17  
**状态:** 生产就绪

---

## 🚀 快速开始

### 1. 最简单的使用

```python
from memory_core import MemoryCore

# 初始化
core = MemoryCore()

# 处理记忆
memory = core.process("今天学习了记忆系统架构设计")

print(f"记忆 ID: {memory.id}")
print(f"质量分数：{memory.score:.2f}")
print(f"内容：{memory.content}")
```

### 2. 带配置的使用

```python
from memory_core import MemoryCore, MemoryConfig

# 自定义配置
config = MemoryConfig(
    quality_threshold=0.7,
    enable_cache=True,
    cache_ttl=600,
    parallel_processing=True
)

# 初始化
core = MemoryCore(config=config)

# 或者直接使用参数
core = MemoryCore(
    quality_threshold=0.7,
    enable_cache=True
)
```

---

## 📖 核心 API

### MemoryCore.process()

处理原始记忆 → 蒸馏 → 评分 → 关联 → 存储

```python
# 字符串输入
memory = core.process("简单的记忆内容")

# 字典输入 (带元数据)
memory = core.process({
    'content': '深度学习笔记',
    'tags': ['AI', '深度学习'],
    'source': '课程学习',
    'timestamp': '2026-03-17'
})

# 访问结果
print(memory.id)        # 记忆 ID
print(memory.content)   # 内容
print(memory.score)     # 质量分数 (0-1)
print(memory.links)     # 关联记忆 ID 列表
print(memory.metadata)  # 元数据
```

### MemoryCore.search()

搜索记忆

```python
# 基本搜索
results = core.search("记忆系统", limit=10)

# 遍历结果
for memory in results:
    print(f"{memory.id}: {memory.content[:50]}... (score={memory.score:.2f})")
```

### MemoryCore.batch_process()

批量处理记忆

```python
memories = [
    "记忆 1 内容",
    "记忆 2 内容",
    {"content": "记忆 3", "tags": ["标签"]},
]

# 串行处理
results = core.batch_process(memories, parallel=False)

# 并行处理 (更快)
results = core.batch_process(memories, parallel=True)

print(f"处理了 {len(results)} 个记忆")
print(f"平均分数：{sum(m.score for m in results)/len(results):.2f}")
```

### MemoryCore.evaluate()

评估记忆质量

```python
score = core.evaluate(memory)
print(f"质量分数：{score:.2f}")
```

### MemoryCore.associate()

查找关联记忆

```python
related = core.associate(memory, limit=5)
print(f"找到 {len(related)} 个关联记忆")
```

### MemoryCore.forget()

遗忘/归档记忆

```python
# 归档
success = core.forget(memory_id, strategy='archive')

# 删除
success = core.forget(memory_id, strategy='delete')

# 压缩
success = core.forget(memory_id, strategy='compress')
```

---

## 📊 统计与监控

### 获取统计信息

```python
stats = core.get_stats()

print(f"总记忆数：{stats['total']}")
print(f"平均分数：{stats['avg_score']:.2f}")
print(f"最低分：{stats['min_score']:.2f}")
print(f"最高分：{stats['max_score']:.2f}")
print(f"高质量：{stats['high_quality']}")
print(f"低质量：{stats['low_quality']}")
```

### 获取仪表板数据

```python
dashboard = core.get_dashboard_data()

print(f"总记忆数：{dashboard['total_memories']}")
print(f"平均分数：{dashboard['avg_score']:.2f}")
print(f"最近记忆：{len(dashboard['recent_memories'])} 个")
```

### 性能报告

```python
report = core.get_performance_report()
print(report)
```

输出示例:
```
Performance Report
==================================================
process                  : 0.0023s avg (0.0012-0.0045s, n=10)
search                   : 0.0015s avg (0.0008-0.0023s, n=5)
evaluate                 : 0.0005s avg (0.0003-0.0008s, n=10)
==================================================
Total time: 0.0341s
```

---

## ⚡ 高级功能

### 缓存管理

```python
# 查看缓存统计
if core.cache:
    stats = core.cache.get_stats()
    print(f"缓存大小：{stats['size']}")
    print(f"命中次数：{stats['hits']}")
    print(f"未命中次数：{stats['misses']}")
    print(f"命中率：{stats['hit_rate']}")

# 清空缓存
core.cache.clear()

# 禁用缓存
core = MemoryCore(enable_cache=False)
```

### 性能分析

```python
# 重置统计
core.reset_stats()

# 处理一些记忆
for i in range(10):
    core.process(f"记忆 {i}")

# 查看性能报告
report = core.get_performance_report()
print(report)

# 查看特定操作的统计
stats = core.profiler.get_stats('process')
print(f"处理操作:")
print(f"  平均时间：{stats['avg']:.4f}s")
print(f"  最短时间：{stats['min']:.4f}s")
print(f"  最长时间：{stats['max']:.4f}s")
```

### 自定义配置

```python
from memory_core import MemoryConfig

config = MemoryConfig(
    # 质量阈值
    quality_threshold=0.6,
    low_quality_threshold=0.3,
    high_quality_threshold=0.8,
    
    # 关联配置
    max_associations=15,
    min_similarity=0.5,
    
    # 缓存配置
    enable_cache=True,
    cache_ttl=600,      # 10 分钟
    cache_max_size=2000,
    
    # 性能配置
    parallel_processing=True,
    max_workers=8,
    batch_size=200,
    
    # 遗忘配置
    auto_forget=False,
    forget_after_days=180,
    
    # 日志配置
    enable_logging=True,
    log_level='INFO',
    log_file='my_memory.log'
)

core = MemoryCore(config=config)
```

### 保存和加载配置

```python
# 保存配置
config.save_to_file('memory_config.json')

# 从文件加载配置
config = MemoryConfig(config_path='memory_config.json')
core = MemoryCore(config=config)
```

---

## 🛠️ 工具模块

### MemoryHelper - 辅助工具

```python
from memory_core.utils import MemoryHelper

# 生成 ID
mem_id = MemoryHelper.generate_id("记忆内容")

# 清洗文本
clean = MemoryHelper.clean_text("  多余  空格  测试  ")

# 生成摘要
summary = MemoryHelper.summarize(long_content, max_length=200)

# 格式化显示
formatted = MemoryHelper.format_memory(memory.to_dict())

# 合并记忆
merged = MemoryHelper.merge_memories([mem1, mem2, mem3])

# 比较相似度
similarity = MemoryHelper.compare_memories(mem1.to_dict(), mem2.to_dict())
```

### MemoryValidator - 验证器

```python
from memory_core.utils import MemoryValidator

# 验证单个记忆
is_valid, errors = MemoryValidator.validate(memory_dict)

if not is_valid:
    print("验证失败:")
    for error in errors:
        print(f"  - {error}")

# 批量验证
results = MemoryValidator.validate_batch(memories)

print(f"总数：{results['total']}")
print(f"有效：{results['valid']}")
print(f"无效：{results['invalid']}")

# 清理数据
sanitized = MemoryValidator.sanitize(memory_dict)
```

---

## 📁 存储系统

### FileStorage - 文件存储

```python
from memory_core.storage import FileStorage
from pathlib import Path

# 初始化
storage = FileStorage(
    storage_dir=Path('13-memory-记忆系统/memories'),
    backup=True
)

# 保存
storage.save(memory.id, memory.to_dict())

# 加载
data = storage.load(memory.id)

# 删除 (移动到归档)
storage.delete(memory.id)

# 列出所有
all_ids = storage.list_all()
print(f"共有 {len(all_ids)} 个记忆")

# 统计
stats = storage.get_stats()
print(f"存储目录：{stats['storage_dir']}")
print(f"记忆数量：{stats['count']}")
print(f"备份启用：{stats['backup_enabled']}")
```

---

## 🧪 完整示例

### 示例 1: 学习笔记管理

```python
from memory_core import MemoryCore

core = MemoryCore()

# 添加学习笔记
notes = [
    {"content": "Python 异步编程：async/await 语法", "tags": ["Python", "异步"]},
    {"content": "记忆系统架构：MemoryCore 核心类设计", "tags": ["架构", "设计"]},
    {"content": "Git 分支策略：Git Flow 工作流", "tags": ["Git", "版本控制"]},
]

# 批量处理
memories = core.batch_process(notes, parallel=True)

# 搜索相关笔记
results = core.search("Python", limit=5)
print(f"找到 {len(results)} 个 Python 相关笔记")

# 查看统计
stats = core.get_stats()
print(f"平均质量：{stats['avg_score']:.2f}")
```

### 示例 2: 研究论文管理

```python
from memory_core import MemoryCore, MemoryConfig

# 高质量阈值设置
config = MemoryConfig(
    quality_threshold=0.7,
    high_quality_threshold=0.85,
    max_associations=20
)

core = MemoryCore(config=config)

# 添加论文笔记
papers = [
    {
        "content": "Attention Is All You Need - Transformer 架构开创性论文",
        "tags": ["AI", "Transformer", "注意力机制"],
        "source": "NeurIPS 2017"
    },
    {
        "content": "BERT: Pre-training of Deep Bidirectional Transformers",
        "tags": ["AI", "BERT", "预训练"],
        "source": "NAACL 2019"
    },
]

for paper in papers:
    memory = core.process(paper)
    
    # 只保留高质量论文
    if memory.score >= 0.85:
        print(f"[高质量] {paper['content'][:50]}...")
    else:
        print(f"[待改进] {paper['content'][:50]}... (score={memory.score:.2f})")
```

### 示例 3: 知识库构建

```python
from memory_core import MemoryCore
from memory_core.storage import FileStorage
from pathlib import Path

core = MemoryCore()
storage = FileStorage(Path('knowledge-base'))

# 构建知识库
topics = [
    "机器学习基础概念",
    "深度学习神经网络",
    "自然语言处理技术",
    "计算机视觉方法",
]

for topic in topics:
    memory = core.process({
        "content": f"{topic} 的详细笔记内容...",
        "tags": ["AI", topic],
        "category": "knowledge"
    })
    
    # 存储到文件系统
    storage.save(memory.id, memory.to_dict())
    print(f"已存储：{topic}")

# 导出知识库
all_ids = storage.list_all()
print(f"\n知识库共有 {len(all_ids)} 个主题")
```

---

## 🐛 常见问题

### Q1: 如何处理大量记忆？

```python
# 使用批量处理 + 并行
large_batch = ["记忆" + str(i) for i in range(1000)]
results = core.batch_process(large_batch, parallel=True)

# 分批处理
batch_size = 100
for i in range(0, len(large_batch), batch_size):
    batch = large_batch[i:i+batch_size]
    core.batch_process(batch, parallel=True)
```

### Q2: 如何提高搜索准确性？

```python
# 1. 添加详细标签
memory = core.process({
    "content": "内容",
    "tags": ["标签 1", "标签 2", "标签 3"]
})

# 2. 使用更具体的查询
results = core.search("Python 异步编程 async await")

# 3. 调整质量阈值
config = MemoryConfig(quality_threshold=0.8)
core = MemoryCore(config=config)
```

### Q3: 如何管理低质量记忆？

```python
# 获取所有记忆
stats = core.get_stats()
print(f"低质量记忆：{stats['low_quality']}")

# 批量归档低质量记忆
for memory in core._memories.values():
    if memory.score < 0.3:
        core.forget(memory.id, strategy='archive')
```

### Q4: 如何备份记忆数据？

```python
from memory_core.storage import FileStorage
import shutil

storage = FileStorage(Path('memories'), backup=True)

# 自动备份 (每次保存时)
storage.save(memory.id, memory.to_dict())

# 手动备份整个存储
shutil.copytree('memories', 'memories_backup')
```

---

## 📈 性能优化建议

1. **启用缓存**
   ```python
   core = MemoryCore(enable_cache=True, cache_ttl=600)
   ```

2. **使用并行处理**
   ```python
   core = MemoryCore(parallel_processing=True, max_workers=8)
   ```

3. **批量操作**
   ```python
   # 好
   core.batch_process(memories)
   
   # 不好
   for m in memories:
       core.process(m)
   ```

4. **定期清理**
   ```python
   # 清空缓存
   core.cache.clear()
   
   # 归档低质量记忆
   core.forget(low_quality_id, 'archive')
   ```

---

## 🔗 相关文档

- **架构设计:** `MEMORY-CORE-DESIGN.md`
- **快速指南:** `MEMORY-QUICKSTART.md`
- **脚本清单:** `MEMORY-SCRIPTS-INVENTORY.md`
- **优化报告:** `MEMORY-CLEANUP-REPORT.md`

---

*Memory Core v2.0 - Unified Memory System* 🐾
