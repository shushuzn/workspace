# 自动化研究工作流索引

**创建时间:** 2026-03-06 23:13  
**位置:** `32-workflows/`  
**版本:** v4.0  
**状态:** 🟢 生产就绪

---

## 📊 完整工作流流程

```
Level 1: 论文收集 → Level 2: 分类标注 → Level 3: 趋势分析
                                              ↓
Level 6: 知识图谱 ← Level 5: 报告生成 ← Level 4: 主题聚类
```

---

## 🔄 核心工作流 (按执行顺序)

### Level 0: 用户命令执行
**索引:** [[10-user-command/README]]  
**时间:** 实时响应  
**用时:** 1-40 分钟 (依任务类型)  
**输入:** 用户指令  
**输出:** 执行结果 + 验证

**链接:**
- [[99-user-command-workflow/baseline-report]] - 基线数据报告
- [[99-user-command-workflow/test-plan]] - 测试方案

---

### Level 1: 论文收集
**索引:** [[01-arxiv-collect/README]]  
**时间:** 每日 02:00  
**用时:** 2 分钟  
**输入:** arXiv RSS Feed  
**输出:** Markdown + JSON

**链接:**
- [[../40-arxiv]] - arXiv 收集目录
- [[../40-arxiv/daily]] - 每日论文归档
- [[../scripts/arxiv_lig_monitor]] - 监控脚本

---

### Level 2: 分类标注
**索引:** [[02-paper-classification/README]]  
**时间:** 每日 02:30  
**用时:** 3 分钟  
**输入:** Level 1 JSON 输出  
**输出:** 分类标注数据

**链接:**
- [[../40-arxiv/classified]] - 已分类论文
- [[../15-docs/AI-FOR-MATERIALS-TRACKING]] - AI 材料追踪文档

---

### Level 3: 趋势分析
**索引:** [[03-trend-analysis/README]]  
**时间:** 每日 03:00  
**用时:** 3 分钟  
**输入:** 分类数据 + 关键词  
**输出:** 趋势分析报告

**链接:**
- [[../21-reports]] - 报告目录
- [[../15-docs/MATERIALS-SYSTEM-COMPLETE]] - 系统完成报告

---

### Level 4: 主题聚类
**索引:** [[04-topic-clustering/README]]  
**时间:** 每日 03:30  
**用时:** 4 分钟  
**输入:** 趋势分析结果  
**输出:** 主题聚类数据

**链接:**
- [[../22-distilled-viewpoints]] - 提炼观点
- [[../11-research]] - 研究项目目录

---

### Level 5: 报告生成
**索引:** [[05-report-gen/README]]  
**时间:** 每日 04:00  
**用时:** 1 分钟  
**输入:** 聚类结果  
**输出:** 每日研究报告

**链接:**
- [[../21-reports/daily]] - 每日报告
- [[../memory]] - 记忆系统 (记录关键发现)

---

### Level 6: 知识图谱
**索引:** [[06-knowledge-graph/README]]  
**时间:** 每日 04:30  
**用时:** 2 分钟  
**输入:** Level 4 聚类 + Level 2 分类  
**输出:** 知识图谱 JSON

**链接:**
- [[../knowledge-graph]] - 知识图谱目录
- [[../knowledge-graph/enhanced-v3]] - 增强图谱 V3
- [[../15-docs/MATERIALS-KNOWLEDGE-GRAPH]] - 图谱文档

---

## 🎯 总控与协调

### 总控工作流
**索引:** [[00-auto-research/README]]  
**功能:** 协调 Level 1-6 完整流程  
**时间:** 每日 02:00-05:00  
**总用时:** 约 15 分钟

**子工作流:**
- [[01-arxiv-collect/README]] - Level 1
- [[02-paper-classification/README]] - Level 2
- [[03-trend-analysis/README]] - Level 3
- [[04-topic-clustering/README]] - Level 4
- [[05-report-gen/README]] - Level 5
- [[06-knowledge-graph/README]] - Level 6

---

## 🛡️ 质量控制

### 质量检查工作流
**索引:** [[00-quality-control/README]]  
**功能:** 验证每个 Level 输出质量  
**检查点:**
- Level 1: 论文数量验证
- Level 2: 分类准确率
- Level 3: 趋势关键词匹配
- Level 4: 聚类合理性
- Level 5: 报告完整性
- Level 6: 图谱一致性

---

## 📝 文档与研究

### 研究文档工作流
**索引:** [[08-research-docs/README]]  
**功能:** 整理研究文档和笔记  
**链接:**
- [[../11-research/PROJECT_INDEX]] - 研究项目索引
- [[../15-docs]] - 文档中心
- [[../13-memory]] - 记忆系统

---

## 🔄 反馈循环

### 反馈循环工作流
**索引:** [[98-feedback-loop/README]]  
**功能:** 收集用户反馈，优化流程  
**链接:**
- [[../HEARTBEAT]] - 心跳任务 (收集反馈)
- [[../memory/2026-03-06]] - 记忆日志 (记录改进)

---

## 📡 监控与 API

### 监控工作流
**索引:** [[99-monitoring/README]]  
**功能:** 监控系统健康状态  
**链接:**
- [[../30-scripts/health-check]] - 健康检查脚本
- [[../30-scripts/nightly-security-audit]] - 安全审计

### API 服务
**索引:** [[96-api-service/README]]  
**功能:** 提供研究数据 API  
**链接:**
- [[../15-docs/API]] - API 文档
- [[../15-docs/MATERIALS-API-DESIGN]] - API 设计

---

## 💾 数据湖

### 数据湖工作流
**索引:** [[97-data-lake/README]]  
**功能:** 集中存储所有研究数据  
**链接:**
- [[../20-29]] - 数据报告目录
- [[../40-49]] - 收集监控目录
- [[../knowledge-graph]] - 知识图谱数据

---

## 🔗 跨文档链接

### 与项目集成
- [[../11-research/PROJECT_INDEX]] - 研究项目使用工作流输出
- [[../11-research/paper/README]] - LIG 论文参考趋势分析
- [[../11-research/cnt-research/README]] - CNT 项目使用文献收集

### 与脚本集成
- [[../30-scripts/arxiv-workflow]] - arXiv 工作流脚本
- [[../30-scripts/auto-update-knowledge-graph]] - 图谱更新脚本
- [[../30-scripts/ai-research]] - AI 研究助手

### 与记忆系统集成
- [[../13-memory/README]] - 记录工作流运行状态
- [[../13-memory/MEMORY]] - 长期记忆关键发现
- [[../memory/2026-03-06]] - 今日运行日志

### 与技能集成
- [[../31-skills/task-manager]] - 任务调度
- [[../31-skills/arxiv-translate]] - 论文翻译
- [[../31-skills/api-gateway]] - API 管理

---

## 📊 工作流统计

| 指标 | 值 |
|------|-----|
| 工作流总数 | 14 个 |
| 核心流程 | 6 个 (Level 1-6) |
| 每日运行时间 | 02:00-05:00 |
| 总处理时间 | ~15 分钟 |
| 输出文件 | 50+ /天 |
| 自动化率 | 100% |

---

## 🚀 快速开始

### 运行完整流程
```bash
cd D:\OpenClaw\workspace
py scripts/materials/automated-research-workflow.py
```

### 运行单个 Level
```bash
# Level 1: 论文收集
bash workflows/01-arxiv-collect/run.sh

# Level 6: 知识图谱
py scripts/materials/materials-knowledge-graph.py
```

### 查看运行状态
```bash
# 查看日志
Get-Content workflows/00-auto-research/logs/run.log -Tail 50
```

---

## 🔙 反向链接

**链接到本文档的文件:**
- [[../README]] - Workspace 导航首页 (引用工作流系统)
- [[../15-docs/LINK_INDEX]] - 内部链接总索引
- [[../HEARTBEAT]] - 心跳任务清单 (记录工作流状态)
- [[../11-research/PROJECT_INDEX]] - 研究项目索引 (使用工作流输出)
- [[../30-scripts/README]] - 脚本索引 (执行工作流)

---

---

## 📊 工作流文件夹索引

| 文件夹 | 说明 | 链接 |
|--------|------|------|
| `00-auto-research/` | 总控工作流 | [[00-auto-research/README]] |
| `00-quality-control/` | 质量控制 | [[00-quality-control/README]] |
| `01-arxiv-collect/` | Level 1: 收集 | [[01-arxiv-collect/README]] |
| `02-paper-classification/` | Level 2: 分类 | [[02-paper-classification/README]] |
| `03-trend-analysis/` | Level 3: 趋势 | [[03-trend-analysis/README]] |
| `04-topic-clustering/` | Level 4: 聚类 | [[04-topic-clustering/README]] |
| `05-report-gen/` | Level 5: 报告 | [[05-report-gen/README]] |
| `06-knowledge-graph/` | Level 6: 图谱 | [[06-knowledge-graph/README]] |
| `08-research-docs/` | 研究文档 | [[08-research-docs/README]] |
| `96-api-service/` | API 服务 | [[96-api-service/README]] |
| `97-data-lake/` | 数据湖 | [[97-data-lake/README]] |
| `98-feedback-loop/` | 反馈循环 | [[98-feedback-loop/README]] |
| `99-monitoring/` | 监控 | [[99-monitoring/README]] |

---

*最后更新:* 2026-03-06 23:13
