# 00 - 自动化研究总控

**版本:** v4.0  
**创建时间:** 2026-03-05 16:40  
**状态:** 🟢 生产就绪

---

## 📋 工作流说明

### 功能
- 一键运行完整自动化流程 (Level 1-6)
- 自动错误处理
- 完整日志记录
- 每日 02:00-05:00 自动运行

### 子工作流

| 序号 | 工作流 | 时间 | 用时 | 输出 |
|------|--------|------|------|------|
| 1 | [[../01-arxiv-collect/README]] | 02:00 | 2 分钟 | 论文 Markdown+JSON |
| 2 | [[../02-paper-classification/README]] | 02:30 | 3 分钟 | 分类标注数据 |
| 3 | [[../03-trend-analysis/README]] | 03:00 | 3 分钟 | 趋势分析报告 |
| 4 | [[../04-topic-clustering/README]] | 03:30 | 4 分钟 | 主题聚类数据 |
| 5 | [[../05-report-gen/README]] | 04:00 | 1 分钟 | 每日研究报告 |
| 6 | [[../06-knowledge-graph/README]] | 04:30 | 2 分钟 | 知识图谱 JSON |
| **总计** | - | - | **15 分钟** | - |

---

## 🔗 相关链接

### 子工作流
- [[../01-arxiv-collect/README]] - Level 1: 论文收集
- [[../02-paper-classification/README]] - Level 2: 分类标注
- [[../03-trend-analysis/README]] - Level 3: 趋势分析
- [[../04-topic-clustering/README]] - Level 4: 主题聚类
- [[../05-report-gen/README]] - Level 5: 报告生成
- [[../06-knowledge-graph/README]] - Level 6: 知识图谱

### 质量控制
- [[../00-quality-control/README]] - 质量检查工作流

### 输出目录
- [[../40-arxiv/daily]] - 每日论文归档
- [[../21-reports]] - 研究报告
- [[../knowledge-graph]] - 知识图谱

### 脚本
- [[../../30-scripts/arxiv-workflow]] - arXiv 工作流脚本
- [[../../30-scripts/auto-update-knowledge-graph]] - 图谱更新

### 文档
- [[../WORKFLOW_INDEX]] - 工作流总索引
- [[../../15-docs/AUTOMATED-RESEARCH-SYSTEM]] - 自动化系统文档

---

## 🔙 反向链接

**链接到本文档的文件:**
- [[../WORKFLOW_INDEX]] - 工作流总索引 (引用总控流程)
- [[../../README]] - Workspace 导航
- [[../../HEARTBEAT]] - 心跳任务 (记录运行状态)

---

*最后更新:* 2026-03-06 23:13
