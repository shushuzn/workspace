# 30-scripts 快速查找指南

**版本:** v1.0 (2026-03-11)  
**用途:** 5 秒内找到需要的脚本

---

## 🚀 快速查找表

### 按功能查找

| 我要... | 去这里 | 关键文件 |
|---------|--------|----------|
| 📄 生成知识卡片 | `01-KNOWLEDGE-CARDS/core/` | `knowledge-card-generator.py` |
| 🌐 启动 Web UI | `01-KNOWLEDGE-CARDS/core/` | `knowledge-card-webui.py` |
| 📰 生成每日简报 | `02-DAILY-BRIEF/core/` | `daily-brief.py` |
| 📊 查看 LIG 图谱 | `03-LIG-KNOWLEDGE-GRAPH/html/` | `LIG-Knowledge-Graph.html` |
| 🤖 AI 论文分析 | `05-AI-RESEARCH/` | `batch-processor-*.py` |
| 📈 领域段位评估 | `10-DOMAIN-RANKING/core/` | `domain_ranker_v2.py` |
| ✍️ 小说章节扩展 | `11-NOVEL-WRITING/chapters/` | `expand_chapter*.py` |
| 🔒 安全审计 | `13-SECURITY/scripts/` | `SCRIPT_*SecurityAudit*.ps1` |
| 📦 数据收集 | `04-COLLECTORS/` | `*-collector.py` |
| 🧪 运行测试 | `09-TESTS/` | `test_*.py` |

### 按项目查找

```
30-scripts/
├── 00-UTILS/                    # 🔧 通用工具
├── 01-KNOWLEDGE-CARDS/          # 📚 知识卡片 (PDF→HTML)
├── 02-DAILY-BRIEF/              # 📰 每日简报
├── 03-LIG-KNOWLEDGE-GRAPH/      # 🔬 LIG 知识图谱
├── 04-COLLECTORS/               # 📥 数据收集 (arXiv/Medium/Reddit)
├── 05-AI-RESEARCH/              # 🤖 AI 研究工具
├── 06-MONITORING/               # 📊 监控工具
├── 07-DATA/                     # 💾 数据处理
├── 08-AUTOMATION/               # ⚙️ 自动化脚本
├── 09-TESTS/                    # 🧪 测试
├── 10-DOMAIN-RANKING/           # 🏆 学科学术段位
├── 11-NOVEL-WRITING/            # ✍️ 小说创作
├── 12-KNOWLEDGE-MANAGEMENT/     # 🗂️ 知识管理
├── 13-SECURITY/                 # 🔒 安全加固
├── 14-PLUGIN/                   # 🔌 插件系统
├── 15-COGNITIVE-SYSTEM/         # 🧠 认知系统
└── 99-ARCHIVE/                  # 📦 归档代码
```

---

## 🔍 常用命令速查

### 知识卡片
```bash
# 生成卡片
py 01-KNOWLEDGE-CARDS/core/knowledge-card-generator.py paper.pdf --validate

# 启动 Web UI
py 01-KNOWLEDGE-CARDS/core/knowledge-card-webui.py --port 5000
```

### 每日简报
```bash
# 生成简报
py 02-DAILY-BRIEF/core/daily-brief.py --date today --send
```

### 领域评估
```bash
# 评估 LIG 领域
py 10-DOMAIN-RANKING/core/domain_ranker_v2.py --evaluate LIG

# 比较所有领域
py 10-DOMAIN-RANKING/core/domain_ranker_v2.py --compare
```

### 小说创作
```bash
# AI 率检测
py 11-NOVEL-WRITING/analysis/detect_ai_style.py

# 字数统计
py 11-NOVEL-WRITING/analysis/check_word_count.py
```

---

## 📋 定时任务清单

| 任务名 | 频率 | 脚本路径 |
|--------|------|----------|
| DailyBrief-Feishu | 每日 7AM | `02-DAILY-BRIEF/core/daily-brief.py` |
| nightly-security-audit | 每日 2AM | `13-SECURITY/scripts/SCRIPT_Nightly_SecurityAudit_v1.0.ps1` |
| OpenClaw-Arxiv-Collect | 每日 4AM | `npm-global/.../arxiv-daily.py` |

---

## 🔗 相关文档

- **项目 README:** 每个项目目录下有 `README.md`
- **定时任务报告:** `08-AUTOMATION/scheduled-tasks/TASK-PATH-UPDATE-REPORT.md`
- **重组报告:** `08-AUTOMATION/REORGANIZATION-COMPLETE.md`

---

*最后更新：2026-03-11 | 版本 v1.0*
