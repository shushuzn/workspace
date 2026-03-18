# Memory Compression Tools - 记忆压缩工具集

**Version:** 1.0  
**Created:** 2026-03-18  
**Status:** ✅ Complete

---

## 📋 概述

记忆压缩工具集提供完整的记忆管理解决方案，包括质量评分、去重清理、混合压缩管道、重要性评估和增量压缩。

### 工具列表

| Tool ID | 工具名称 | 功能 | 触发时机 |
|---------|---------|------|----------|
| `memory-hybrid-pipeline` | 混合压缩管道 | 整合所有压缩策略 | 每周日 |
| `memory-quality-scorer` | 质量评分工具 | 5 维度评分 (100 分制) | 每周日 |
| `memory-cleanup-compress` | 去重清理工具 | 检测重复/清理冗余 | 每周日 |
| `memory-importance-assessor` | 重要性评估 | 5 维度评分 (0-1) | 会话结束 |
| `memory-incremental-compressor` | 增量压缩 | LCS 差异存储 | 每周日 |

---

## 🛠️ 工具详情

### 1. Memory Hybrid Pipeline (混合压缩管道)

**文件:** `30-scripts-tools/memory_hybrid_pipeline.py` (22.8KB)

**功能:**
- 整合 6 种压缩策略 (去重/质量/重要性/增量/分层/LLM)
- 自动决策树选择最优压缩策略
- 批量处理 + 单文件模式

**压缩决策树:**
```
                    ┌─────────────────┐
                    │   输入记忆      │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  1. 质量评分    │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
       ┌──────▼──────┐ ┌─────▼─────┐ ┌─────▼─────┐
       │ Quality≥0.9 │ │0.7≤Q<0.9  │ │ Quality<0.7│
       └──────┬──────┘ └─────┬─────┘ └─────┬─────┘
              │              │              │
       ┌──────▼──────┐ ┌─────▼─────┐ ┌─────▼─────┐
       │3.重要性评估 │ │ 标准压缩  │ │ 归档/遗忘 │
       └──────┬──────┘ └───────────┘ └───────────┘
              │
       ┌──────┴──────┐
       │  Importance │
       └──────┬──────┘
              │
    ┌─────────┼─────────┐
    │         │         │
┌───▼───┐ ┌───▼───┐ ┌───▼───┐
│ Imp≥0.8│ │0.5≤I<0.8│ │  I<0.5 │
└───┬───┘ └───┬───┘ └───┬───┘
    │         │         │
┌───▼───┐ ┌───▼───┐ ┌───▼───┐
│蒸馏到 │ │分层压 │ │重度压 │
│MEMORY │ │缩 50% │ │缩 20% │
└───────┘ └───────┘ └───────┘
```

**使用:**
```bash
# 单文件压缩
py memory_hybrid_pipeline.py --memory "13-memory/2026-03-18.md"

# 批量处理 (最近 7 天)
py memory_hybrid_pipeline.py --batch --days 7

# 仅分析 (不执行压缩)
py memory_hybrid_pipeline.py --analyze --days 14

# 生成压缩报告
py memory_hybrid_pipeline.py --report --days 30
```

**输出示例:**
```
============================================================
Hybrid Compression Pipeline - Analysis
============================================================

[Overview]
  Total Memories: 8
  Analysis Period: 14 days

[Summary]
  Average Quality:    0.732
  Average Importance: 0.440

[Strategy Distribution]
  tiered_light: 2
  tiered_heavy: 5
  tiered_standard: 1
```

---

### 2. Memory Quality Scorer (质量评分工具)

**文件:** `30-scripts-tools/memory_quality_scorer.py` (17.7KB)

**评分维度 (总分 100 分):**

| 维度 | 权重 | 检查项 |
|------|------|--------|
| 完整性 | 25 分 | 标题/上下文/决策/理由/行动 |
| 结构化 | 20 分 | 标题层级/列表/代码块/表格 |
| 信息密度 | 20 分 | 非空行比例/平均行长度 |
| 可执行性 | 20 分 | Next Actions/量化指标/时间承诺 |
| 独特性 | 15 分 | 新概念/洞察/架构变更 |

**质量等级:**
- A (≥90): 优秀 - 直接蒸馏到 MEMORY.md
- B (80-89): 良好 - 轻度压缩保留
- C (70-79): 中等 - 标准压缩
- D (60-69): 及格 - 重度压缩
- F (<60): 不合格 - 归档或删除

**使用:**
```bash
# 评分单条记忆
py memory_quality_scorer.py --memory "13-memory/2026-03-18.md"

# 批量评分 (最近 7 天)
py memory_quality_scorer.py --batch --days 7

# 识别低质量记忆
py memory_quality_scorer.py --low-quality --days 30

# 生成质量报告
py memory_quality_scorer.py --report --days 30
```

**输出示例:**
```
============================================================
Memory Quality Report
============================================================

[Overview]
  Total Memories: 8
  Average Score:  67.42/100

[Grade Distribution]
  A:   0 (  0.0%) 
  B:   2 ( 25.0%) █████
  C:   2 ( 25.0%) █████
  D:   2 ( 25.0%) █████
  F:   2 ( 25.0%) █████
```

---

### 3. Memory Cleanup & Deduplication (去重清理工具)

**文件:** `30-scripts-tools/memory_cleanup_compress.py` (15.3KB)

**算法:**
- Jaccard 相似度检测重复
- LCS (Longest Common Subsequence) 检测冗余
- 文本清理 (空行、空白字符、重复行)

**重复类型:**
- Exact (精确重复): 哈希相同
- Near Duplicate (近似重复): 相似度≥80%
- Partial (部分重复): 相似度≥50%

**使用:**
```bash
# 检测重复
py memory_cleanup_compress.py --detect-duplicates --days 30

# 清理单条记忆
py memory_cleanup_compress.py --cleanup --memory "13-memory/2026-03-18.md"

# 批量清理 (最近 7 天)
py memory_cleanup_compress.py --batch --days 7

# 生成去重报告
py memory_cleanup_compress.py --report --days 30
```

**输出示例:**
```
============================================================
Memory Deduplication Report
============================================================

[Overview]
  Total Memories Scanned: 8
  Duplicate Pairs Found:  0
  Total Redundancy:       0 bytes

[Recommendations]
  • No duplicates found
```

---

### 4. Memory Importance Assessor (重要性评估工具)

**文件:** `30-scripts-tools/memory_importance_assessor.py` (17.7KB)

**评分维度 (总分 1.0):**

| 维度 | 权重 | 检查项 |
|------|------|--------|
| 可执行性 | 20% | Next Actions/时间承诺/量化指标 |
| 独特性 | 25% | 新工具/新概念/新洞察 |
| 时效性 | 15% | 指数衰减曲线 (30 天半衰期) |
| 影响力 | 25% | 架构变更/重大决策 |
| 连接性 | 15% | 引用链接/跨领域连接 |

**使用:**
```bash
# 评估单条记忆
py memory_importance_assessor.py --memory "13-memory/2026-03-18.md"

# 批量评估 (最近 7 天)
py memory_importance_assessor.py --batch --days 7

# 生成 JSON 报告
py memory_importance_assessor.py --report --days 14 --json
```

---

### 5. Memory Incremental Compressor (增量压缩工具)

**文件:** `30-scripts-tools/memory_incremental_compressor.py` (17.9KB)

**算法:** LCS (Longest Common Subsequence)

**功能:**
- 识别连续记忆之间的重复内容
- 只存储差异部分
- 计算冗余率和新内容比例

**使用:**
```bash
# 差异报告
py memory_incremental_compressor.py --diff --days 7

# 冗余分析
py memory_incremental_compressor.py --redundancy --days 14

# 详细报告 (JSON)
py memory_incremental_compressor.py --report --days 30 --json
```

**输出示例:**
```
============================================================
Incremental Compression - Diff Report
============================================================

[Overview]
  Total Memories:        5
  Total Original Size:   19,756 bytes
  Total Compressed Size: 19,771 bytes
  Overall Compression:   -0.1% reduction

[Content Analysis]
  Average Redundancy Rate:  0.3%
  Average New Content:      99.6%
```

---

## 🔄 工作流集成

### Session-End 工作流更新

**文件:** `30-scripts-tools/workflows/session-end.json`

**新增步骤:**
```json
{
  "step": 8,
  "tool_id": "memory-importance-assessor",
  "description": "评估当日记忆重要性",
  "parameters": {
    "memory": "13-memory/${TODAY}.md"
  }
}
```

### 每周日自动任务

**Cron 配置:**
```json
{
  "schedule": "0 5 * * 0",  // 每周日 05:00
  "command": "py 30-scripts-tools/memory_hybrid_pipeline.py --batch --days 7",
  "description": "Weekly memory compression"
}
```

---

## 📊 性能基准

| 工具 | 平均耗时 | 目标 | 状态 |
|------|---------|------|------|
| Hybrid Pipeline | ~200ms | <500ms | ✅ |
| Quality Scorer | ~100ms | <200ms | ✅ |
| Cleanup Compress | ~150ms | <300ms | ✅ |
| Importance Assessor | ~50ms | <100ms | ✅ |
| Incremental Compressor | ~120ms | <200ms | ✅ |

**测试环境:**
- 记忆数量：8 条 (14 天)
- 总大小：~60KB
- 平均每条：~7.5KB

---

## 🎯 最佳实践

### 1. 定期质量检查

每周运行质量评分，识别低质量记忆：
```bash
py memory_quality_scorer.py --low-quality --days 30
```

### 2. 去重清理

发现重复时及时清理：
```bash
py memory_cleanup_compress.py --detect-duplicates --days 30
```

### 3. 混合压缩

对重要记忆使用混合管道：
```bash
py memory_hybrid_pipeline.py --memory "13-memory/2026-03-18.md" --batch
```

### 4. 增量备份

定期运行增量压缩，减少存储：
```bash
py memory_incremental_compressor.py --diff --days 7
```

---

## 📚 相关文档

- [Memory System Architecture](./MEMORY-ARCHITECTURE.md)
- [Session Compression Guide](./SESSION-COMPRESSION.md)
- [Tools Registry](../30-scripts-tools/tools_registry.json)

---

*Last Updated: 2026-03-18 | Version: 1.0*
