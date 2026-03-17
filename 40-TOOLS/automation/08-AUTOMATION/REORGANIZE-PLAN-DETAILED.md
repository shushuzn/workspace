# 30-scripts 详细重组方案

**创建日期:** 2026-03-11 18:52  
**版本:** v2.0 (详细版)  
**执行时间:** 预计 45 分钟

---

## 📊 当前文件统计

| 类别 | 文件数 | 文件夹数 | 总大小 |
|------|--------|----------|--------|
| Python 脚本 | 75 | - | ~350KB |
| PowerShell | 20+ | - | ~50KB |
| 子文件夹 | - | 24 | ~200KB |
| **总计** | **95+** | **24** | **~600KB** |

---

## 🗂️ 新目录结构详解

### 00-UTILS/ (通用工具)
**用途:** 跨项目通用工具、缓存、备份

```
00-UTILS/
├── cache/                    # 缓存管理
│   └── __pycache__/
├── backups/                  # 备份脚本
├── utils/                    # 工具函数
├── tools/                    # 通用工具
└── README.md
```

**移动文件:**
- `cache/` → `00-UTILS/cache/`
- `backups/` → `00-UTILS/backups/`
- `utils/` → `00-UTILS/utils/`
- `tools/` → `00-UTILS/tools/`

---

### 01-KNOWLEDGE-CARDS/ (知识卡片生成器) 🔥
**用途:** PDF→HTML 知识卡片生成，含 Web UI

```
01-KNOWLEDGE-CARDS/
├── core/                     # 核心脚本
│   ├── knowledge-card-generator.py    (52KB, 主脚本)
│   ├── knowledge-card-webui.py        (21KB, Web 界面)
│   └── README.md
├── pdf/                      # PDF 处理
│   └── pdf-extractor/
│       ├── layoutlm_pdf_extractor.py
│       ├── simple_pdf_extractor.py
│       └── README.md
├── figures/                  # 图表处理
│   └── figure-enhancer/
│       ├── figure_enhancer.py
│       ├── super_resolution.py
│       └── README.md
├── docs/                     # 文档
│   └── knowledge-card-generator/
│       └── README.md
├── test-output/              # 测试输出
└── README.md                 # 项目说明
```

**移动文件:**
- `knowledge-card-generator.py` → `01-KNOWLEDGE-CARDS/core/`
- `knowledge-card-webui.py` → `01-KNOWLEDGE-CARDS/core/`
- `knowledge-card-generator/` → `01-KNOWLEDGE-CARDS/docs/`
- `pdf-extractor/` → `01-KNOWLEDGE-CARDS/pdf/`
- `figure-enhancer/` → `01-KNOWLEDGE-CARDS/figures/`
- `check_layout.py` → `01-KNOWLEDGE-CARDS/pdf/`
- `analyze_pdf.py` → `01-KNOWLEDGE-CARDS/pdf/`

**相关脚本:**
- `prepare-formula-dataset.py` → `01-KNOWLEDGE-CARDS/pdf/`
- `generate_formula_dataset.py` → `01-KNOWLEDGE-CARDS/pdf/`
- `generate_handwritten_formulas.py` → `01-KNOWLEDGE-CARDS/pdf/`
- `finetune-formula-model.py` → `01-KNOWLEDGE-CARDS/pdf/`
- `prepare_complex_formulas.py` → `01-KNOWLEDGE-CARDS/pdf/`

**依赖:** PyMuPDF, Flask, tqdm, Pillow

---

### 02-DAILY-BRIEF/ (日常简报系统)
**用途:** 每日自动简报生成和推送

```
02-DAILY-BRIEF/
├── daily-brief/              # 简报核心
│   ├── daily-brief.py        (22KB)
│   └── README.md
├── weather/                  # 天气模块
│   ├── weather.bat
│   ├── weather.sh
│   └── weather-config.example.json
├── scripts/                  # 辅助脚本
│   ├── feishu-ui-sync.py     (10KB)
│   ├── process-feishu-queue.py
│   └── obsidian-sync-startup.bat
└── README.md
```

**移动文件:**
- `daily-brief/` → `02-DAILY-BRIEF/daily-brief/`
- `weather/` → `02-DAILY-BRIEF/weather/`
- `feishu-ui-sync.py` → `02-DAILY-BRIEF/scripts/`
- `process-feishu-queue.py` → `02-DAILY-BRIEF/scripts/`
- `obsidian-sync-startup.bat` → `02-DAILY-BRIEF/scripts/`
- `daily-brief.ps1` → `02-DAILY-BRIEF/`
- `daily-brief-autorun.bat` → `02-DAILY-BRIEF/`
- `setup-daily-brief-task.ps1` → `02-DAILY-BRIEF/`

**依赖:** Flask, requests

---

### 03-LIG-KNOWLEDGE-GRAPH/ (LIG 知识图谱)
**用途:** LIG 领域知识图谱可视化和分析

```
03-LIG-KNOWLEDGE-GRAPH/
├── graph-optimizer/          # 图谱优化
│   └── README.md
├── multimodal-kg/            # 多模态图谱
├── workers/                  # Web Worker
│   ├── lig-worker.js
│   ├── lig-worker-v6.js
│   ├── lig-worker-compressed.js
│   ├── lig-worker-persistent.js
│   ├── lig-worker-transferable.js
│   └── lig-worker-adaptive.js
├── html/                     # HTML 工具
│   ├── LIG-Knowledge-Graph.html
│   ├── LIG-Knowledge-Graph-v6.html
│   ├── LIG-Graph-Editor.html
│   ├── LIG-Graph-Editor-v2.html
│   ├── LIG-Export-Tool.html
│   ├── LIG-Share-Tool.html
│   └── ... (15 个 HTML 文件)
├── scripts/                  # PowerShell 脚本
│   ├── lig-fetch-papers.ps1
│   ├── lig-update-graph.ps1
│   ├── lig-team-monitor.ps1
│   ├── lig-team-dashboard.ps1
│   └── ... (8 个脚本)
└── README.md
```

**移动文件:**
- `graph-optimizer/` → `03-LIG-KNOWLEDGE-GRAPH/`
- `multimodal-kg/` → `03-LIG-KNOWLEDGE-GRAPH/`
- `lig-*.js` → `03-LIG-KNOWLEDGE-GRAPH/workers/`
- `LIG-*.html` → `03-LIG-KNOWLEDGE-GRAPH/html/`
- `lig-*.ps1` → `03-LIG-KNOWLEDGE-GRAPH/scripts/`
- `lig-collect-industry.py` → `03-LIG-KNOWLEDGE-GRAPH/scripts/`
- `lig-create-outreach.py` → `03-LIG-KNOWLEDGE-GRAPH/scripts/`
- `organize-lig-outreach.py` → `03-LIG-KNOWLEDGE-GRAPH/scripts/`
- `fix-lig-outreach.py` → `03-LIG-KNOWLEDGE-GRAPH/scripts/`
- `train_lig_stability_model.py` → `03-LIG-KNOWLEDGE-GRAPH/`

---

### 04-COLLECTORS/ (数据收集器)
**用途:** arXiv/Medium/HackerNews 自动收集

```
04-COLLECTORS/
├── collectors/               # 收集器核心
├── arxiv-daily/              # arXiv 收集
├── medium-watcher/           # Medium 监控
├── reddit/                   # Reddit 监控
│   ├── reddit-monitor.log
│   └── reddit-seen.db
├── x-twitter/                # Twitter 监控
│   ├── x-twitter-monitor.py  (8KB)
│   ├── x-twitter.log
│   └── x-twitter-seen.db
└── README.md
```

**移动文件:**
- `collectors/` → `04-COLLECTORS/`
- `reddit-monitor.log` → `04-COLLECTORS/reddit/`
- `reddit-seen.db` → `04-COLLECTORS/reddit/`
- `x-twitter-monitor.py` → `04-COLLECTORS/x-twitter/`
- `x-twitter.log` → `04-COLLECTORS/x-twitter/`
- `x-twitter-seen.db` → `04-COLLECTORS/x-twitter/`

---

### 05-AI-RESEARCH/ (AI 研究工具)
**用途:** AI 论文分析、多 Agent 框架

```
05-AI-RESEARCH/
├── ai-analysis/              # AI 分析
├── analysis/                 # 分析工具
├── research/                 # 研究脚本
├── multi-agent/              # 多 Agent 系统
│   ├── multi-agent-framework.py (11KB)
│   └── multi-agent-executors.py (7KB)
├── tdd/                      # TDD 调试
│   └── tdd-debug-agent.py    (12KB)
└── README.md
```

**移动文件:**
- `ai-analysis/` → `05-AI-RESEARCH/`
- `analysis/` → `05-AI-RESEARCH/`
- `research/` → `05-AI-RESEARCH/`
- `multi-agent-framework.py` → `05-AI-RESEARCH/multi-agent/`
- `multi-agent-executors.py` → `05-AI-RESEARCH/multi-agent/`
- `tdd-debug-agent.py` → `05-AI-RESEARCH/tdd/`
- `integrate-advanced-skills.py` → `05-AI-RESEARCH/`
- `integrate-collectors.py` → `05-AI-RESEARCH/`
- `hn-comment-analyzer.py` → `05-AI-RESEARCH/`

---

### 06-MONITORING/ (监控工具)
**用途:** 系统监控、CPU 限制、健康检查

```
06-MONITORING/
├── monitoring/               # 监控核心
├── scripts/                  # 监控脚本
│   ├── METRICS_COLLECTOR.ps1
│   ├── cpu-limiter.ps1
│   ├── heartbeat-check.ps1
│   └── health-check.ps1
└── README.md
```

**移动文件:**
- `monitoring/` → `06-MONITORING/`
- `METRICS_COLLECTOR.ps1` → `06-MONITORING/scripts/`
- `METRICS_DASHBOARD.html` → `06-MONITORING/`
- `metrics_history.csv` → `06-MONITORING/`
- `metrics_collector.log` → `06-MONITORING/`
- `cpu-limiter.ps1` (在 SCRIPT_ 文件中) → `06-MONITORING/scripts/`
- `heartbeat-check.ps1` → `06-MONITORING/scripts/`
- `heartbeat-exec.ps1` → `06-MONITORING/scripts/`
- `heartbeat-done.ps1` → `06-MONITORING/scripts/`

---

### 07-DATA/ (数据处理)
**用途:** API、数据湖、数据处理

```
07-DATA/
├── api/                      # API 相关
├── api-server/               # API 服务器
├── data-lake/                # 数据湖
├── materials/                # 材料数据
└── README.md
```

**移动文件:**
- `api/` → `07-DATA/`
- `api-server/` → `07-DATA/`
- `data-lake/` → `07-DATA/`
- `materials/` → `07-DATA/`
- `domain_data_collector.py` → `07-DATA/` (23KB)
- `test_jina.py` → `07-DATA/api/`
- `test_rss.py` → `07-DATA/api/`

---

### 08-AUTOMATION/ (自动化脚本)
**用途:** 自动化任务、定时任务、GitHub 同步

```
08-AUTOMATION/
├── auto-pnote/               # 自动 P-Note
├── github-sync/              # GitHub 同步
├── scheduled-tasks/          # 定时任务
├── scripts/                  # 自动化脚本
└── README.md
```

**移动文件:**
- `auto-pnote/` → `08-AUTOMATION/`
- `auto-pnote.ps1` → `08-AUTOMATION/auto-pnote/`
- `github-repo-reorganize.py` → `08-AUTOMATION/github-sync/` (10KB)
- `github-repo-reorganize-phase2.py` → `08-AUTOMATION/github-sync/`
- `github-repo-reorganize-phase3.py` → `08-AUTOMATION/github-sync/`
- `github-repo-reorganize-phase4.py` → `08-AUTOMATION/github-sync/`
- `setup-scheduled-task.py` → `08-AUTOMATION/scheduled-tasks/`
- `setup-daily-brief-task.ps1` → `08-AUTOMATION/scheduled-tasks/`
- `setup-domain-cron.ps1` → `08-AUTOMATION/scheduled-tasks/`
- `setup-arxiv-orchestrator-task.ps1` → `08-AUTOMATION/scheduled-tasks/`
- `feishu-ui-sync-cron.json` → `08-AUTOMATION/scheduled-tasks/`
- `lig-auto-update.ps1` → `08-AUTOMATION/scripts/`
- `organize_workspace.py` → `08-AUTOMATION/scripts/` (9KB)
- `organize-reports-folder.py` → `08-AUTOMATION/scripts/`

---

### 09-TESTS/ (测试相关)
**用途:** 测试脚本、测试套件

```
09-TESTS/
├── testing/                  # 测试核心
├── test-suites/              # 测试套件
└── README.md
```

**移动文件:**
- `testing/` → `09-TESTS/`
- `test_pdf_extractor.py` → `09-TESTS/`
- `test_results.json` → `09-TESTS/`
- `test_suite.py` → `09-TESTS/`
- `benchmark.py` → `09-TESTS/`
- `check_classical_ratio.py` → `09-TESTS/`
- `check_recent.py` → `09-TESTS/`
- `check_recent_papers.py` → `09-TESTS/`
- `run-acceptance-test.ps1` → `09-TESTS/`

---

### 10-DOMAIN-RANKING/ (学科学术段位)
**用途:** 领域段位评估系统

```
10-DOMAIN-RANKING/
├── core/                     # 核心脚本
│   ├── domain_ranker_v2.py   (24KB, 主脚本)
│   ├── domain_ranker.py      (10KB)
│   └── domain_data_collector.py
├── reports/                  # 报告
│   └── domain_ranking_report.py
├── scripts/                  # 辅助脚本
└── README.md
```

**移动文件:**
- `domain_ranker_v2.py` → `10-DOMAIN-RANKING/core/` (24KB)
- `domain_ranker.py` → `10-DOMAIN-RANKING/core/` (10KB)
- `domain_ranking_report.py` → `10-DOMAIN-RANKING/reports/` (11KB)
- `domain_data_collector.py` → `10-DOMAIN-RANKING/core/` (23KB)
- `setup-domain-cron.ps1` → `10-DOMAIN-RANKING/scripts/`

---

### 11-NOVEL-WRITING/ (小说创作)
**用途:** 小说章节扩展、AI 率检测、字数统计

```
11-NOVEL-WRITING/
├── chapters/                 # 章节扩展
│   ├── expand_chapter*.py    (21 个脚本)
│   └── manage_chapters.py
├── analysis/                 # 分析工具
│   ├── detect_ai_style.py    (11KB)
│   ├── check_word_count.py   (5KB)
│   ├── optimize_ai_rate.py
│   └── track_writing_progress.py
├── foreshadowing/            # 伏笔追踪
│   └── track_foreshadowing.py
└── README.md
```

**移动文件:**
- `expand_chapter*.py` (21 个) → `11-NOVEL-WRITING/chapters/`
- `expand_chapters.py` → `11-NOVEL-WRITING/chapters/`
- `expand_chapters_5_6.py` → `11-NOVEL-WRITING/chapters/`
- `manage_chapters.py` → `11-NOVEL-WRITING/chapters/` (5KB)
- `detect_ai_style.py` → `11-NOVEL-WRITING/analysis/` (11KB)
- `check_word_count.py` → `11-NOVEL-WRITING/analysis/` (5KB)
- `optimize_ai_rate.py` → `11-NOVEL-WRITING/analysis/`
- `optimize_chapter3.py` → `11-NOVEL-WRITING/chapters/`
- `optimize_chapter7.py` → `11-NOVEL-WRITING/chapters/`
- `deep_optimize_chapter4.py` → `11-NOVEL-WRITING/chapters/`
- `enhance_chapters_2_3.py` → `11-NOVEL-WRITING/chapters/`
- `track_writing_progress.py` → `11-NOVEL-WRITING/analysis/` (4KB)
- `track_foreshadowing.py` → `11-NOVEL-WRITING/foreshadowing/` (7KB)
- `read_chapter.py` → `11-NOVEL-WRITING/`
- `fix_chapter5_count.py` → `11-NOVEL-WRITING/chapters/`

---

### 12-KNOWLEDGE-MANAGEMENT/ (知识管理)
**用途:** 知识卡片重命名、整理

```
12-KNOWLEDGE-MANAGEMENT/
├── rename/                   # 重命名脚本
│   ├── rename-knowledge-cards.py
│   └── rename-knowledge-cards-v2.py
└── README.md
```

**移动文件:**
- `rename-knowledge-cards.py` → `12-KNOWLEDGE-MANAGEMENT/rename/`
- `rename-knowledge-cards-v2.py` → `12-KNOWLEDGE-MANAGEMENT/rename/`

---

### 13-SECURITY/ (安全加固)
**用途:** 安全审计、加固脚本

```
13-SECURITY/
├── scripts/                  # 安全脚本
│   ├── security_hardening.py
│   └── SCRIPT_Health_Check_v1.0.ps1
└── README.md
```

**移动文件:**
- `security_hardening.py` → `13-SECURITY/scripts/` (6KB)
- `SCRIPT_Health_Check_v1.0.ps1` → `13-SECURITY/scripts/`
- `SCRIPT_Nightly_SecurityAudit_v1.0.ps1` → `13-SECURITY/scripts/`
- `SCRIPT_Run_AllAudit_v1.0.ps1` → `13-SECURITY/scripts/`
- `check-quality.sh` → `13-SECURITY/scripts/`

---

### 14-PLUGIN/ (插件系统)
**用途:** 插件市场、技能集成

```
14-PLUGIN/
├── marketplace/              # 插件市场
│   └── plugin_marketplace.py
└── README.md
```

**移动文件:**
- `plugin_marketplace.py` → `14-PLUGIN/marketplace/` (5KB)
- `install-blogwatcher.bat` → `14-PLUGIN/`
- `install-summarize.bat` → `14-PLUGIN/`
- `SCRIPT_Install_Blogwatcher_v1.0.ps1` → `14-PLUGIN/`
- `SCRIPT_Install_Tools_v1.0.ps1` → `14-PLUGIN/`

---

### 15-COGNITIVE-SYSTEM/ (认知系统)
**用途:** 认知系统调试、导出

```
15-COGNITIVE-SYSTEM/
├── debug/                    # 调试工具
│   ├── dump_cognitive.py
│   ├── read_cognitive_system.py
│   └── cognitive_system_dump.json
└── README.md
```

**移动文件:**
- `dump_cognitive.py` → `15-COGNITIVE-SYSTEM/debug/`
- `read_cognitive_system.py` → `15-COGNITIVE-SYSTEM/debug/`
- `cognitive_system_dump.json` → `15-COGNITIVE-SYSTEM/debug/`

---

### 99-ARCHIVE/ (归档)
**用途:** 废弃/实验性代码

```
99-ARCHIVE/
├── level-0/                  # 初始版本
├── early_exit_framework/     # 早期退出框架
├── feedback/                 # 反馈系统
├── intent-belief-integration/# 意图 - 信念集成
└── README.md
```

**移动文件:**
- `level-0/` → `99-ARCHIVE/`
- `early_exit_framework/` → `99-ARCHIVE/`
- `feedback/` → `99-ARCHIVE/`
- `intent-belief-integration/` → `99-ARCHIVE/`

---

## 📋 执行脚本

### PowerShell 重组脚本

```powershell
# reorganize-30-scripts.ps1
$ErrorActionPreference = "Stop"
$src = "D:\OpenClaw\workspace\30-scripts"
$dst = "D:\OpenClaw\workspace\30-scripts"

Write-Host "🚀 开始重组 30-scripts..." -ForegroundColor Green

# 创建目录结构
$dirs = @(
    "00-UTILS", "01-KNOWLEDGE-CARDS", "02-DAILY-BRIEF", "03-LIG-KNOWLEDGE-GRAPH",
    "04-COLLECTORS", "05-AI-RESEARCH", "06-MONITORING", "07-DATA",
    "08-AUTOMATION", "09-TESTS", "10-DOMAIN-RANKING", "11-NOVEL-WRITING",
    "12-KNOWLEDGE-MANAGEMENT", "13-SECURITY", "14-PLUGIN", "15-COGNITIVE-SYSTEM",
    "99-ARCHIVE"
)

foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Force -Path (Join-Path $dst $dir) | Out-Null
    Write-Host "  ✅ 创建：$dir" -ForegroundColor Gray
}

# 移动文件 (示例：知识卡片项目)
Write-Host "`n📦 移动知识卡片项目..." -ForegroundColor Cyan
Move-Item -Path (Join-Path $src "knowledge-card-generator.py") -Destination (Join-Path $dst "01-KNOWLEDGE-CARDS/core/") -Force
Move-Item -Path (Join-Path $src "knowledge-card-webui.py") -Destination (Join-Path $dst "01-KNOWLEDGE-CARDS/core/") -Force
Move-Item -Path (Join-Path $src "knowledge-card-generator") -Destination (Join-Path $dst "01-KNOWLEDGE-CARDS/docs/") -Force
Move-Item -Path (Join-Path $src "pdf-extractor") -Destination (Join-Path $dst "01-KNOWLEDGE-CARDS/pdf/") -Force
Move-Item -Path (Join-Path $src "figure-enhancer") -Destination (Join-Path $dst "01-KNOWLEDGE-CARDS/figures/") -Force

# ... (继续其他项目)

Write-Host "`n✅ 重组完成!" -ForegroundColor Green
```

---

## ✅ 验收清单

### 结构验证
- [ ] 所有 17 个主目录创建完成
- [ ] 所有子目录结构正确
- [ ] 无文件遗漏在根目录

### 功能验证
- [ ] `knowledge-card-generator.py` 正常运行
- [ ] `knowledge-card-webui.py` 正常启动
- [ ] `daily-brief.py` 正常运行
- [ ] `domain_ranker_v2.py` 正常运行
- [ ] 所有定时任务正常执行

### 文档验证
- [ ] 每个项目 README.md 创建完成
- [ ] 所有路径引用更新完成
- [ ] Git 提交并推送

---

## 📊 重组后效果

### 查找效率对比
| 任务 | 重组前 | 重组后 | 提升 |
|------|--------|--------|------|
| 找知识卡片相关 | 3 个文件夹 | 1 个项目 | 3x |
| 找小说创作脚本 | 散落 21 个文件 | 1 个项目 | 5x |
| 找 LIG 图谱工具 | 散落 30+ 文件 | 1 个项目 | 6x |
| 找定时任务配置 | 散落各处 | 08-AUTOMATION/ | 4x |

### 项目管理
- ✅ 项目边界清晰
- ✅ 易于删除/归档整个项目
- ✅ 新成员易于理解
- ✅ 权限管理简化

---

*由 Claw 创建 | 2026-03-11 18:52 | 版本 v2.0*
