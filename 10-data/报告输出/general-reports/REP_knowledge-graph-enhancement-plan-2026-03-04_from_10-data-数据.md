# 🕸️ 知识图谱增强计划

**创建时间:** 2026-03-04 23:59  
**当前状态:** 基础功能就绪  
**下一步:** 摘要提取 + 关系增强

---

## 📊 当前状态

### 图谱统计

| 指标 | 数值 | 状态 |
|------|------|------|
| **实体数量** | 38 个 | ✅ 已构建 |
| **关系数量** | 139 个 | ✅ 已构建 |
| **实体类型** | 4 种 | ✅ Concept/Paper/Author/Org |
| **关系类型** | 4 种 | ✅ co_occurrence/related_work/contemporary/writes |

### 文件格式

| 格式 | 文件 | 大小 | 用途 |
|------|------|------|------|
| **JSON** | graph.json | 2.2 KB | 程序读取 |
| **GraphML** | graph.graphml | 2.3 KB | Gephi/Neo4j |
| **Mermaid** | graph.mmd | 0.5 KB | Markdown 渲染 |

---

## 🎯 增强方向

### 1. 摘要提取 ⭐⭐⭐⭐⭐

**目标:** 为每篇论文提取关键摘要

**来源:**
- P-Note 的"10 维度分析"
- P-Note 的"核心方法"
- P-Note 的"关键发现"

**实现:**
```python
# extract-summaries.py
def extract_summary_from_pnote(file_path):
    content = file_path.read_text(encoding="utf-8")
    
    summary = {
        "title": "",           # 论文标题
        "arxiv_id": "",        # arXiv ID
        "key_findings": [],    # 关键发现 (前 5 维度)
        "methods": [],         # 核心方法
        "confidence": 0.0      # 置信度
    }
    
    # 提取逻辑...
    return summary
```

**状态:** ⏳ 脚本已创建，需优化解析逻辑

---

### 2. 关系增强 ⭐⭐⭐⭐

**当前关系:**
- `co_occurrence` (共现) - 40 个
- `related_work` (相关工作) - 60 个
- `contemporary` (同时代) - 36 个
- `writes` (作者写论文) - 3 个

**新增关系:**
- `cites` (引用) - 从参考文献提取
- `extends` (扩展) - 从"改进"关键词提取
- `critiques` (反驳) - 从"局限性"提取
- `uses_method` (使用方法) - 从方法名提取

**实现:**
```python
# 在 kg-builder.py 中添加
relation_patterns = {
    "cites": ["引用", "cite", "based on"],
    "extends": ["扩展", "extend", "改进"],
    "critiques": ["局限性", "limitation", "不足"],
    "uses_method": ["使用", "employ", "采用"]
}
```

**状态:** ⏳ 待实现

---

### 3. 可视化增强 ⭐⭐⭐⭐

**当前:**
- Mermaid 基础图表
- GraphML 可导入 Gephi

**增强:**
- D3.js 交互式可视化
- 时间线视图
- 主题聚类视图
- 搜索功能

**实现:**
```html
<!-- knowledge-graph/visualization/index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>知识图谱可视化</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
</head>
<body>
    <div id="graph"></div>
    <script>
        // D3.js 力导向图
        // ...
    </script>
</body>
</html>
```

**状态:** ⏳ 待创建

---

### 4. 自动更新 ⭐⭐⭐

**当前:** 手动运行 kg-builder.py

**增强:** 集成到 n8n 工作流

**n8n 节点:**
```
Daily 6AM → kg-builder.py → 更新图谱 → Git 提交
```

**状态:** ⏳ 待配置

---

## 📋 执行清单

### 第 1 阶段：摘要提取 (高优先级)

- [ ] 优化 P-Note 解析逻辑
- [ ] 提取标题/arXiv ID
- [ ] 提取 10 维度分析
- [ ] 提取核心方法
- [ ] 保存到 paper-summaries.json
- [ ] 合并到知识图谱

**预计时间:** 30 分钟

---

### 第 2 阶段：关系增强 (中优先级)

- [ ] 添加引用关系提取
- [ ] 添加扩展关系提取
- [ ] 添加反驳关系提取
- [ ] 更新 kg-builder.py
- [ ] 重新构建图谱

**预计时间:** 45 分钟

---

### 第 3 阶段：可视化 (中优先级)

- [ ] 创建 D3.js 交互式图表
- [ ] 添加搜索功能
- [ ] 添加过滤器
- [ ] 部署到 visualization/index.html

**预计时间:** 60 分钟

---

### 第 4 阶段：自动化 (低优先级)

- [ ] 创建 n8n 工作流
- [ ] 配置每日 6AM 触发
- [ ] 添加 Git 提交
- [ ] 测试完整流程

**预计时间:** 30 分钟

---

## 🎯 优先级排序

| 增强方向 | 价值 | 工作量 | 优先级 |
|---------|------|--------|--------|
| **摘要提取** | ⭐⭐⭐⭐⭐ | 30 分钟 | 最高 |
| **关系增强** | ⭐⭐⭐⭐ | 45 分钟 | 高 |
| **可视化** | ⭐⭐⭐⭐ | 60 分钟 | 中 |
| **自动化** | ⭐⭐⭐ | 30 分钟 | 低 |

---

## 📊 预期效果

### 优化前

```json
{
  "entities": [
    {
      "id": "paper_2602_23681",
      "type": "Paper",
      "properties": {
        "arxiv_id": "2602.23681"
      }
    }
  ],
  "relations": []
}
```

### 优化后

```json
{
  "entities": [
    {
      "id": "paper_2602_23681",
      "type": "Paper",
      "properties": {
        "arxiv_id": "2602.23681",
        "title": "ODAR: Adaptive Routing for LLM Reasoning",
        "abstract": "提出自适应路由方法，减少 82% 计算成本...",
        "key_findings": ["问题定义", "核心方法", "实验设计"],
        "confidence": 0.95
      }
    }
  ],
  "relations": [
    {
      "source": "paper_2602_23681",
      "target": "paper_2602_23668",
      "type": "extends",
      "confidence": 0.8
    }
  ]
}
```

---

## 🔗 相关文件

- `knowledge-graph/extract-summaries.py` - 摘要提取脚本
- `knowledge-graph/scripts/kg-builder.py` - 图谱构建脚本
- `reports/knowledge-graph-enhancement-plan-2026-03-04.md` - 本计划

---

*知识图谱增强计划 · 2026-03-04 23:59*
