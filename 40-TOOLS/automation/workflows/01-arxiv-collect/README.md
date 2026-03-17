# 01 - ArXiv 收集工作流 (Level 1)

**版本:** v4.0  
**创建时间:** 2026-03-05 16:40  
**状态:** 🟢 生产就绪

---

## 📋 工作流说明

### 功能 (Level 1)
- 自动收集 arXiv 材料科学论文
- 支持 9 个 cond-mat 类别
- 自动分类和归档
- 输出 JSON 格式供 Level 2 使用

### 输入
- arXiv RSS Feed
- 9 个材料科学类别

### 输出
- Markdown 格式论文文件
- JSON 格式原始数据 (供 Level 2 使用)
- 保存位置：`40-arxiv/daily/YYYY/MM/DD/`

---

## 🔄 数据流转

```
arXiv RSS Feed
    ↓
[01-arxiv-collect]
    ↓
papers.json (原始数据)
    ↓
[02-paper-classification] (Level 2)
```

---

## 🔗 相关链接

### 上下游工作流
- [[../00-auto-research/README]] - 总控工作流
- [[../02-paper-classification/README]] - Level 2: 分类标注 (下游)

### 数据目录
- [[../../40-arxiv]] - arXiv 收集目录
- [[../../40-arxiv/daily]] - 每日论文归档
- [[../../40-arxiv/classified]] - 已分类论文

### 脚本
- [[../../30-scripts/arxiv-workflow]] - arXiv 工作流脚本
- [[../../30-scripts/arxiv-sync-start]] - 同步启动脚本
- [[../../11-research/scripts/arxiv_lig_monitor]] - LIG 监控脚本

### 文档
- [[../WORKFLOW_INDEX]] - 工作流总索引
- [[../../15-docs/AI-FOR-MATERIALS-TRACKING]] - AI 材料追踪
- [[../../15-docs/PAPER-ANALYSIS-PIPELINE]] - 论文分析管道

---

## 🔙 反向链接

**链接到本文档的文件:**
- [[../WORKFLOW_INDEX]] - 工作流总索引
- [[../00-auto-research/README]] - 总控工作流
- [[../02-paper-classification/README]] - Level 2 (引用 Level 1 输出)

---

*最后更新:* 2026-03-06 23:13
