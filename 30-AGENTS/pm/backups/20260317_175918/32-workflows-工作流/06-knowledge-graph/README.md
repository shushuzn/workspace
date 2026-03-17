# 06 - 知识图谱更新工作流 (Level 6)

**版本:** v5.0  
**创建时间:** 2026-03-05 16:40  
**状态:** 🟢 生产就绪

---

## 📋 工作流说明

### 功能 (Level 6)
- 从 Level 4 聚类结果提取实体
- 建立研究网络关系
- 自动更新知识图谱
- 整合多层次分析数据

### 输入
- Level 4 输出：`clusters/clusters.json`
- Level 2 输出：`classified/all_classified.json`
- 实体提取规则
- 关系提取规则

### 输出
- 知识图谱 JSON 文件
- 研究网络数据
- 保存位置：`knowledge-graph/materials-kg.json`

---

## 🔄 数据流转

```
Level 4 (主题聚类)
    ↓
clusters.json
    ↓
[06-knowledge-graph]
    ↓
materials-kg.json (知识图谱)
```

---

## 🔗 相关链接

### 上游工作流
- [[../04-topic-clustering/README]] - Level 4: 主题聚类 (主要输入)
- [[../02-paper-classification/README]] - Level 2: 分类标注 (辅助输入)
- [[../00-auto-research/README]] - 总控工作流

### 知识图谱目录
- [[../../knowledge-graph]] - 知识图谱主目录
- [[../../knowledge-graph/enhanced-v3]] - 增强图谱 V3
- [[../../knowledge-graph/visualization]] - 可视化

### 脚本
- [[../../30-scripts/auto-update-knowledge-graph]] - 自动更新脚本
- [[../../11-research/scripts/generate_feature_importance]] - 特征重要性

### 文档
- [[../WORKFLOW_INDEX]] - 工作流总索引
- [[../../15-docs/MATERIALS-KNOWLEDGE-GRAPH]] - 知识图谱文档
- [[../../15-docs/KNOWLEDGE-GRAPH-AUTOMATION]] - 图谱自动化

### 研究项目
- [[../../11-research/PROJECT_INDEX]] - 研究项目索引
- [[../../11-research/cnt-research/README]] - CNT 项目 (使用图谱)

---

## 🔙 反向链接

**链接到本文档的文件:**
- [[../WORKFLOW_INDEX]] - 工作流总索引
- [[../00-auto-research/README]] - 总控工作流
- [[../04-topic-clustering/README]] - Level 4 (引用 Level 6 输出)
- [[../../knowledge-graph/README]] - 知识图谱目录

---

*最后更新:* 2026-03-06 23:13
