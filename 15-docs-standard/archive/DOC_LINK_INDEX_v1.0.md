# 内部链接索引

**创建时间:** 2026-03-06 22:58  
**最后更新:** 2026-03-07 15:21  
**目的:** 集中管理所有 Obsidian 内部链接，便于维护和查找

---

## 📁 核心文档链接

### 根目录文件
```markdown
[[README]] - Workspace 导航首页
[[SOUL]] - 身份定义
[[AGENTS]] - 工作区规范
[[USER]] - 用户信息
[[TOOLS]] - 工具配置
[[IDENTITY]] - 身份简介
[[HEARTBEAT]] - 心跳任务清单
```

### 记忆系统
```markdown
[[memory/2026-03-06]] - 今日记忆日志
[[13-memory/MEMORY]] - 长期记忆库
[[13-memory/2026-03-05]] - 昨日记忆
```

---

## 🔬 研究项目

### LIG 导电率预测 (投稿中)

**项目索引:** [[11-research/PROJECT_INDEX]]

#### 论文文档
```markdown
[[11-research/paper/00_abstract]] - 摘要
[[11-research/paper/01_introduction]] - 引言
[[11-research/paper/02_related_work]] - 相关工作
[[11-research/paper/03_methods]] - 方法
[[11-research/paper/04_results]] - 结果与讨论
[[11-research/paper/05_conclusion]] - 结论
```

#### 投稿材料
```markdown
[[11-research/paper/cover_letter]] - 投稿信
[[11-research/paper/highlights]] - 亮点 (5 条)
[[11-research/paper/submission_checklist]] - 投稿检查清单
[[11-research/paper/timeline]] - 投稿时间线
[[11-research/paper/journal_selection]] - 期刊选择分析
[[11-research/paper/MANIFEST]] - 文件清单
```

#### 数据与代码
```markdown
[[11-research/github_repo]] - GitHub 仓库信息
[[11-research/models]] - 模型文件目录
[[11-research/figures]] - 可视化图表
[[11-research/scripts/gp_run]] - GP 训练脚本
[[11-research/scripts/predict]] - 预测脚本
```

#### 旧版草稿
```markdown
[[11-research/ORGANIZED_PROJECT/01_Paper_Draft/PAPER_DRAFT_V2]] - 完整论文草稿
```

---

### CNT 性能预测 (启动阶段)

**项目索引:** [[11-research/PROJECT_INDEX]]

#### 项目文档
```markdown
[[11-research/cnt-research/README]] - 项目总览
[[11-research/cnt-research/literature/README]] - 文献收集指南
[[11-research/cnt-research/literature/WEEKLY_PLAN]] - 周计划
[[11-research/cnt-research/literature/starter_papers]] - 起点论文
[[11-research/cnt-research/literature/SEARCH_GUIDE]] - 检索指南
[[11-research/cnt-research/data/data_extraction_template]] - 数据提取模板
```

#### 脚本工具
```markdown
[[11-research/cnt-research/scripts/cnt_gp_run]] - GP 模型训练
[[11-research/cnt-research/scripts/cnt_shap_analysis]] - SHAP 分析
[[11-research/cnt-research/scripts/cnt_data_extractor]] - 数据提取
[[11-research/cnt-research/scripts/active_learning_simulator]] - 主动学习模拟
```

---

### 理论工作 (100% 完成)

```markdown
[[11-research/theory/01_theoretical_framework]] - 理论框架
[[11-research/theory/03_deep_derivation]] - 深度推导
[[11-research/theory/04_numerical_simulation]] - 数值模拟
[[11-research/theory/05_temperature_dependent_properties]] - 温度依赖属性
[[11-research/theory/06_2d_axisymmetric_model]] - 2D 轴对称模型
```

---

## 📚 文档中心 (15-docs)

### 索引与导航
```markdown
[[15-docs/FOLDER-INDEX]] - 文件夹完整索引
[[15-docs/README]] - 文档中心首页
[[15-docs/LINK_INDEX]] - 本文件 (链接索引)
[[15-docs/OUTPUT-FORMAT]] - 输出格式规范 (2026-03-07)
[[15-docs/SESSION-CHECKLIST]] - 会话启动检查清单 (2026-03-07)
```

### 系统文档
```markdown
[[15-docs/SYSTEM-ARCHITECTURE]] - 系统架构
[[15-docs/DEPLOYMENT-GUIDE]] - 部署指南
[[15-docs/USAGE-EXAMPLES]] - 使用示例
[[15-docs/TROUBLESHOOTING]] - 故障排除
[[15-docs/CLI-REFERENCE]] - CLI 参考
```

### 材料科学项目
```markdown
[[15-docs/AI-FOR-MATERIALS-TRACKING]] - AI 材料追踪
[[15-docs/MATERIALS-SYSTEM-COMPLETE]] - 材料系统完成报告
[[15-docs/MATERIALS-KNOWLEDGE-GRAPH]] - 材料知识图谱
[[15-docs/CGCNN-vs-MEGNet]] - 模型对比
```

### 自动化与部署
```markdown
[[15-docs/AUTOMATED-RESEARCH-SYSTEM]] - 自动化研究系统
[[15-docs/MATERIALS-DOCKER-DEPLOYMENT]] - Docker 部署
[[15-docs/KUBERNETES-DEPLOYMENT]] - Kubernetes 部署
[[15-docs/SECURITY-HARDENING]] - 安全加固
```

---

## 🛠️ 工具与技能

### 脚本目录
```markdown
[[30-scripts]] - PowerShell 脚本目录
[[31-skills]] - 技能包目录
[[32-workflows]] - 工作流目录
```

### 技能文档
```markdown
[[skills/proactive-agent-lite/README]] - 主动代理技能
[[skills/proactive-agent-lite/SKILL]] - 技能说明
[[skills/nano-pdf/SKILL]] - PDF 编辑技能
```

---

## 📡 数据收集

### arXiv
```markdown
[[40-arxiv]] - arXiv 收集目录
```

### Medium
```markdown
[[41-medium]] - Medium 监控目录
```

### HackerNews
```markdown
[[42-hackernews]] - HackerNews 追踪目录
```

---

## 🗄️ 归档与日志

```markdown
[[90-archive]] - 历史归档
[[92-tests]] - 测试文件
[[99-workspace-archive]] - 工作区归档
[[logs]] - 系统日志
```

---

## 🔗 跨文档链接网络

### 从 HEARTBEAT.md 出发
```markdown
[[HEARTBEAT]] → [[11-research/paper/*]] (9 篇论文文档)
              → [[11-research/github_repo]]
              → [[11-research/cnt-research/*]] (2 个 CNT 文档)
              → [[memory/2026-03-06]]
              → [[MEMORY]]
```

### 从 SOUL.md 出发
```markdown
[[SOUL]] → [[IDENTITY]], [[USER]], [[AGENTS]], [[TOOLS]]
         → [[13-memory/MEMORY]], [[memory/2026-03-06]]
         → [[11-research/paper/README]], [[11-research/cnt-research/README]]
         → [[HEARTBEAT]], [[15-docs/FOLDER-INDEX]]
```

### 从 memory/2026-03-06.md 出发
```markdown
[[memory/2026-03-06]] → [[11-research/paper/*]] (4 个论文文档)
                      → [[11-research/models]], [[11-research/figures]]
                      → [[11-research/cnt-research/*]] (3 个 CNT 文档)
                      → [[HEARTBEAT]], [[SOUL]], [[AGENTS]], [[TOOLS]], [[USER]]
                      → [[MEMORY]], [[2026-03-05]]
```

### 从 PROJECT_INDEX.md 出发
```markdown
[[11-research/PROJECT_INDEX]] → LIG 项目 (10+ 文档)
                               → CNT 项目 (8+ 文档)
                               → 理论工作 (5 文档)
                               → 记忆系统 (2 文档)
                               → 核心文档 (5 文档)
```

---

## 📊 链接统计

| 类别 | 链接数 |
|------|--------|
| 核心文档 | 7 |
| 记忆系统 | 5 |
| LIG 项目 | 15+ |
| CNT 项目 | 10+ |
| 理论工作 | 5 |
| 文档中心 | 16+ |
| 工具技能 | 10+ |
| 数据收集 | 8 |
| 归档日志 | 4 |
| 脚本索引 | 60+ |
| PowerShell 脚本 | 27 |
| 技能包 | 6 |
| 工作流 | 15+ |
| **总计** | **500+** |

---

## 🎯 维护指南

### 添加新链接
1. 在对应类别下添加 `[[路径/文件名]] - 说明`
2. 更新链接统计
3. 如创建新文档，确保有反向链接

### 检查断链
- 定期搜索 `[[` 检查格式
- 确保目标文件存在
- 更新已移动文件的链接

### 优化导航
- 保持链接层次清晰
- 添加简短说明
- 使用 emoji 增强可读性

---

*最后更新:* 2026-03-06 23:08

---

## 🔙 反向链接

**链接到本文档的文件:**
- [[../README]] - Workspace 导航首页 (引用 LINK_INDEX 作为总索引)
- [[../11-research/PROJECT_INDEX]] - 研究项目索引 (交叉引用)
- [[../11-research/scripts/README]] - Python 脚本索引 (引用总链接)
- [[../30-scripts/README]] - PowerShell 脚本索引 (引用总链接)
- [[../31-skills/README]] - 技能包索引 (引用总链接)
- [[../41-medium/README]] - Medium 监控 (引用总链接)
- [[../13-memory/README]] - 记忆系统 (引用总链接)
- [[../90-archive/README]] - 归档目录 (引用总链接)
- [[FOLDER-INDEX]] - 文件夹索引 (姐妹文档)

**维护说明:**
- 每次添加新索引文档时，在此添加反向链接
- 保持链接统计更新 (当前 272+ 链接)
- 定期检查断链

---
