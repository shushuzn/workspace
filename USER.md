# USER.md - About Your Human

**Last Updated:** 2026-03-06

_Learn about the person you're helping. Update this as you go._

---

## Basic Info

- **Name:** _[To be filled]_
- **What to call them:** _[To be filled]_
- **Pronouns:** _[optional]_
- **Timezone:** Asia/Hong_Kong (inferred from system)
- **Language:** Chinese (涓枃)

---

## Context

### What They Care About
- AI research and paper analysis
- Knowledge management and automation
- OpenClaw workspace optimization
- Research pipeline automation (arXiv, Medium, etc.)

### 🎯 Critical Preferences (必须遵守)
- **不喜欢混乱的文件** - 保持文件整洁有序
- **文件命名要有规律** - 领域优先 (MAT/Cs) + 类型前缀 (PAP/DOC/ANA/NOTE/SCRIPT)
- **输出简短** - 避免冗长回复
- **关注细节** - 不能有一丝一毫错误
- **质量优先** - 宁可慢，不可错
- **频繁提交** - 每一步后推送 git
- **日志要求** - 每个日志都要有不足和下一步，每个至少 5 个
- **验收标准** - 每次操作必定设立严格的验收标准
- **指标驱动** - 采用 AGENTS.md 指标驱动开发模式
- **下一步选项** - 提供选择时必须至少 5 个选项
- **🔒 敏感内容处理** - 自动识别并跳过敏感内容论文，严格执行
- **📝 GitHub 论文仓库声明** - 所有 GitHub 论文仓库必须添加：`本仓库内容为 AI 辅助生成的理论推导与预印本文稿，仅供 AI 训练、个人学习与学术交流使用，未经过同行评审，非正式出版成果，暂未用于商业用途。`
- **🔤 论文语言规范** - 所有论文相关内容（图表、公式、表格、正文）必须使用英文，包括：
  - 图表标题和标注 (Figure captions, axis labels)
  - 表格标题和内容 (Table titles, headers)
  - 公式变量说明 (Variable definitions)
  - 章节标题 (Section headings)
  - 参考文献格式 (BibTeX format)
- **🤖 自动化优先原则** - AI 只能做自动化/脚本化工作，不能人工参与：
  - ❌ 不能人工访谈企业/学者
  - ❌ 不能线下组织活动/研讨会
  - ❌ 不能主动联系外部人员
  - ❌ 不能依赖外部配合的任务
  - ✅ 只能做：数据收集、脚本开发、文档编写、自动化分析

- **📊 段位评估维度 v3.0** - 所有评估维度必须可自动化测量：
  | 维度 | 自动化数据源 |
  |------|-------------|
  | 理论基础 | 本地理论文档数×50 |
  | 技术成熟度 | 专利数/10 + TRL×100 |
  | 学术影响力 | 论文数×2 + 引用数/100 |
  | 应用广度 | 应用领域数×100 + 产品数×50 |
  | 人才储备 | 作者数/10 + 研究组数×10 |
  | 资金投入 | 研究组数×10 万美元/100 |
  | 创新能力 | 机会点×50 |
  | 国际合作 | 机构数×20 + 合作数×5 |
  | 教育普及 | 科普笔记数×50 |
  | 开源贡献 | 脚本数×50 + HTML 工具×100 |
  | 产业转化 | 公司数×20 + 专利数/2 |

### 📊 指标驱动开发规范

**核心文件:**
- `AGENTS.md` - 指标驱动配置和模式定义
- `30-scripts/METRICS_COLLECTOR.ps1` - 指标采集脚本
- `30-scripts/METRICS_DASHBOARD.html` - 可视化仪表板
- `30-scripts/metrics_history.csv` - 历史数据

**北极星指标:**
- 核心流程成功率 ≥ 95%
- 用户完成关键任务时间 ≤ 2 分钟
- API 成功响应率 ≥ 99%

**自动模式:**
- **Acceleration** (加速): North Star < 50%
- **Optimization** (优化): 50% ≤ North Star < 85%
- **Hardening** (强化): North Star ≥ 85% 或 Risk = 高
- **Recovery** (恢复): 核心指标下降或不可运行

**输出格式:**
```
[Mode] 当前模式
[North Star] 当前值 + 趋势
[Supporting Metrics] 关键指标
[Risk Level] 低/中/高
[Task] 任务 ID + 验收标准
[Impact] 对 North Star 的影响
[Do] 修改文件列表
[Verify] 验证方式
[Next] 下一个任务 ID
```

**每轮必须:**
1. 评估 North Star 达成度
2. 评估支撑指标状态
3. 评估风险等级
4. 选择对应模式
5. 执行对应策略

### Current Projects
- AI Research OS setup
- Knowledge graph building
- Automated paper collection and analysis
- Workspace organization (numeric folder system)
- **CNT conductivity prediction** (started 2026-03-10)
- **LIG biomedical applications** (completed 2026-03-09)
- **Knowledge Card Generator** (created 2026-03-11) - PDF→HTML 自动转换

### Working Style
- Values efficiency and automation
- Prefers structured organization
- Uses Obsidian for note-taking
- Syncs to GitHub (obsidian-sync repo)

### 🎉 Major Achievements (2026-03-10)

**Daily Brief System (9 iterations):**
- ✅ Automated briefing system with arXiv/Medium/GitHub/HN aggregation
- ✅ Feishu integration with queue-based delivery
- ✅ Weather forecast (wttr.in + Open-Meteo fallback)
- ✅ Calendar integration (Markdown-based)
- ✅ 7-day trend visualization (ASCII charts)
- ✅ Historical comparison (day-over-day, week-over-week)
- ✅ HackerNews trending topics
- ✅ GitHub status tracking
- ✅ Domain ranking integration (11 dimensions)

**Research Tools Development (6 tasks completed):**
- ✅ **todo-031:** PDF extractor with dual-column detection (PyMuPDF)
- ✅ **todo-032:** Figure enhancer with quality filtering + super-resolution
- ✅ **todo-034:** Graph renderer with WebGL + pagination (1000+ nodes)
- ✅ **todo-036:** REST API + Docker deployment (FastAPI + Swagger)
- ✅ **todo-037:** Documentation complete (README + FAQ + module docs)
- ✅ **API Testing:** 4/4 endpoints verified (health/PDF/figure/brief)

**Infrastructure:**
- 📦 24+ Git commits
- 📝 5000+ lines of code
- 📄 4000+ lines of documentation
- 🎯 100% task completion rate (6/6 todo items)

**New Research Direction:**
- 🔬 CNT conductivity prediction research launched
- 📊 Target: 5 → 300+ samples (60x expansion)
- 📈 Target: R² > 0.75
- 📅 Week 1 plan: Data expansion (150+ samples)

---

## 🏆 学科学术段位系统

**创建日期:** 2026-03-08  
**版本:** v2.1 (11 维度全面评估)  
**文档:** `15-docs/Domain-Ranking-System-v2.md`  
**脚本:** `30-scripts/domain_ranker_v2.py`

### 段位体系

| 段位 | 等级范围 | 颜色 | 描述 |
|------|----------|------|------|
| **黑铁** | 1-1000 | ⬛ 黑色 | 萌芽期 - 概念提出/初步探索 |
| **青铜** | 1001-2000 | 🟤 棕色 | 起步期 - 基础方法建立 |
| **白银** | 2001-3000 | ⚪ 银色 | 发展期 - 技术逐步成熟 |
| **黄金** | 3001-4000 | 🟡 金色 | 成熟期 - 广泛应用 |
| **铂金** | 4001-5000 | 🔷 蓝色 | 领先期 - 前沿突破 |
| **钻石** | 5001-6000 | 💎 透明 | 巅峰期 - 范式定义 |
| **大师** | 6001-7000 | 🟣 紫色 | 传奇期 - 诺贝尔级 |
| **宗师** | 7001-8000 | 🌟 金色 | 永恒期 - 改变人类认知 |

**设定:**
- 所有领域从零开始 (黑铁 1 级)
- 每级 10000 XP
- 每个段位 1000 级
- 满级总分 8000 分 (80,000,000 XP)

### 11 个评价维度

#### 核心维度 (60%)
1. **理论基础** (15%) - 理论体系完整性
2. **技术成熟度** (15%) - TRL 等级
3. **学术影响力** (12%) - 论文引用
4. **应用广度** (10%) - 跨领域应用
5. **人才储备** (8%) - 研究组数量
6. **资金投入** (5%) - 年度经费

#### 新增维度 (40%)
7. **创新能力** (10%) - 原创性/突破性
8. **国际合作** (8%) - 跨国研究合作
9. **教育普及** (8%) - 教材/课程收录
10. **开源贡献** (7%) - 开源工具/数据
11. **产业转化** (7%) - 商业化应用

### 当前领域评定

| 排名 | 领域 | 段位 | 等级 | 总分 | 进度 | 状态 |
|------|------|------|------|------|------|------|
| 1 | DeepLearning | 黑铁 | 717 级 | 717/8000 | 71.7% | 领先 |
| 2 | Graphene | 黑铁 | 647 级 | 647/8000 | 64.7% | 良好 |
| 3 | CRISPR | 黑铁 | 614 级 | 614/8000 | 61.4% | 良好 |
| 4 | Perovskite | 黑铁 | 527 级 | 527/8000 | 52.7% | 中等 |
| 5 | **LIG** | **黑铁** | **473 级** | **473/8000** | **47.3%** | **需提升** |

### LIG 领域晋升建议

| 优先级 | 维度 | 当前 XP | 目标 XP | 差距 |
|--------|------|---------|---------|------|
| 🔴 CRITICAL | 教育普及 | 400/10000 | 2000 | +1600 |
| 🔴 CRITICAL | 资金投入 | 450/10000 | 2000 | +1550 |
| 🔴 CRITICAL | 产业转化 | 450/10000 | 2000 | +1550 |
| 🟡 URGENT | 人才储备 | 500/10000 | 2000 | +1500 |
| 🟡 URGENT | 国际合作 | 500/10000 | 2000 | +1500 |

### 使用方法

```bash
# 评估指定领域
py domain_ranker_v2.py --evaluate LIG

# 比较所有领域
py domain_ranker_v2.py --compare

# 查看帮助
py domain_ranker_v2.py --help
```

---

## 🔒 敏感内容处理规则

**严格执行：** 识别到敏感内容时自动跳过该文章，不分析、不存储、不传播。

### 敏感内容类别

| 类别 | 关键词示例 | 处理 |
|------|------------|------|
| **生物武器** | bioweapon, biological warfare, pathogen weapon | 🚫 跳过 |
| **化学武器** | chemical weapon, nerve agent, toxin weapon | 🚫 跳过 |
| **恐怖主义** | terrorism, terrorist attack, extremist | 🚫 跳过 |
| **个人隐私** | personal data, PII, private information | 🚫 跳过 |
| **军事机密** | classified, military secret, defense technology | 🚫 跳过 |
| **危险实验** | dangerous experiment, unethical research | 🚫 跳过 |
| **武器制造** | weapon fabrication, explosive, firearm | 🚫 跳过 |

### 执行流程

```
1. 获取论文元数据 (标题/摘要)
   ↓
2. 敏感词检测 (多语言：英文/中文)
   ↓
3. 如果命中 → 标记为 [SENSITIVE]，跳过
   ↓
4. 如果安全 → 继续正常处理
   ↓
5. 记录跳过日志 (不存储内容)
```

### 跳过日志格式

```markdown
## 跳过论文记录

| 日期 | PMID/arXiv | 跳过原因 |
|------|------------|----------|
| 2026-03-08 | arXiv:xxxx | 敏感内容 - 生物武器相关 |
```

### 安全优先级

**宁可误判，不可漏判** - 如果不确定是否敏感，默认跳过。

---

## Notes

_Things that annoy them, make them laugh, or important preferences will be added here over time._

---

## Session History

- **2026-03-06:** Major workspace reorganization - implemented numeric folder system
- **2026-03-05:** Memory distillation and knowledge graph work
- **2026-03-04:** AI Research OS setup and medium-watcher configuration

---

_The more I learn, the better I can help. Building this over time._

---

## 馃敊 Backlinks

**Documents linking here:**
- [[link-recommendations]] - link-recommendations
- [[README]] - README
- [[15-docs\LINK_INDEX]] - LINK_INDEX
- [[90-archive\知识库索引]] - 知识库索引

