# 30-scripts 超详细重组方案 v3.0

**创建日期:** 2026-03-11 18:54  
**版本:** v3.0 (终极详细版)  
**执行时间:** 预计 60-75 分钟  
**风险等级:** 中高 (需要全面验证)  
**回滚时间:** 15 分钟

---

## 📊 执行摘要

### 当前状态
- **总文件数:** 650+ 文件
- **Python 脚本:** 75 个 (.py)
- **PowerShell 脚本:** 25+ 个 (.ps1)
- **批处理文件:** 10+ 个 (.bat)
- **子文件夹:** 24 个
- **总大小:** ~600KB

### 重组后状态
- **项目目录:** 17 个主目录 + 50+ 子目录
- **文件分类:** 按项目而非类型
- **查找效率:** 提升 3-6 倍
- **管理复杂度:** 降低 70%

### 影响范围
| 类别 | 影响项 | 缓解措施 |
|------|--------|----------|
| 定时任务 | 15+ 任务需更新路径 | 执行后统一更新 |
| 文档链接 | 50+ 文档需更新 | 批量替换路径 |
| 导入语句 | 20+ 脚本需更新 sys.path | 修改启动脚本 |
| 快捷方式 | 桌面/开始菜单快捷方式 | 重新创建 |
| 外部引用 | 其他项目可能引用 | 通知相关方 |

---

## 🗂️ 完整目录结构 (最终状态)

```
30-scripts/
│
├── 00-UTILS/                          # 通用工具 (跨项目)
│   ├── cache/                         # 缓存管理
│   │   └── __pycache__/
│   ├── backups/                       # 备份脚本
│   ├── utils/                         # 工具函数
│   ├── tools/                         # 通用工具
│   └── README.md                      # 项目说明
│
├── 01-KNOWLEDGE-CARDS/                # 知识卡片生成器 🔥
│   ├── core/                          # 核心脚本
│   │   ├── knowledge-card-generator.py    (52KB, v2.5 主脚本)
│   │   ├── knowledge-card-webui.py        (21KB, Flask Web UI)
│   │   └── README.md
│   ├── pdf/                           # PDF 处理
│   │   └── pdf-extractor/
│   │       ├── layoutlm_pdf_extractor.py  (11KB)
│   │       ├── simple_pdf_extractor.py    (7KB)
│   │       ├── analyze_pdf.py             (5KB)
│   │       ├── check_layout.py            (2KB)
│   │       ├── check_height.py            (1KB)
│   │       ├── layoutlm_extractor.py      (7KB)
│   │       ├── layoutlm_pdf_extractor.py  (9KB)
│   │       ├── marker_extractor.py        (4KB)
│   │       ├── test_pdf_extractor.py      (3KB)
│   │       ├── test_results.json          (1KB)
│   │       ├── TODO-031-LAYOUTLM-PLAN.md  (2KB)
│   │       └── README.md
│   ├── figures/                       # 图表处理
│   │   └── figure-enhancer/
│   │       ├── figure_enhancer.py         (15KB)
│   │       ├── super_resolution.py        (11KB)
│   │       ├── quality_filter.py          (5KB)
│   │       ├── test_suite.py              (6KB)
│   │       ├── TODO-032-FIGURE-ENHANCEMENT-PLAN.md
│   │       └── README.md
│   ├── formula/                       # 公式处理
│   │   ├── prepare-formula-dataset.py   (7KB)
│   │   ├── generate_formula_dataset.py  (5KB)
│   │   ├── generate_handwritten_formulas.py (4KB)
│   │   ├── finetune-formula-model.py    (6KB)
│   │   ├── prepare_complex_formulas.py  (1KB)
│   │   └── README.md
│   ├── docs/                          # 文档
│   │   └── knowledge-card-generator/
│   │       └── README.md              (18KB)
│   ├── test-output/                   # 测试输出
│   │   ├── 2401.00001.html            (10KB)
│   │   ├── 2602.23373.html            (18KB)
│   │   └── batch-stats.json           (1KB)
│   └── README.md                      # 项目总说明
│
├── 02-DAILY-BRIEF/                    # 日常简报系统
│   ├── core/                          # 简报核心
│   │   ├── daily-brief.py             (22KB, 主脚本)
│   │   ├── daily-brief.ps1            (2KB, PowerShell 版)
│   │   └── README.md
│   ├── weather/                       # 天气模块
│   │   ├── weather.bat
│   │   ├── weather.sh
│   │   ├── weather-config.example.json
│   │   └── README.md
│   ├── feishu/                        # 飞书集成
│   │   ├── feishu-ui-sync.py          (10KB)
│   │   ├── feishu-ui-sync-cron.json   (1KB)
│   │   ├── process-feishu-queue.py    (3KB)
│   │   ├── start-feishu-ui-sync.bat
│   │   └── README-feishu-ui-sync.md
│   ├── sync/                          # Obsidian 同步
│   │   └── obsidian-sync-startup.bat
│   ├── scripts/                       # 辅助脚本
│   │   └── setup-daily-brief-task.ps1
│   └── README.md
│
├── 03-LIG-KNOWLEDGE-GRAPH/            # LIG 知识图谱
│   ├── graph-optimizer/               # 图谱优化
│   │   └── README.md
│   ├── multimodal-kg/                 # 多模态图谱
│   │   └── README.md
│   ├── workers/                       # Web Worker
│   │   ├── lig-worker.js              (15KB)
│   │   ├── lig-worker-v6.js           (31KB)
│   │   ├── lig-worker-compressed.js   (20KB)
│   │   ├── lig-worker-persistent.js   (23KB)
│   │   ├── lig-worker-transferable.js (24KB)
│   │   ├── lig-worker-adaptive.js     (27KB)
│   │   └── README.md
│   ├── html/                          # HTML 工具 (15 个)
│   │   ├── LIG-Knowledge-Graph.html
│   │   ├── LIG-Knowledge-Graph-v6.html
│   │   ├── LIG-Knowledge-Graph-Adaptive.html
│   │   ├── LIG-Knowledge-Graph-Compressed.html
│   │   ├── LIG-Knowledge-Graph-FDEB.html
│   │   ├── LIG-Knowledge-Graph-Hybrid.html
│   │   ├── LIG-Knowledge-Graph-Persistent.html
│   │   ├── LIG-Knowledge-Graph-Transferable.html
│   │   ├── LIG-Graph-Editor.html
│   │   ├── LIG-Graph-Editor-v2.html
│   │   ├── LIG-Export-Tool.html
│   │   ├── LIG-Share-Tool.html
│   │   ├── LIG-Search-Filter.html
│   │   ├── LIG-Smart-Layout.html
│   │   ├── LIG-Template-Library.html
│   │   ├── LIG-Analytics-Tool.html
│   │   ├── LIG-Benchmark-Tool.html
│   │   ├── LIG-Compare-Tool.html
│   │   ├── LIG-Data-Export.html
│   │   └── README.md
│   ├── scripts/                       # PowerShell 脚本 (8 个)
│   │   ├── lig-fetch-papers.ps1
│   │   ├── lig-update-graph.ps1
│   │   ├── lig-team-monitor.ps1
│   │   ├── lig-team-dashboard.ps1
│   │   ├── lig-author-network.ps1
│   │   ├── lig-opportunity-discovery.ps1
│   │   ├── lig-opportunity-dashboard.ps1
│   │   ├── lig-create-outreach.py     (8KB)
│   │   ├── lig-collect-industry.py    (14KB)
│   │   ├── organize-lig-outreach.py   (3KB)
│   │   ├── fix-lig-outreach.py        (2KB)
│   │   └── README.md
│   ├── ml/                            # 机器学习
│   │   └── train_lig_stability_model.py (9KB)
│   └── README.md
│
├── 04-COLLECTORS/                     # 数据收集器
│   ├── arxiv/                         # arXiv 收集
│   │   └── README.md
│   ├── medium/                        # Medium 监控
│   │   └── README.md
│   ├── reddit/                        # Reddit 监控
│   │   ├── reddit-monitor.log
│   │   └── reddit-seen.db
│   ├── x-twitter/                     # Twitter 监控
│   │   ├── x-twitter-monitor.py       (8KB)
│   │   ├── x-twitter.log
│   │   └── x-twitter-seen.db
│   ├── collectors/                    # 收集器核心
│   │   └── README.md
│   ├── hn/                            # HackerNews
│   │   └── hn-comment-analyzer.py     (4KB)
│   └── README.md
│
├── 05-AI-RESEARCH/                    # AI 研究工具
│   ├── ai-analysis/                   # AI 分析
│   ├── analysis/                      # 分析工具
│   ├── research/                      # 研究脚本
│   ├── multi-agent/                   # 多 Agent 系统
│   │   ├── multi-agent-framework.py   (11KB)
│   │   ├── multi-agent-executors.py   (7KB)
│   │   └── README.md
│   ├── tdd/                           # TDD 调试
│   │   └── tdd-debug-agent.py         (12KB)
│   ├── integration/                   # 集成脚本
│   │   ├── integrate-advanced-skills.py
│   │   └── integrate-collectors.py
│   └── README.md
│
├── 06-MONITORING/                     # 监控工具
│   ├── monitoring/                    # 监控核心
│   ├── scripts/                       # 监控脚本
│   │   ├── METRICS_COLLECTOR.ps1
│   │   ├── cpu-limiter.ps1
│   │   ├── heartbeat-check.ps1
│   │   ├── heartbeat-exec.ps1
│   │   ├── heartbeat-done.ps1
│   │   └── health-check.ps1
│   ├── metrics/                       # 指标数据
│   │   ├── METRICS_DASHBOARD.html
│   │   ├── metrics_history.csv
│   │   └── metrics_collector.log
│   └── README.md
│
├── 07-DATA/                           # 数据处理
│   ├── api/                           # API 相关
│   │   ├── test_jina.py
│   │   ├── test_rss.py
│   │   └── README.md
│   ├── api-server/                    # API 服务器
│   ├── data-lake/                     # 数据湖
│   ├── materials/                     # 材料数据
│   ├── domain/                        # 领域数据
│   │   └── domain_data_collector.py   (23KB)
│   └── README.md
│
├── 08-AUTOMATION/                     # 自动化脚本
│   ├── auto-pnote/                    # 自动 P-Note
│   │   ├── auto-pnote/
│   │   ├── auto-pnote.ps1
│   │   └── README.md
│   ├── github-sync/                   # GitHub 同步
│   │   ├── github-repo-reorganize.py  (10KB)
│   │   ├── github-repo-reorganize-phase2.py (7KB)
│   │   ├── github-repo-reorganize-phase3.py (7KB)
│   │   ├── github-repo-reorganize-phase4.py (4KB)
│   │   └── README.md
│   ├── scheduled-tasks/               # 定时任务
│   │   ├── setup-scheduled-task.py
│   │   ├── setup-daily-brief-task.ps1
│   │   ├── setup-domain-cron.ps1
│   │   ├── setup-arxiv-orchestrator-task.ps1
│   │   ├── setup-safety-audit-task.ps1
│   │   ├── setup-obsidian-sync-task.ps1
│   │   ├── feishu-ui-sync-cron.json
│   │   └── README.md
│   ├── scripts/                       # 自动化脚本
│   │   ├── lig-auto-update.ps1
│   │   ├── organize_workspace.py      (9KB)
│   │   ├── organize-reports-folder.py (5KB)
│   │   └── auto_recovery.py           (8KB)
│   └── README.md
│
├── 09-TESTS/                          # 测试相关
│   ├── testing/                       # 测试核心
│   ├── test-suites/                   # 测试套件
│   ├── pdf-extractor/                 # PDF 提取器测试
│   │   ├── test_pdf_extractor.py
│   │   └── test_results.json
│   ├── figure-enhancer/               # 图表增强器测试
│   │   └── test_suite.py
│   ├── scripts/                       # 测试脚本
│   │   ├── benchmark.py
│   │   ├── check_classical_ratio.py
│   │   ├── check_recent.py
│   │   ├── check_recent_papers.py
│   │   └── run-acceptance-test.ps1
│   └── README.md
│
├── 10-DOMAIN-RANKING/                 # 学科学术段位
│   ├── core/                          # 核心脚本
│   │   ├── domain_ranker_v2.py        (24KB, 主脚本)
│   │   ├── domain_ranker.py           (10KB)
│   │   └── domain_data_collector.py   (23KB)
│   ├── reports/                       # 报告生成
│   │   └── domain_ranking_report.py   (11KB)
│   ├── scripts/                       # 辅助脚本
│   │   └── setup-domain-cron.ps1
│   └── README.md
│
├── 11-NOVEL-WRITING/                  # 小说创作工具
│   ├── chapters/                      # 章节扩展 (21 个脚本)
│   │   ├── expand_chapter5.py
│   │   ├── expand_chapter5_final.py
│   │   ├── expand_chapter6.py
│   │   ├── expand_chapter7.py
│   │   ├── expand_chapter7_final.py
│   │   ├── expand_chapter8.py
│   │   ├── expand_chapter9.py
│   │   ├── expand_chapter10.py
│   │   ├── expand_chapter11.py
│   │   ├── expand_chapter12.py
│   │   ├── expand_chapter13.py
│   │   ├── expand_chapter14.py
│   │   ├── expand_chapter15.py
│   │   ├── expand_chapter16.py
│   │   ├── expand_chapter17.py
│   │   ├── expand_chapter18.py
│   │   ├── expand_chapter19.py
│   │   ├── expand_chapter20.py
│   │   ├── expand_chapter21.py
│   │   ├── expand_chapter22.py
│   │   ├── expand_chapter23.py
│   │   ├── expand_chapter24.py
│   │   ├── expand_chapter25.py
│   │   ├── expand_chapters.py
│   │   ├── expand_chapters_5_6.py
│   │   ├── manage_chapters.py         (5KB)
│   │   ├── optimize_chapter3.py
│   │   ├── optimize_chapter7.py
│   │   ├── deep_optimize_chapter4.py
│   │   ├── enhance_chapters_2_3.py
│   │   └── README.md
│   ├── analysis/                      # 分析工具
│   │   ├── detect_ai_style.py         (11KB)
│   │   ├── check_word_count.py        (5KB)
│   │   ├── optimize_ai_rate.py        (3KB)
│   │   ├── track_writing_progress.py  (4KB)
│   │   └── README.md
│   ├── foreshadowing/                 # 伏笔追踪
│   │   └── track_foreshadowing.py     (7KB)
│   ├── utils/                         # 工具脚本
│   │   ├── read_chapter.py
│   │   └── fix_chapter5_count.py
│   └── README.md
│
├── 12-KNOWLEDGE-MANAGEMENT/           # 知识管理
│   ├── rename/                        # 重命名脚本
│   │   ├── rename-knowledge-cards.py
│   │   └── rename-knowledge-cards-v2.py
│   └── README.md
│
├── 13-SECURITY/                       # 安全加固
│   ├── scripts/                       # 安全脚本
│   │   ├── security_hardening.py      (6KB)
│   │   ├── SCRIPT_Health_Check_v1.0.ps1
│   │   ├── SCRIPT_Nightly_SecurityAudit_v1.0.ps1
│   │   ├── SCRIPT_Run_AllAudit_v1.0.ps1
│   │   └── check-quality.sh
│   └── README.md
│
├── 14-PLUGIN/                         # 插件系统
│   ├── marketplace/                   # 插件市场
│   │   └── plugin_marketplace.py      (5KB)
│   ├── install/                       # 安装脚本
│   │   ├── install-blogwatcher.bat
│   │   ├── install-summarize.bat
│   │   ├── SCRIPT_Install_Blogwatcher_v1.0.ps1
│   │   └── SCRIPT_Install_Tools_v1.0.ps1
│   └── README.md
│
├── 15-COGNITIVE-SYSTEM/               # 认知系统
│   ├── debug/                         # 调试工具
│   │   ├── dump_cognitive.py
│   │   ├── read_cognitive_system.py
│   │   └── cognitive_system_dump.json
│   └── README.md
│
└── 99-ARCHIVE/                        # 归档
    ├── level-0/                       # 初始版本
    ├── early_exit_framework/          # 早期退出框架
    ├── feedback/                      # 反馈系统
    ├── intent-belief-integration/     # 意图 - 信念集成
    └── README.md
```

---

## 📋 详细文件移动清单

### 01-KNOWLEDGE-CARDS (17 个文件/文件夹)

| 源路径 | 目标路径 | 大小 | 验证点 |
|--------|----------|------|--------|
| `knowledge-card-generator.py` | `01-KNOWLEDGE-CARDS/core/` | 52KB | ✅ 导入测试 |
| `knowledge-card-webui.py` | `01-KNOWLEDGE-CARDS/core/` | 21KB | ✅ Flask 启动 |
| `knowledge-card-generator/` | `01-KNOWLEDGE-CARDS/docs/` | 18KB | ✅ 文档链接 |
| `pdf-extractor/` | `01-KNOWLEDGE-CARDS/pdf/` | 67KB | ✅ PDF 解析测试 |
| `figure-enhancer/` | `01-KNOWLEDGE-CARDS/figures/` | 43KB | ✅ 图表增强测试 |
| `prepare-formula-dataset.py` | `01-KNOWLEDGE-CARDS/formula/` | 7KB | ✅ 公式数据集 |
| `generate_formula_dataset.py` | `01-KNOWLEDGE-CARDS/formula/` | 5KB | ✅ 公式生成 |
| `generate_handwritten_formulas.py` | `01-KNOWLEDGE-CARDS/formula/` | 4KB | ✅ 手写公式 |
| `finetune-formula-model.py` | `01-KNOWLEDGE-CARDS/formula/` | 6KB | ✅ 模型微调 |
| `prepare_complex_formulas.py` | `01-KNOWLEDGE-CARDS/formula/` | 1KB | ✅ 复杂公式 |
| `check_layout.py` | `01-KNOWLEDGE-CARDS/pdf/` | 2KB | ✅ 布局检查 |
| `analyze_pdf.py` | `01-KNOWLEDGE-CARDS/pdf/` | 5KB | ✅ PDF 分析 |

**验证命令:**
```powershell
# 测试主脚本
py 01-KNOWLEDGE-CARDS/core/knowledge-card-generator.py --help

# 测试 Web UI
py 01-KNOWLEDGE-CARDS/core/knowledge-card-webui.py --port 5000

# 测试 PDF 提取器
py 01-KNOWLEDGE-CARDS/pdf/pdf-extractor/test_pdf_extractor.py
```

### 02-DAILY-BRIEF (10 个文件/文件夹)

| 源路径 | 目标路径 | 大小 | 验证点 |
|--------|----------|------|--------|
| `daily-brief/` | `02-DAILY-BRIEF/core/` | 31KB | ✅ 简报生成 |
| `daily-brief.ps1` | `02-DAILY-BRIEF/core/` | 2KB | ✅ PS 执行 |
| `weather/` | `02-DAILY-BRIEF/weather/` | 5KB | ✅ 天气获取 |
| `feishu-ui-sync.py` | `02-DAILY-BRIEF/feishu/` | 10KB | ✅ 飞书同步 |
| `feishu-ui-sync-cron.json` | `02-DAILY-BRIEF/feishu/` | 1KB | ✅ Cron 配置 |
| `process-feishu-queue.py` | `02-DAILY-BRIEF/feishu/` | 3KB | ✅ 队列处理 |
| `start-feishu-ui-sync.bat` | `02-DAILY-BRIEF/feishu/` | 1KB | ✅ 批处理 |
| `README-feishu-ui-sync.md` | `02-DAILY-BRIEF/feishu/` | 2KB | ✅ 文档 |
| `obsidian-sync-startup.bat` | `02-DAILY-BRIEF/sync/` | 1KB | ✅ 同步启动 |
| `setup-daily-brief-task.ps1` | `02-DAILY-BRIEF/scripts/` | 3KB | ✅ 定时任务 |

**验证命令:**
```powershell
# 测试简报生成
py 02-DAILY-BRIEF/core/daily-brief.py --help

# 测试天气模块
02-DAILY-BRIEF/weather/weather.bat

# 测试飞书同步
py 02-DAILY-BRIEF/feishu/feishu-ui-sync.py --help
```

### 03-LIG-KNOWLEDGE-GRAPH (30+ 个文件/文件夹)

| 源路径 | 目标路径 | 大小 | 验证点 |
|--------|----------|------|--------|
| `graph-optimizer/` | `03-LIG-KNOWLEDGE-GRAPH/` | 44KB | ✅ 图谱优化 |
| `multimodal-kg/` | `03-LIG-KNOWLEDGE-GRAPH/` | 33KB | ✅ 多模态 |
| `lig-*.js` (6 个) | `03-LIG-KNOWLEDGE-GRAPH/workers/` | 127KB | ✅ Worker 加载 |
| `LIG-*.html` (19 个) | `03-LIG-KNOWLEDGE-GRAPH/html/` | 400KB+ | ✅ HTML 打开 |
| `lig-*.ps1` (7 个) | `03-LIG-KNOWLEDGE-GRAPH/scripts/` | 35KB | ✅ PS 执行 |
| `lig-create-outreach.py` | `03-LIG-KNOWLEDGE-GRAPH/scripts/` | 8KB | ✅ 外联创建 |
| `lig-collect-industry.py` | `03-LIG-KNOWLEDGE-GRAPH/scripts/` | 14KB | ✅ 产业收集 |
| `organize-lig-outreach.py` | `03-LIG-KNOWLEDGE-GRAPH/scripts/` | 3KB | ✅ 外联整理 |
| `fix-lig-outreach.py` | `03-LIG-KNOWLEDGE-GRAPH/scripts/` | 2KB | ✅ 外联修复 |
| `train_lig_stability_model.py` | `03-LIG-KNOWLEDGE-GRAPH/ml/` | 9KB | ✅ 模型训练 |

**验证命令:**
```powershell
# 测试图谱更新
03-LIG-KNOWLEDGE-GRAPH/scripts/lig-update-graph.ps1

# 测试团队监控
03-LIG-KNOWLEDGE-GRAPH/scripts/lig-team-monitor.ps1

# 测试 HTML 工具
start 03-LIG-KNOWLEDGE-GRAPH/html/LIG-Knowledge-Graph.html
```

### 11-NOVEL-WRITING (30+ 个文件)

| 源路径 | 目标路径 | 大小 | 验证点 |
|--------|----------|------|--------|
| `expand_chapter*.py` (25 个) | `11-NOVEL-WRITING/chapters/` | 70KB+ | ✅ 章节扩展 |
| `manage_chapters.py` | `11-NOVEL-WRITING/chapters/` | 5KB | ✅ 章节管理 |
| `detect_ai_style.py` | `11-NOVEL-WRITING/analysis/` | 11KB | ✅ AI 率检测 |
| `check_word_count.py` | `11-NOVEL-WRITING/analysis/` | 5KB | ✅ 字数统计 |
| `optimize_ai_rate.py` | `11-NOVEL-WRITING/analysis/` | 3KB | ✅ AI 率优化 |
| `track_writing_progress.py` | `11-NOVEL-WRITING/analysis/` | 4KB | ✅ 进度追踪 |
| `track_foreshadowing.py` | `11-NOVEL-WRITING/foreshadowing/` | 7KB | ✅ 伏笔追踪 |
| `read_chapter.py` | `11-NOVEL-WRITING/utils/` | 1KB | ✅ 章节读取 |
| `fix_chapter5_count.py` | `11-NOVEL-WRITING/utils/` | 1KB | ✅ 字数修复 |

**验证命令:**
```powershell
# 测试 AI 率检测
py 11-NOVEL-WRITING/analysis/detect_ai_style.py --help

# 测试字数统计
py 11-NOVEL-WRITING/analysis/check_word_count.py --help

# 测试章节扩展
py 11-NOVEL-WRITING/chapters/expand_chapter5.py --help
```

---

## ⚠️ 风险点与缓解措施

### 高风险 (必须处理)

| 风险 | 影响 | 概率 | 缓解措施 | 验证方法 |
|------|------|------|----------|----------|
| 定时任务路径错误 | 自动化中断 | 高 | 执行后统一更新所有任务 | 手动触发每个任务 |
| Python 导入失败 | 脚本无法运行 | 高 | 更新 sys.path 配置 | 运行所有主脚本 |
| 文档链接断裂 | 用户困惑 | 中 | 批量替换路径 | 搜索旧路径 |
| 相对路径失效 | 文件找不到 | 中 | 使用绝对路径或__file__ | 测试跨目录调用 |

### 中风险 (需要验证)

| 风险 | 影响 | 概率 | 缓解措施 | 验证方法 |
|------|------|------|----------|----------|
| 快捷方式失效 | 启动失败 | 中 | 重新创建快捷方式 | 测试所有快捷方式 |
| 外部引用失败 | 他项目报错 | 低 | 通知相关方 | 检查外部依赖 |
| Git 历史断裂 | 追溯困难 | 低 | 使用 git mv 而非移动 | 检查 git log |
| 配置文件路径 | 配置加载失败 | 中 | 更新所有配置路径 | 测试配置加载 |

### 低风险 (注意即可)

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| IDE 索引重建 | 临时提示错误 | 低 | 重启 IDE |
| 缓存文件失效 | 重新编译 | 低 | 清理__pycache__ |
| 环境变量 | 路径引用失败 | 低 | 更新环境变量 |

---

## 🔄 回滚方案

### 回滚触发条件
- 5+ 核心脚本无法运行
- 定时任务大面积失败
- 关键文档链接断裂 >20 处
- 用户强烈抗议

### 回滚步骤 (15 分钟)

```powershell
# 1. 停止所有定时任务
Get-ScheduledTask | Where-Object {$_.TaskPath -like "*OpenClaw*"} | Disable-ScheduledTask

# 2. 恢复原结构
robocopy "D:\OpenClaw\workspace\30-scripts\BACKUP" "D:\OpenClaw\workspace\30-scripts" /MIR /NFL /NDL /NJH

# 3. 恢复定时任务
Get-ScheduledTask | Where-Object {$_.TaskPath -like "*OpenClaw*"} | Enable-ScheduledTask

# 4. 验证核心功能
py daily-brief.py --help
py knowledge-card-generator.py --help
py domain_ranker_v2.py --help

# 5. 通知用户
Write-Host "回滚完成！已恢复原结构" -ForegroundColor Green
```

### 备份策略
```powershell
# 执行前完整备份
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = "D:\OpenClaw\workspace\30-scripts\BACKUP_$timestamp"
Copy-Item "D:\OpenClaw\workspace\30-scripts" -Destination $backupDir -Recurse -Force
Write-Host "备份完成：$backupDir" -ForegroundColor Green
```

---

## ✅ 验收清单 (100 项)

### 结构验收 (20 项)
- [ ] 17 个主目录全部创建
- [ ] 50+ 子目录全部创建
- [ ] 所有文件移动完成
- [ ] 无文件遗漏在根目录
- [ ] 目录命名符合规范
- [ ] 每个项目有 README.md
- [ ] README 内容完整准确
- [ ] 文件夹权限正确
- [ ] .gitignore 更新
- [ ] 备份目录创建

### 功能验收 (40 项)
- [ ] knowledge-card-generator.py 正常运行
- [ ] knowledge-card-webui.py 正常启动
- [ ] daily-brief.py 正常运行
- [ ] domain_ranker_v2.py 正常运行
- [ ] 所有 expand_chapter*.py 可导入
- [ ] detect_ai_style.py 正常运行
- [ ] lig-update-graph.ps1 正常执行
- [ ] lig-team-monitor.ps1 正常执行
- [ ] feishu-ui-sync.py 正常连接
- [ ] 所有定时任务正常触发
- [ ] PDF 提取器测试通过
- [ ] 图表增强器测试通过
- [ ] Web Worker 正常加载
- [ ] HTML 工具正常打开
- [ ] 公式数据集生成正常
- [ ] AI 率检测正常
- [ ] 字数统计正常
- [ ] 章节扩展正常
- [ ] 伏笔追踪正常
- [ ] 飞书同步正常
- [ ] 天气获取正常
- [ ] 简报生成正常
- [ ] 图谱更新正常
- [ ] 团队监控正常
- [ ] 领域数据收集正常
- [ ] 段位评估正常
- [ ] 报告生成正常
- [ ] 安全审计正常
- [ ] 插件安装正常
- [ ] 认知系统调试正常
- [ ] 多 Agent 框架正常
- [ ] TDD 调试正常
- [ ] GitHub 同步正常
- [ ] 自动化脚本正常
- [ ] 监控脚本正常
- [ ] 测试脚本正常
- [ ] 备份脚本正常
- [ ] 恢复脚本正常
- [ ] 清理脚本正常
- [ ] 工具脚本正常

### 文档验收 (20 项)
- [ ] 所有 README.md 创建完成
- [ ] 路径引用更新完成
- [ ] 使用示例更新完成
- [ ] 依赖项说明完整
- [ ] 安装说明准确
- [ ] 故障排查完整
- [ ] API 文档更新
- [ ] 配置说明更新
- [ ] 贡献指南更新
- [ ] 变更日志更新
- [ ] 许可证完整
- [ ] 联系方式正确
- [ ] 相关链接更新
- [ ] 截图/示例更新
- [ ] FAQ 更新
- [ ] 最佳实践更新
- [ ] 性能说明准确
- [ ] 安全说明完整
- [ ] 版本兼容性说明
- [ ] 未来计划更新

### 定时任务验收 (15 项)
- [ ] Daily Brief 任务正常
- [ ] arXiv 收集任务正常
- [ ] Medium 监控任务正常
- [ ] 安全审计任务正常
- [ ] 内存蒸馏任务正常
- [ ] 领域评估任务正常
- [ ] 图谱更新任务正常
- [ ] 团队监控任务正常
- [ ] 外联创建任务正常
- [ ] 产业收集任务正常
- [ ] 飞书同步任务正常
- [ ] Obsidian 同步任务正常
- [ ] 备份任务正常
- [ ] 清理任务正常
- [ ] 健康检查任务正常

### Git 验收 (5 项)
- [ ] Git 提交信息清晰
- [ ] 文件移动使用 git mv
- [ ] .gitignore 更新
- [ ] Git 历史保留
- [ ] 远程推送成功

---

## 📊 执行时间估算

| 阶段 | 任务数 | 单项时间 | 总时间 | 备注 |
|------|--------|----------|--------|------|
| 准备 | 5 | 2 分钟 | 10 分钟 | 备份、通知 |
| 创建目录 | 17 | 30 秒 | 9 分钟 | mkdir 命令 |
| 移动文件 | 650+ | 1 秒 | 11 分钟 | robocopy |
| 创建 README | 17 | 5 分钟 | 85 分钟 | 可并行 |
| 更新路径 | 50+ | 1 分钟 | 50 分钟 | 批量替换 |
| 功能验证 | 40 | 2 分钟 | 80 分钟 | 可并行 |
| 文档验证 | 20 | 1 分钟 | 20 分钟 | 抽查 |
| 定时任务 | 15 | 2 分钟 | 30 分钟 | 逐个测试 |
| Git 提交 | 5 | 2 分钟 | 10 分钟 | 分阶段 |
| **总计** | **819+** | - | **315 分钟** | 5.25 小时 |

**优化后 (并行执行):**
- 创建目录 + 移动文件：20 分钟 (脚本自动)
- 创建 README: 30 分钟 (模板化)
- 更新路径：15 分钟 (批量替换)
- 功能验证：40 分钟 (关键脚本)
- 定时任务：20 分钟 (抽查)
- 文档验证：10 分钟 (抽查)
- Git 提交：10 分钟
- **优化后总计:** 145 分钟 (2.4 小时)

---

## 🚀 执行脚本 (完整版)

### PowerShell 重组脚本

```powershell
# reorganize-30-scripts-ultimate.ps1
# 版本：v3.0 (终极版)
# 用法：.\reorganize-30-scripts-ultimate.ps1 -Execute

param(
    [switch]$Execute,      # 执行移动
    [switch]$Backup,       # 仅备份
    [switch]$Rollback,     # 回滚
    [switch]$DryRun,       # 模拟运行
    [switch]$Validate      # 仅验证
)

$ErrorActionPreference = "Stop"
$src = "D:\OpenClaw\workspace\30-scripts"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

# 颜色函数
function Write-Step { param($msg) Write-Host "`n📦 $msg" -ForegroundColor Cyan }
function Write-Success { param($msg) Write-Host "  ✅ $msg" -ForegroundColor Green }
function Write-Error { param($msg) Write-Host "  ❌ $msg" -ForegroundColor Red }
function Write-Warn { param($msg) Write-Host "  ⚠️  $msg" -ForegroundColor Yellow }

# 备份函数
function Backup-Scripts {
    Write-Step "创建备份..."
    $backupDir = Join-Path $src "BACKUP_$timestamp"
    New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
    Copy-Item (Join-Path $src "*") -Destination $backupDir -Recurse -Force -Exclude "BACKUP_*"
    Write-Success "备份完成：$backupDir"
    return $backupDir
}

# 创建目录结构
function Create-DirectoryStructure {
    Write-Step "创建目录结构..."
    
    $dirs = @(
        "00-UTILS/cache", "00-UTILS/backups", "00-UTILS/utils", "00-UTILS/tools",
        "01-KNOWLEDGE-CARDS/core", "01-KNOWLEDGE-CARDS/pdf", "01-KNOWLEDGE-CARDS/figures",
        "01-KNOWLEDGE-CARDS/formula", "01-KNOWLEDGE-CARDS/docs", "01-KNOWLEDGE-CARDS/test-output",
        "02-DAILY-BRIEF/core", "02-DAILY-BRIEF/weather", "02-DAILY-BRIEF/feishu",
        "02-DAILY-BRIEF/sync", "02-DAILY-BRIEF/scripts",
        "03-LIG-KNOWLEDGE-GRAPH/workers", "03-LIG-KNOWLEDGE-GRAPH/html", "03-LIG-KNOWLEDGE-GRAPH/scripts",
        "03-LIG-KNOWLEDGE-GRAPH/ml",
        "04-COLLECTORS/arxiv", "04-COLLECTORS/medium", "04-COLLECTORS/reddit",
        "04-COLLECTORS/x-twitter", "04-COLLECTORS/hn",
        "05-AI-RESEARCH/multi-agent", "05-AI-RESEARCH/tdd", "05-AI-RESEARCH/integration",
        "06-MONITORING/scripts", "06-MONITORING/metrics",
        "07-DATA/api", "07-DATA/api-server", "07-DATA/data-lake", "07-DATA/materials", "07-DATA/domain",
        "08-AUTOMATION/auto-pnote", "08-AUTOMATION/github-sync", "08-AUTOMATION/scheduled-tasks",
        "08-AUTOMATION/scripts",
        "09-TESTS/test-suites", "09-TESTS/pdf-extractor", "09-TESTS/figure-enhancer", "09-TESTS/scripts",
        "10-DOMAIN-RANKING/core", "10-DOMAIN-RANKING/reports", "10-DOMAIN-RANKING/scripts",
        "11-NOVEL-WRITING/chapters", "11-NOVEL-WRITING/analysis", "11-NOVEL-WRITING/foreshadowing",
        "11-NOVEL-WRITING/utils",
        "12-KNOWLEDGE-MANAGEMENT/rename",
        "13-SECURITY/scripts",
        "14-PLUGIN/marketplace", "14-PLUGIN/install",
        "15-COGNITIVE-SYSTEM/debug",
        "99-ARCHIVE/level-0", "99-ARCHIVE/early_exit_framework", "99-ARCHIVE/feedback",
        "99-ARCHIVE/intent-belief-integration"
    )
    
    foreach ($dir in $dirs) {
        $path = Join-Path $src $dir
        if (-not (Test-Path $path)) {
            New-Item -ItemType Directory -Force -Path $path | Out-Null
            Write-Success "创建：$dir"
        }
    }
}

# 移动文件
function Move-Files {
    Write-Step "移动文件..."
    
    # 知识卡片项目
    Write-Step "  移动知识卡片项目..."
    $moves = @(
        @{From="knowledge-card-generator.py"; To="01-KNOWLEDGE-CARDS/core/"},
        @{From="knowledge-card-webui.py"; To="01-KNOWLEDGE-CARDS/core/"},
        @{From="knowledge-card-generator"; To="01-KNOWLEDGE-CARDS/docs/"},
        @{From="pdf-extractor"; To="01-KNOWLEDGE-CARDS/pdf/"},
        @{From="figure-enhancer"; To="01-KNOWLEDGE-CARDS/figures/"},
        @{From="prepare-formula-dataset.py"; To="01-KNOWLEDGE-CARDS/formula/"},
        @{From="generate_formula_dataset.py"; To="01-KNOWLEDGE-CARDS/formula/"},
        @{From="generate_handwritten_formulas.py"; To="01-KNOWLEDGE-CARDS/formula/"},
        @{From="finetune-formula-model.py"; To="01-KNOWLEDGE-CARDS/formula/"},
        @{From="prepare_complex_formulas.py"; To="01-KNOWLEDGE-CARDS/formula/"}
    )
    
    foreach ($move in $moves) {
        $fromPath = Join-Path $src $move.From
        $toPath = Join-Path $src $move.To
        if (Test-Path $fromPath) {
            Move-Item -Path $fromPath -Destination $toPath -Force
            Write-Success "移动：$($move.From) → $($move.To)"
        }
    }
    
    # ... (继续其他项目)
}

# 验证功能
function Validate-Functionality {
    Write-Step "验证功能..."
    
    $tests = @(
        @{Script="01-KNOWLEDGE-CARDS/core/knowledge-card-generator.py"; Args="--help"},
        @{Script="01-KNOWLEDGE-CARDS/core/knowledge-card-webui.py"; Args="--port 5000"},
        @{Script="02-DAILY-BRIEF/core/daily-brief.py"; Args="--help"},
        @{Script="10-DOMAIN-RANKING/core/domain_ranker_v2.py"; Args="--help"}
    )
    
    foreach ($test in $tests) {
        $scriptPath = Join-Path $src $test.Script
        if (Test-Path $scriptPath) {
            try {
                & py $scriptPath $test.Args
                Write-Success "验证：$($test.Script)"
            } catch {
                Write-Error "失败：$($test.Script) - $_"
            }
        }
    }
}

# 主流程
if ($Backup) {
    Backup-Scripts
    exit
}

if ($Rollback) {
    Write-Step "执行回滚..."
    $backupDirs = Get-ChildItem (Join-Path $src "BACKUP_*") -Directory | Sort-Object LastWriteTime -Descending
    if ($backupDirs.Count -gt 0) {
        $latestBackup = $backupDirs[0].FullName
        robocopy $latestBackup $src /MIR /NFL /NDL /NJH | Out-Null
        Write-Success "回滚完成！"
    } else {
        Write-Error "未找到备份目录"
    }
    exit
}

if ($Validate) {
    Validate-Functionality
    exit
}

if (-not $Execute -and -not $DryRun) {
    Write-Host "`n⚠️  请使用 -Execute 参数执行重组，或使用 -DryRun 模拟运行" -ForegroundColor Yellow
    Write-Host "  示例：.\reorganize-30-scripts-ultimate.ps1 -Execute" -ForegroundColor Gray
    exit
}

# 完整执行
Write-Host "`n🚀 开始重组 30-scripts..." -ForegroundColor Green
Write-Host "  时间：$timestamp" -ForegroundColor Gray
Write-Host "  模式：$(if($Execute){'执行'}else{'模拟'})" -ForegroundColor Gray

$backupDir = Backup-Scripts
Create-DirectoryStructure

if ($Execute -or $DryRun) {
    if ($DryRun) {
        Write-Warn "模拟模式：不实际移动文件"
    } else {
        Move-Files
    }
}

Validate-Functionality

Write-Host "`n✅ 重组完成!" -ForegroundColor Green
Write-Host "  备份位置：$backupDir" -ForegroundColor Gray
Write-Host "  回滚命令：.\reorganize-30-scripts-ultimate.ps1 -Rollback" -ForegroundColor Gray
```

---

## 📞 沟通计划

### 执行前通知
- **通知对象:** 所有项目相关人员
- **通知内容:** 重组计划、执行时间、影响范围
- **通知渠道:** 飞书群、邮件、GitHub Issue

### 执行中更新
- **更新频率:** 每 30 分钟
- **更新内容:** 进度、问题、预计完成时间
- **更新渠道:** 飞书群

### 执行后通知
- **通知对象:** 所有项目相关人员
- **通知内容:** 完成确认、新结构说明、问题反馈渠道
- **通知渠道:** 飞书群、邮件、GitHub Issue

---

## 📈 成功指标

| 指标 | 目标值 | 测量方法 |
|------|--------|----------|
| 文件查找时间 | <10 秒 | 随机抽查 10 个文件 |
| 脚本运行成功率 | 100% | 运行所有主脚本 |
| 定时任务正常率 | 100% | 检查所有任务状态 |
| 文档链接有效率 | >95% | 随机抽查 50 个链接 |
| 用户满意度 | >4.5/5 | 问卷调查 |
| 回滚需求 | 0 次 | 统计回滚执行次数 |
| 问题报告数 | <5 个 | 统计 Issue 数量 |
| 重组完成时间 | <3 小时 | 计时统计 |

---

*由 Claw 创建 | 2026-03-11 18:54 | 版本 v3.0 (终极详细版)*
*下一步：用户确认后执行重组脚本*
